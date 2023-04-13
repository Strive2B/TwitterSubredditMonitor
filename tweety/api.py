from email.mime import image
from pprint import pprint
import asyncio
import os
from tweety.headers import Headers
import aiohttp
from .logger import logger
import typing
from typing import *
from tweety import types, exceptions
from .models.user import User, ConnectedUser
from .payloads import Payloads, URLVars
from .enums import *
from .models.tweet import Tweet
from .models.space import Space
from .captcha import Solver
from retry import retry
from . import utils, filters
import re


class Client:
    def __init__(self, *, email: str = None,
                 password: str = None,
                 username: str = None,
                 phone: str = None,
                 proxy: str = None,
                 captcha_api_key: str = None):
        self._email = self._check_empty_or_none(email)
        self._username = self._check_empty_or_none(username)
        self._phone = self._check_empty_or_none(phone)
        self._password = password
        self._proxy = proxy
        if captcha_api_key is not None and captcha_api_key != "":
            self._2captcha = Solver(
                captcha_api_key, Statics.RECAPTCHA_SITE_KEY)
        else:
            self._2captcha = None
        self._base_url = 'https://twitter.com'
        self._mobile_url = "https://mobile.twitter.com"
        self._usernames_map = dict()
        self._unavailable_types = ["UserUnavailable"]
        self._payloads = Payloads()
        self._session: aiohttp.ClientSession = None
        self._url_vars = URLVars()
        self.logged_in = False
        self.user = None
        self.extra_info = {}

    def _check_empty_or_none(self, ent: str):
        if ent == "" or ent is None:
            return None
        return ent

    async def async_init(self) -> "Client":
        """Call this method once to complete the init"""
        self.loop = asyncio.get_event_loop()
        self._session = aiohttp.ClientSession()
        self._header_dir = './sessions'
        os.makedirs(self._header_dir, exist_ok=True)
        self._session_id = self._username or self._email
        self._session_file = f"{self._header_dir}/{self._session_id}"
        self._headers = await Headers(self._session).load()
        await self._load_session()
        if await self.is_logged_in():
            self.logged_in = True
        return self

    @property
    def presentable(self):
        if self._username:
            return self._username
        if self._email:
            return self._email
        if self._phone:
            return self._phone

    async def close(self):
        if self._session is not None:
            if not self._session.closed:
                return await self._session.close()

    async def _save_session(self):
        """Saves the headers after every successull request."""
        ...
        # print(self._session._cookie_jar)
        t = self.loop.run_in_executor(None,
                                      lambda: self._session._cookie_jar.save(self._session_file))
        while not t.done():
            await asyncio.sleep(0.1)
        # self._session._cookie_jar.save(self._session_file)

    @staticmethod
    def cookies_dict(cookies: str):
        cookies_list = cookies.split(';')
        cookies = {}
        for cookie in cookies_list:
            try:
                name = cookie.split("=")[0].strip()
                value = cookie.split("=")[1].strip()
            except:
                continue
            cookies[name] = value

        return cookies

    async def do_manual_load(self, cookies: str, csrf: str) -> "Client":
        self._session = aiohttp.ClientSession()
        self._session._cookie_jar.update_cookies(self.cookies_dict(cookies))
        self._header_dir = './sessions'
        os.makedirs(self._header_dir, exist_ok=True)
        session_id = self._email or self._username
        self._session_file = f"{self._header_dir}/{session_id}"
        self._headers = await Headers(self._session).load(csrf)
        headers = await self._headers.manual_load(csrf, cookies)
        # return print(headers)
        variables = self._url_vars.get_me()
        path = f"/i/api/1.1/account/settings.json?{variables}"
        res = await self._request(path, headers, method="GET")
        # print(await res.text())
        me = await res.json()
        headers = self._headers.logged_in()
        user = await self.resolve_screen_name(me["screen_name"])
        self.user = ConnectedUser(user.data)
        self.logged_in = True
        return self

    async def _load_session(self):
        if not os.path.exists(self._session_file):
            return logger.debug("No session file.")
        try:
            # self._session._cookie_jar.load(self._session_file)
            t = self.loop.run_in_executor(
                None, lambda: self._session._cookie_jar.load(self._session_file))
            while not t.done():
                await asyncio.sleep(1)
            await self._filter_csrf_token()
            logger.debug("Session loaded.")
        except FileNotFoundError:
            return logger.debug(f"{self._session_file} does not exist")

    async def _filter_csrf_token(self):
        ...
        cookies = self._session.cookie_jar
        for cookie in cookies:
            cookie_value = str(cookie).split('Set-Cookie:')[-1].strip()
            if cookie_value.startswith("ct0="):
                self._headers.csrf_token = cookie_value.split(
                    ";")[0].strip().replace("ct0=", "").strip()

    @retry((aiohttp.ServerDisconnectedError,
            aiohttp.ServerTimeoutError,
            aiohttp.ClientProxyConnectionError,
            aiohttp.ServerConnectionError,
            aiohttp.ClientHttpProxyError,
            aiohttp.ClientConnectorError), tries=3, delay=3)
    async def _request(self, path, headers: dict = None,
                       payload={},
                       method="GET",
                       proxy: str = None,
                       use_mobile_url=False,
                       base_url=None) -> aiohttp.ClientResponse:
        """Make requests using this function"""

        if base_url is None:
            if use_mobile_url:
                url = f"{self._mobile_url}{path}"
            else:
                url = f'{self._base_url}{path}'
        else:
            url = f"{base_url}{path}"

        proxy = proxy or self._proxy
        async with self._session.request(method=method,
                                         url=url,
                                         headers=headers,
                                         data=payload,
                                         proxy=proxy,
                                         verify_ssl=False) as resp:
            await resp.read()
            await self._filter_csrf_token()
            await self._save_session()
            # print(resp)
            if resp.status in [200]:
                # print(await resp.json())
                return resp

            if resp.status == 429:
                # Rate limit
                js = await resp.json()
                try:
                    message = js.get("errors", [])[0]["message"]
                except (IndexError, KeyError):
                    message = "Debug for error details"
                raise exceptions.RateLimitError(message, resp.status)

            if resp.status in [503]:
                raise exceptions.ServiceUnavailable(await resp.text(), resp.status)

            # logger.debug(resp.reason)
            # logger.debug(await resp.text())

            if resp.status == 403:
                # Trying to do something that is forbidden
                try:
                    js = await resp.json()
                except aiohttp.ContentTypeError:
                    raise exceptions.Forbidden(await resp.text(), resp.status)
                if js["errors"][0]["code"] == 349:
                    # Trying to send the DM to person who does not receive DMs.
                    raise exceptions.CannotSendDM(await resp.text(), resp.status)
                raise exceptions.Forbidden(await resp.text(), resp.status)

            raise exceptions.TweetyException(await resp.text(), resp.status)

    async def is_logged_in(self) -> bool:
        path = "/i/api/2/badge_count/badge_count.json?supports_ntab_urt=1"
        try:
            headers = self._headers.basic()
            response = await self._request(path, headers)
            await self.get_me()
            logger.debug(f"Logged-in as {self.user}")
        except Exception as e:
            return logger.debug("User not logged in already")
        return response.status == 200

    async def get_me(self) -> ConnectedUser:
        ...
        variables = self._url_vars.get_me()
        path = f"/i/api/1.1/account/settings.json?{variables}"
        headers = self._headers.basic()
        res = await self._request(path, headers, method="GET")
        # print(await res.text())
        me = await res.json()
        user = await self.resolve_screen_name(me["screen_name"])
        self.user = ConnectedUser(user.data)
        self.logged_in = True
        return self.user

    async def login(self, step_delay=0.5):
        """
        Login to twitter using the creds provided
        raises 
            InvalidUsername
            InvalidPassword
            InvalidEmail
            InvalidPhone
        """
        if self.logged_in:
            return logger.info(f"User already logged in")

        next_step = LoginSteps.START_LOGIN_FLOW
        while True:
            if next_step == LoginSteps.START_LOGIN_FLOW:
                logger.debug("Starting login flow")
                r = await self.get_login_flow_token()
                data = await r.json()
                next_step = self.filter_next_step(data)
                self.flow_token = data["flow_token"]
                # next_step = LoginSteps.START_REF_FLOW
                logger.debug(f"Got initial flow token {self.flow_token}")
                await asyncio.sleep(step_delay)
                continue

            # if next_step == LoginSteps.LOGIN_INSTRUMENTION:
            #     continue

            if next_step == LoginSteps.LOGIN_INSTRUMENTION:
                logger.debug("Starting ref flow ")
                r = await self.send_ref()
                data = await r.json()
                # pprint(data)
                next_step = self.filter_next_step(data)
                self.flow_token = data["flow_token"]
                logger.debug(f"Got ref flow token {self.flow_token}")
                # print(next_step)
                if self._username:
                    next_step = LoginSteps.ENTER_USERNAME
                elif self._email:
                    next_step = LoginSteps.ENTER_EMAIL
                await asyncio.sleep(step_delay)
                continue

            if next_step == LoginSteps.ENTER_EMAIL or next_step == LoginSteps.ENTER_USERNAME:
                logger.debug("Entering username/email")
                if next_step == LoginSteps.ENTER_EMAIL:
                    identity = self._email
                elif next_step == LoginSteps.ENTER_USERNAME:
                    identity = self._username
                r = await self.send_id(identity)
                data = await r.json()
                self.flow_token = data["flow_token"]
                logger.debug(f"Got id flow token {self.flow_token}")
                next_step = self.filter_next_step(data)
                await asyncio.sleep(step_delay)
                continue

            if next_step == LoginSteps.ENTER_PHONE_NUMBER:
                raise exceptions.LoginFailed(
                    "Need to enter the phone number. Not implemented yet.")

            if next_step == LoginSteps.ALTERNATIVE_ID_USERNAME:
                ...
                logger.debug("Need to submit an alternate id to login.")
                headers = await self._headers.login_flow()
                payload = await self._payloads.send_alt_id(self.flow_token, self._username)
                path = "/i/api/1.1/onboarding/task.json"
                try:
                    r = await self._request(path, headers, payload, method="POST")
                except exceptions.TweetyException as e:
                    raise exceptions.InvalidUsername(await r.text(), r.status) from e
                logger.debug("Username sent")
                data = await r.json()
                self.flow_token = data["flow_token"]
                next_step = self.filter_next_step(data)
                await asyncio.sleep(step_delay)
                continue

            if next_step == LoginSteps.ALTERNATIVE_ID_PHONE:
                raise exceptions.LoginFailed(
                    f"Twitter requires phone for login and we can't do that yet.")

            if next_step == LoginSteps.ENTER_PASSWORD:
                r = await self.send_password()
                data = await r.json()
                self.flow_token = data["flow_token"]
                next_step = self.filter_next_step(data)
                continue

            if next_step == LoginSteps.ACCOUNT_DUPLICATION_CHECK:
                logger.debug(f"Confirming the duplication check ..")
                path = "/i/api/1.1/onboarding/task.json"
                headers = await self._headers.login_flow()
                payload = await self._payloads.send_duplicate_account_check(self.flow_token)
                r = await self._request(path, headers, payload, method="POST")
                data = await r.json()
                self.flow_token = data["flow_token"]
                next_step = self.filter_next_step(data)
                continue

            if next_step == LoginSteps.LOGIN_COMPLETE:
                vars = self._url_vars.viewer_vars()
                path = f"/i/api/graphql/O_C5Q6xAVNOmeolcXjKqYw/Viewer?variables={vars}"
                headers = await self._headers.login_flow()
                await self._request(path, headers)
                await self.get_me()
                self.logged_in = True
                return logger.debug("Login success!")

            if next_step == LoginSteps.RECAPTCHA_REQUIRED_1:
                logger.debug("ReCaptcha required. Solving..")
                path = "/i/api/1.1/onboarding/task.json"
                if self._2captcha:
                    code = await self._2captcha.get_recaptcha_code(Statics.RECAPTCHA_SITE_KEY)
                else:
                    message = "Twitter requested captcha and captcha not solved. API key not available."
                    raise exceptions.MissingCaptchaAPIKey(message, r.status)
                payload = await self._payloads.login_recaptcha(self.flow_token, code)
                header = await self._headers.login_flow()
                r = await self._request(path, headers=header, payload=payload, method="POST")
                logger.debug("Recaptcha solved.")
                data = await r.json()
                self.flow_token = data["flow_token"]
                next_step = self.filter_next_step(data)
                continue

            if next_step == LoginSteps.LOGIN_ACID_PHONE or next_step == LoginSteps.LOGIN_ACID_EMAIL:
                # Need to enter the phone number.
                logger.debug(
                    f"Login Acid is required to complete the login.")
                path = "/i/api/1.1/onboarding/task.json"
                if next_step == LoginSteps.LOGIN_ACID_EMAIL:
                    if self._email is None:
                        raise exceptions.LoginFailed(
                            "Email is needed to login but not available", status=404)
                    acid = self._email
                    logger.debug("Using email as login acid")
                elif next_step == LoginSteps.LOGIN_ACID_PHONE:
                    if self._phone is None:
                        raise exceptions.LoginFailed(
                            "Phone number is needed to login but not available", status=404)
                    acid = self._phone
                    logger.debug("Using phone as login acid")
                payload = await self._payloads.login_acid(
                    self.flow_token, acid)
                headers = await self._headers.login_flow()
                r = await self._request(path, headers=headers, payload=payload, method="POST")
                logger.debug(f"{acid} sent as login acid.")
                data = await r.json()
                self.flow_token = data["flow_token"]
                next_step = self.filter_next_step(data)
                continue

            if next_step == LoginSteps.LOGIN_DISABLED:
                raise exceptions.LoginDisabled(
                    "Login is temprarily disabled.", status=403)

            return logger.debug(f"Unknown next step {next_step}")

    def filter_next_step(self, data: dict):
        # pprint(data)
        try:
            for task in data["subtasks"]:
                if task["subtask_id"] == LoginSteps.ALTERNATIVE_ID:
                    # We need to enter the username/phone here.
                    if "username" in task["enter_text"]["primary_text"]["text"]:
                        # We can enter username.
                        return LoginSteps.ALTERNATIVE_ID_USERNAME
                    elif "phone" in task["enter_text"]["primary_text"]["text"]:
                        # We need to enter the phone number
                        ...
                        return LoginSteps.ALTERNATIVE_ID_PHONE
                    else:
                        return logger.debug(f"twitter requested some unknown task {task}")

                elif task["subtask_id"] == LoginSteps.ACCOUNT_DUPLICATION_CHECK:
                    return LoginSteps.ACCOUNT_DUPLICATION_CHECK

                elif task["subtask_id"] == LoginSteps.ENTER_PASSWORD:
                    return LoginSteps.ENTER_PASSWORD

                elif task["subtask_id"] == LoginSteps.LOGIN_ACID:
                    # print("Found login acid")
                    secondary_text = task["enter_text"]["header"]["secondary_text"]["text"]
                    # print(secondary_text)
                    if "@" in secondary_text.lower():

                        if "confirmation code" in secondary_text.lower():
                            raise exceptions.EmailVerificationCodeRequired(
                                "Email verification code is needed to complete login.", status=404)

                        return LoginSteps.LOGIN_ACID_EMAIL

                    elif "phone" in secondary_text.lower():

                        if "confirmation code" in secondary_text.lower():

                            raise exceptions.PhoneVerificationCodeRequired(
                                "Phone verification code is needed to complete login.", status=404)

                        return LoginSteps.LOGIN_ACID_PHONE
                    else:
                        return secondary_text

                elif task["subtask_id"] == LoginSteps.LOGIN_COMPLETE:
                    return LoginSteps.LOGIN_COMPLETE

                elif task["subtask_id"] == LoginSteps.RECAPTCHA_REQUIRED_1 or task["subtask_id"] == LoginSteps.RECAPTCHA_REQUIRED_2:
                    return LoginSteps.RECAPTCHA_REQUIRED_1

                elif task["subtask_id"] == LoginSteps.LOGIN_INSTRUMENTION:
                    return LoginSteps.LOGIN_INSTRUMENTION

            if len(data.get("subtasks")) > 0:
                return data.get("subtasks")[0].get("subtask_id", None)

        except KeyError:
            return

    async def get_login_flow_token(self):
        path = "/i/api/1.1/onboarding/task.json?flow_name=login"
        headers = await self._headers.login_flow()
        payload = await self._payloads.login_flow_start()
        return await self._request(path, headers, payload=payload, method="POST")

    async def send_ref(self):
        path = "/i/api/1.1/onboarding/task.json"
        headers = await self._headers.login_flow()
        payload = await self._payloads.send_ref_payload(self.flow_token)
        return await self._request(path, headers, payload, "POST")

    async def send_id(self, identity: str):
        path = "/i/api/1.1/onboarding/task.json"
        payload = await self._payloads.send_email(identity, self.flow_token)
        # print(payload)
        headers = await self._headers.login_flow()
        return await self._request(path, headers, payload, "POST")

    async def send_password(self):
        path = "/i/api/1.1/onboarding/task.json"
        payload = await self._payloads.send_password(self._password, self.flow_token)
        headers = await self._headers.login_flow()
        return await self._request(path, headers, payload, "POST")

    async def send_phone_number(self):
        pass

    """
    Other operations are handled below.
    """

    async def resolve_screen_name(self, screen_name: str) -> User:
        """ Resolve a twitter username to get info """
        if screen_name is None:
            raise exceptions.UserNotFound(
                f"{screen_name} not found", status=404)

        if screen_name in self._usernames_map.keys():
            return self._usernames_map[screen_name]
        vars = self._url_vars.encode_screen_name_vars(screen_name)
        path = f'/i/api/graphql/B-dCk4ph5BZ0UReWK590tw/UserByScreenName?variables={vars}'
        headers = self._headers.basic()
        response = await self._request(path, headers=headers)
        res = await response.json()
        try:
            if res["data"] == {}:
                raise exceptions.UserNotFound(
                    f"{screen_name} not found", status=404)

        except KeyError:
            logger.debug(res)
            raise

        try:
            data = res["data"]["user"]["result"]
            user = User(data)
            self._usernames_map[screen_name] = user
            return user

        except KeyError:
            return logger.debug(res)

    async def get_follows_chunk(self, follows_type: str,
                                user_rest_id: str = None,
                                screen_name: str = None,
                                chunk_size: int = 4900,
                                cursor: str = "-1"):
        '''
        user_rest_id : the rest_id of the user
        chunk_size : the number of user that will be retrieved in 1 request
        cursor : the cursor
        '''
        if not user_rest_id and not screen_name:
            ValueError("Missing username/rest_id")

        previous_cursor = cursor
        if user_rest_id is None:
            user_info = await self.resolve_screen_name(screen_name)
            user_rest_id = user_info.rest_id

        vars = self._url_vars.encode_follows_vars(
            user_id=user_rest_id, count=chunk_size, cursor=cursor)
        if follows_type == types.FOLLOWINGS:
            path = f'/i/api/graphql/A6M2PaHNiqpufPSg41x3xw/Following?variables={vars}'
        elif follows_type == types.FOLLOWERS:
            path = f'/i/api/graphql/ObxmU9WHnfi4VCdyLldQIA/Followers?variables={vars}'

        headers = self._headers.basic()
        response = await self._request(path, headers=headers)
        res = await response.json()

        if res["data"]["user"]["result"]["__typename"] in self._unavailable_types:
            return

        try:
            timeline = res["data"]["user"]["result"]["timeline"]["timeline"]

        except KeyError as e:

            if res["errors"][0]["code"] == ErrorCodes.OverCapacity:
                logger.warning(f'Over capacity!! Waiting for few seconds')
                await asyncio.sleep(15)
                return await self.get_follows_chunk(follows_type, user_rest_id, chunk_size, cursor)

            else:
                logger.exception(e)
                logger.warning(
                    '\n NOTE : Above exception is unhandled exception\n')

        for item in timeline["instructions"]:
            if item["type"] == "TimelineAddEntries":
                follows = item["entries"][:-2]
                cursor = item["entries"][-2]["content"]["value"]
                break
        logger.debug(f'Got followings in chunk : {len(follows)}')

        filtered_follows_list = list()
        for follow in follows:
            user = follow["content"]["itemContent"]["user_results"]["result"]
            if user["__typename"] in self._unavailable_types:
                continue
            filtered_follows_list.append(user)

        if cursor.startswith("0|"):
            logger.debug(cursor)
            cursor = previous_cursor
        return filtered_follows_list, cursor

    async def follows(self, follows_type: str,
                      user_rest_id: str,
                      chunk_size: int = 4900,
                      cursor: str = "-1",
                      wait_for_new: bool = False,
                      check_time: int = 20,
                      async_lock: typing.Union[asyncio.Lock,
                                               asyncio.Semaphore] = None,
                      wait_between_requests: int = 1,
                      save_cursor: bool = False,
                      wait_on_ratelimit=False,
                      rate_limit_wait_seconds=10):
        '''
        Get followers/follows of a user.
        user_rest_id : the rest_id of the user
        chunk_size : the number of user that will be retrieved in 1 request
        cursor : the cursor
        wait_for_new : When True funcion will monitor the latest cursor for new follows
        check_time : The time between checking for new follows when wait_for_new is True
        async_lock : The async lock / semaphore to prevent the funcion from blowing up twitter API.
        wait_between_requests : Seconds to wait between requests when getting followers from API.
        '''
        def save_cur(cursor):
            with open("cursor.txt", "w") as f:
                f.write(cursor)
        previous_cursor = cursor
        while True:
            vars = self._url_vars.encode_follows_vars(
                user_id=user_rest_id, count=chunk_size, cursor=cursor)
            if follows_type == types.FOLLOWINGS:
                path = f'/i/api/graphql/A6M2PaHNiqpufPSg41x3xw/Following?variables={vars}'
            elif follows_type == types.FOLLOWERS:
                path = f'/i/api/graphql/ObxmU9WHnfi4VCdyLldQIA/Followers?variables={vars}'

            headers = self._headers.basic()
            if async_lock is not None:
                async with async_lock:
                    response = await self._request(path, headers=headers)
                    await asyncio.sleep(wait_between_requests)
            else:
                try:
                    response = await self._request(path, headers=headers)
                except exceptions.TweetyException as e:
                    if e.code == 429 or e.status == 429:
                        # Hitting the rate limit
                        if wait_on_ratelimit:
                            await asyncio.sleep(rate_limit_wait_seconds)
                            continue
                        else:
                            raise e
                await asyncio.sleep(wait_between_requests)

            res = await response.json()
            if res["data"]["user"]["result"]["__typename"] in self._unavailable_types:
                return

            try:
                timeline = res["data"]["user"]["result"]["timeline"]["timeline"]

            except KeyError as e:

                if res["errors"][0]["code"] == ErrorCodes.OverCapacity:
                    logger.warning(f'Over capacity!! Waiting for few seconds')
                    await asyncio.sleep(15)
                    continue

                else:
                    logger.exception(e)
                    logger.warning(
                        '\n NOTE : Above exception is unhandled exception\n')

            for item in timeline["instructions"]:
                if item["type"] == "TimelineAddEntries":
                    follows = item["entries"][:-2]
                    previous_cursor = cursor
                    cursor = item["entries"][-2]["content"]["value"]
                    if save_cursor:
                        print(f"Next Cursor : {cursor}")
                        save_cur(cursor)
                    break
            logger.debug(f'Got followings in chunk : {len(follows)}')

            filtered_follows_list = list()
            for follow in follows:
                user = follow["content"]["itemContent"]["user_results"]["result"]
                if user["__typename"] in self._unavailable_types:
                    continue
                filtered_follows_list.append(user)

            yield [User(data) for data in filtered_follows_list]

            if cursor.startswith("0|"):
                if wait_for_new:
                    logger.debug(cursor)
                    cursor = previous_cursor
                    logger.info(cursor)
                    logger.info(len(filtered_follows_list))
                    await asyncio.sleep(check_time)
                    continue
                logger.debug('No more follows')
                return

    async def get_follows_list(self, follows_type: str,
                               user_rest_id: str,
                               chunk_size: int = 4900,
                               cursor: str = "-1",
                               wait_for_new: bool = False,
                               check_time: int = 20,
                               async_lock: typing.Union[asyncio.Lock,
                                                        asyncio.Semaphore] = None,
                               wait_between_requests: int = 1) -> List[User]:
        follows_list = []
        async for follows in self.follows(follows_type,
                                          user_rest_id=user_rest_id,
                                          chunk_size=chunk_size,
                                          cursor=cursor,
                                          wait_for_new=wait_for_new,
                                          check_time=check_time,
                                          async_lock=async_lock,
                                          wait_between_requests=wait_between_requests):

            follows_list.extend(follows)
        return follows_list

    def _filtered_replies(self, replies):
        pure_replies = list()
        for reply in replies:
            try:
                if reply["content"]["entryType"] == "TimelineTimelineItem":
                    pure_replies.append(Tweet(
                        reply["content"]["itemContent"]["tweet_results"]["result"]))
            except KeyError:
                continue
            if reply["content"]["entryType"] == "TimelineTimelineModule":
                invalid_types = ["TimelineTimelineCursor"]
                for tweet in reply["content"]["items"]:
                    if tweet["item"]["itemContent"]["itemType"] in invalid_types:
                        continue
                    try:
                        pure_replies.append(Tweet(
                            tweet["item"]["itemContent"]["tweet_results"]["result"]
                        ))
                    except KeyError:
                        continue
        return pure_replies

    async def tweet_replies(self, tweet_id: int) -> Generator[List[Tweet], None, None]:
        have_more = True
        cursor = None
        while have_more:
            vars = self._url_vars.encode_tweet_details_vars(
                tweet_id, cursor=cursor)
            path = f'/i/api/graphql/1mwvJFWVNiKbgR6QTIkXgQ/TweetDetail?variables={vars}'
            headers = self._headers.basic()
            response = await self._request(path, headers=headers)
            res = await response.json()
            instructions = res["data"]["threaded_conversation_with_injections"]["instructions"]
            for ins in instructions:
                if ins["type"] == "TimelineAddEntries":
                    replies = ins["entries"]
                    if replies[-1]["entryId"].startswith("cursor"):
                        cursor = replies[-1]["content"]["itemContent"]["value"]
                        have_more = True
                        replies = replies[:-1]
                    else:
                        yield self._filtered_replies(replies)
                        return
            yield self._filtered_replies(replies)

    async def tweet_replies_list(self, tweet_id: int) -> typing.List[Tweet]:
        """Get the list of tweet replies"""
        replies = []
        async for chunk in self.tweet_replies(tweet_id):
            replies.extend(chunk)

        return replies

    async def post_tweet(self, text: str,
                         in_reply_to_tweet_id: str = None,
                         quoted_tweet_id: str = None,
                         proxy: str = None,
                         randomize_user_agent=False,
                         images_locations:Union[str, List[str], None]=None) -> Tweet:
        ...
        """Post a tweet/comment/quote update"""
        if isinstance(images_locations, str):
            images_locations = [images_locations]
        if not isinstance(images_locations, list):
            images_locations = []
        tasks = []
        for m in images_locations:
            tasks.append(asyncio.create_task(self.upload_media(m)))
        media_ids =  await asyncio.gather(*tasks)
        query_id = "4YIaS-f70TM_DmWIEDSFNA"
        path = f"/i/api/graphql/{query_id}/CreateTweet"
        payload = await self._payloads.post_tweet(text, query_id=query_id,
                                                  in_reply_to_tweet_id=in_reply_to_tweet_id,
                                                  quoted_tweet_id=quoted_tweet_id, 
                                                  media_ids=media_ids)
        headers = self._headers.json_content(new_agent=randomize_user_agent)
        r = await self._request(path, method="POST", payload=payload, headers=headers, proxy=proxy)
        if r.status != 200:
            logger.debug(r)
            logger.debug(r.reason)
            return logger.debug(await r.json())
        data = await r.json()
        try:
            result = data["data"]["create_tweet"]["tweet_results"]["result"]
            return Tweet(result)
        except KeyError:
            return await r.json()

    async def retweet(self, tweet_id: str):
        """Retweet a tweet with id."""
        query_id = "ojPdsZsimiJrUGLR1sjUtA"
        path = f"/i/api/graphql/{query_id}/CreateRetweet"
        payload = await self._payloads.retweet(tweet_id, query_id)
        headers = self._headers.logged_in()
        r = await self._request(path, method="POST", payload=payload, headers=headers)
        if r.status != 200:
            logger.debug(r.reason)
            logger.debug(await r.json())
        return await r.json()

    async def favorite_tweet(self, tweet_id: str):
        """Favorite/Like a tweet"""
        query_id = "lI07N6Otwv1PhnEgXILM7A"
        path = f"/i/api/graphql/{query_id}/FavoriteTweet"
        payload = await self._payloads.favorite_tweet(tweet_id, query_id)
        headers = self._headers.logged_in()
        r = await self._request(path, method="POST", payload=payload, headers=headers)
        if r.status != 200:
            logger.debug(r.reason)
            logger.debug(await r.json())
        return await r.json()

    async def tweet_likers(self, tweet_id: int) -> Generator[List[User], None, None]:
        """Get the users list who liked the tweet"""
        headers = self._headers.logged_in()
        new_cursor = None
        while True:
            variables = self._url_vars.tweet_likers(
                tweet_id, cursor=new_cursor)
            path = f"/i/api/graphql/WIWiqzpsdRQNX00z5fmyoA/Favoriters?variables={variables}"
            res = await self._request(path, headers, method="GET")
            js = await res.json()
            try:
                entries = js["data"]["favoriters_timeline"]["timeline"]["instructions"][0]["entries"]
            except (IndexError, KeyError):
                return
            users = []
            for entry in entries:
                try:
                    users.append(User(entry["content"]["itemContent"]
                                      ["user_results"]["result"]))
                except KeyError:
                    if entry["entryId"].startswith("cursor-top"):
                        # This is the cursor to scroll up.
                        back_cusror = entry["content"]["value"]
                    elif entry["entryId"].startswith("cursor-bottom"):
                        next_cusror = entry["content"]["value"]
                except AttributeError:
                    pprint(entry)
            yield users
            if next_cusror == new_cursor:
                return
            new_cursor = next_cusror

    async def tweet_likers_list(self, tweet_id: int) -> List[User]:
        """Get a list of all users who liked a person"""
        likers = []
        async for chunk in self.tweet_likers(tweet_id):
            likers.extend((chunk))
        return likers

    async def retweeters(self, tweet_id: int) -> Generator[List[User], None, None]:
        """Get the retweeters of a tweet"""
        headers = self._headers.basic()
        new_cursor = "-1"
        while True:
            variables = self._url_vars.retweeters(
                tweet_id, cursor=new_cursor, count=1000)
            path = f"/i/api/graphql/V7bDmi20J2EG-Uw2i8sRVQ/Retweeters?variables={variables}"
            res = await self._request(path, headers, method="GET")
            js = await res.json()
            try:
                entries = js["data"]["retweeters_timeline"]['timeline']["instructions"][0]["entries"]
            except (IndexError, KeyError):
                return
            users = []
            for entry in entries:
                # pprint(entry)
                try:
                    users.append(User(entry["content"]["itemContent"]
                                      ["user_results"]["result"]))
                except KeyError:
                    if entry["entryId"].startswith("cursor-top"):
                        # This is the cursor to scroll up.
                        back_cusror = entry["content"]["value"]
                    elif entry["entryId"].startswith("cursor-bottom"):
                        # This is the cursor to get more items
                        next_cusror = entry["content"]["value"]
                except AttributeError:
                    pprint(entry)
            # pprint(users)
            yield users
            if next_cusror == new_cursor:
                return
            new_cursor = next_cusror

    async def retweeters_list(self, tweet_id: int) -> List[User]:
        """Get the list of all the retweeters of a tweet"""
        retweeters = []
        async for chunk in self.retweeters(tweet_id):
            retweeters.extend(chunk)

        return retweeters

    async def hashtag_latest_tweets(self, hashtag: str) -> Generator[List[int], None, None]:
        """Scrape the latest tweets from hashtag"""
        headers = self._headers.basic()
        cursor = None
        while True:
            payload = self._url_vars.latest_from_hashtag(
                hashtag, cursor=cursor, count=100)
            path = f"""/i/api/2/search/adaptive.json?{payload}"""
            res = await self._request(path, headers)
            js = await res.json()
            instructions = js["timeline"]["instructions"]
            entries = None
            for instruction in instructions:
                if "addEntries" in instruction.keys():
                    entries = instruction["addEntries"]["entries"]
                if "replaceEntry" in instruction.keys():
                    if instruction["replaceEntry"]["entryIdToReplace"] == "sq-cursor-top":
                        # This is the refresh cursor
                        refresh_cursor = instruction["replaceEntry"]["entry"]["content"]["operation"]["cursor"]["value"]
                    elif instruction["replaceEntry"]["entryIdToReplace"] == "sq-cursor-bottom":
                        next_cursor = instruction["replaceEntry"]["entry"]["content"]["operation"]["cursor"]["value"]
            entries = js["timeline"]["instructions"][0]["addEntries"]["entries"]
            tweets_ids = []
            for entry in entries:
                if entry["entryId"].startswith("sq-I-t"):
                    tweets_ids.append(
                        entry["content"]["item"]["content"]["tweet"]["id"])
                elif entry["entryId"] == "sq-cursor-top":
                    # The Refresh cursror
                    refresh_cursor = entry["content"]["operation"]["cursor"]["value"]

                elif entry["entryId"] == "sq-cursor-bottom":
                    # The next cursor
                    next_cursor = entry["content"]["operation"]["cursor"]["value"]

            yield tweets_ids
            if next_cursor == cursor:
                logger.debug(f"No more results {next_cursor}")
                return

            cursor = next_cursor
            # break

    async def send_dm(self, message: str, user_id: str = None, screen_name: str = None):
        """Send the DM to the user_id
        """
        if not user_id and not screen_name:
            raise ValueError("Provide screen_name or user_id")
        if screen_name:
            user = await self.resolve_screen_name(screen_name)
            if not user:
                return print("User not found for DM")
            if not user.can_dm:
                raise exceptions.CannotDMUser(
                    "Cannot DM this user", status=403)
            user_id = user.rest_id
        path = "/i/api/1.1/dm/new.json"
        payload = self._url_vars.send_dm(
            message, f"{self.user.rest_id}-{user_id}")
        headers = self._headers.send_dm()
        r = await self._request(path, headers, payload=payload, method="POST")
        if r.status != 200:
            logger.debug(r)
            logger.debug(r.reason)
            logger.debug(await r.json())
        return await r.json()

    async def get_notifications(self):
        """Get the notifications of account"""

    async def fetch_home(self):
        """Fetch home timeline of the user"""
        variables = self._url_vars.get_home_timeline()
        path = f"/i/api/2/timeline/home.json?{variables}"
        headers = self._headers.logged_in()
        r = await self._request(path, headers=headers, method="GET")
        if r.status != 200:
            logger.debug(r.reason)
            logger.debug(await r.json())
        return await r.json()

    async def is_accont_suspended(self) -> bool:
        """Check if the authorized account is suspended"""
        tl = await self.fetch_home()
        tl_entries = tl.get("timeline").get("instructions", [])
        for entry in tl_entries:
            if "pinEntry" in entry.keys():
                header_text = entry.get("pinEntry").get(
                    "entry", {}).get("content", {}).get(
                    "item", {}).get("content", {}).get(
                    "message", {}).get("content", {}).get(
                    "inlinePrompt", {}).get("headerText", "")

                return header_text.lower() == ExpectedTexts.ACCOUNT_SUSPENDED.lower()
        return False

    async def update_profile(self, *, new_name: str = None,
                             new_desc: str = None,
                             new_location: str = None):
        if new_name is None:
            new_name = self.user.name
        if new_desc is None:
            new_desc = self.user.description
        if new_location is None:
            new_location = self.user.location
        path = "/i/api/1.1/account/update_profile.json"
        headers = self._headers.basic()
        payload = self._url_vars.update_profile(
            name=new_name,
            description=new_desc,
            location=new_location)
        r = await self._request(path, headers, payload, method="POST")
        if r.status in range(200, 299):
            self.user.name = new_name
            self.user.description = new_desc
            await self.get_me()
            return await r.json()

        return await r.text()

    async def update_profile_image(self, image_location: str):
        media_id = await self.upload_media(media_path=image_location)
        path = f"/i/api/1.1/account/update_profile_image.json"
        payload = await self._payloads.update_profile_picture(media_id)
        headers = self._headers.basic()
        r = await self._request(path, headers, payload, method="POST")
        if r.status in range(200, 299):
            await self.get_me()
            return await r.json()

        try:
            return await r.json()
        except aiohttp.ContentTypeError:
            return await r.text()

    async def upload_media(self, media_path: str):
        image_ext = media_path.split(".")[-1]
        total_bytes = utils.file_size_bytes(media_path)

        async def __request(path, headers):
            async with self._session.request(method="POST", url=path, headers=headers) as response:
                await response.read()
                return response

        variables = self._url_vars.upload_media_init(total_bytes, image_ext)
        path = f"https://upload.twitter.com/i/media/upload.json?{variables}"
        headers = await self._headers.upload_media_init()
        r = await __request(path, headers)
        r_js = await r.json()
        media_id = r_js["media_id"]
        form = aiohttp.FormData()
        value = open(media_path, "rb").read()
        form.add_field(name="media", value=value, filename="blob",
                       content_type="application/octet-stream")
        variables = self._url_vars.upload_media_append(media_id)
        path = f"https://upload.twitter.com/i/media/upload.json?{variables}"
        async with self._session.request(method="POST", url=path, headers=await self._headers.upload_media_append(), data=form) as resp:
            await resp.read()

        headers = await self._headers.upload_media_final()
        variables = self._url_vars.upload_media_final(media_id)
        path = f"https://upload.twitter.com/i/media/upload.json?{variables}"

        async with self._session.request(method="POST", url=path, headers=headers) as resp:
            await resp.read()
        r_js = await resp.json()

        return media_id

    async def search(self, search_term: str, result_filter=SearchFilter.PEOPLE):
        """Search users on twitter by search term"""

        next_cursor = None
        while True:
            variables = self._url_vars.search(
                search_term, result_filter, count=20, cursor=next_cursor)
            path = f"/i/api/2/search/adaptive.json?{variables}"
            headers = self._headers.basic()
            r = await self._request(path, headers)
            r_js = await r.json()
            users_data = r_js.get("globalObjects").get("users", {})
            users = []
            for user_d in users_data.values():
                users.append(User(user_d))

            def _extract_cursor_next(entries):
                for entry in entries:
                    # print(entry)
                    if entry["entryId"].startswith("sq-cursor-b"):
                        return entry["content"]["operation"]["cursor"]["value"]

            instructions = r_js["timeline"]["instructions"]
            entries = []
            # print(instructions[0])
            for instruction in instructions:
                if "addEntries" in instruction.keys():
                    entries = instruction["addEntries"]["entries"]

            next_cursor = _extract_cursor_next(entries)
            print(next_cursor)

    async def update_username(self, username: str):
        """Update the username"""
        path = "/i/api/1.1/account/settings.json"
        payload = self._url_vars.update_username(username)
        headers = self._headers.basic()
        r = await self._request(path, headers=headers, payload=payload, method="POST")
        if r.status == 200:
            old_user = self.user
            await self.get_me()
            if self._session_id == old_user.username:
                # Need to rename the session file.
                self._session_id = f"{self.user.username}"
                new_session_file = f"{self._header_dir}/{self._session_id}"
                os.rename(self._session_file, new_session_file)
                self._session_file = new_session_file
            return await r.json()
        return await r.text()

    async def _get_user_tweets(self, user_id: int, cursor: str = None):
        variables = await self._url_vars.get_user_tweets(user_id=user_id, cursor=cursor)
        query_id = "kXtgwSN5duK2CTxWXITc8Q"
        path = f"/i/api/graphql/{query_id}/UserTweets?{variables}"
        headers = self._headers.basic()
        r = await self._request(path, headers=headers)
        if r.status == 200:
            r_js = await r.json()
            instructions = r_js.get("data", {}).get("user", {}).get(
                "result", {}).get("timeline_v2", {}).get("timeline", {}).get("instructions", [])
            entries = []
            for instruction in instructions:
                if instruction.get("type", "") == "TimelineAddEntries":
                    entries = instruction["entries"]
            return filters.tweets_from_entries(entries)

    async def get_user_recent_tweets(self, user_id: int) -> List[Tweet]:
        """Get the most recent tweets of the user"""

        tweets, next_cur, prev_cur = await self._get_user_tweets(user_id)
        return tweets

    async def get_all_user_tweets(self, user_id: int):
        cursor = None
        while True:
            tweets, next_cur, prev_cur = await self._get_user_tweets(user_id, cursor=cursor)
            yield tweets
            if cursor == next_cur:
                # No more results
                return
            cursor = next_cur
            await asyncio.sleep(1)

    async def get_space_info(self, space_id: str) -> Space:
        """Get all info about a space"""
        query_id = "X3en8yLOVNToFoCv53D94A"
        path = f"/i/api/graphql/{query_id}/AudioSpaceById"
        headers = self._headers.basic()
        payload = await self._url_vars.get_space_info(space_id)
        r = await self._request(path=path, headers=headers, payload=payload, method="GET")
        r_js = await r.json()
        data = r_js.get("data", {}).get("audioSpace", {})
        return Space(data)

    async def get_space_members_usernames(self, space_id: str) -> List[str]:
        """Get the usernames of space listening members"""
        data = await self.get_space_info(space_id)
        participants = data.get("participants", {})

        def _extract_usernames(items):
            usernames = []
            for item in items:
                usernames.append(item["twitter_screen_name"])
            return usernames
        admins = _extract_usernames(participants.get("admins", []))
        speakers = _extract_usernames(participants.get("speakers", []))
        listeners = _extract_usernames(participants.get("listeners", []))
        to_return = []
        to_return.extend(admins)
        to_return.extend(speakers)
        to_return.extend(listeners)
        return to_return

    async def is_space_live(self, space_id: str) -> bool:
        """Check if the space is live"""
        info = await self.get_space_info(space_id)
        return info["metadata"]["state"] == "Running"

    async def follow_user(self, *,
                          screen_name: str = None,
                          user_id: int = None):
        path = "/i/api/1.1/friendships/create.json"
        if user_id is None and screen_name is None:
            raise ValueError("Provide user_id or screen_name")
        if user_id is None:
            user = await self.resolve_screen_name(screen_name)
            user_id = user.rest_id
        payload = self._url_vars.follow_user(user_id)
        headers = self._headers.basic()
        r = await self._request(path, headers=headers, payload=payload, method="POST")
        r_js = await r.json()
        return r_js

    async def _get_periscope_login_token(self):
        path = "/i/api/1.1/oauth/authenticate_periscope.json"
        headers = self._headers.basic()
        r = await self._request(path, headers=headers, method="GET")
        r_js = await r.json()
        return r_js["token"]

    async def _login_proxsee_using_twitter_token(self, twitter_token: str):
        base_url = "https://proxsee.pscp.tv/"
        path = "api/v2/loginTwitterToken"
        payload = await self._payloads.proxsee_login(twitter_token)
        headers = self._headers.proxsee()
        r = await self._request(path, payload=payload, headers=headers, method="POST", base_url=base_url)
        r_js = await r.json()
        return r_js["cookie"]

    async def _get_chat_and_lifecycle_token(self, media_key: str):
        payload = self._url_vars.get_chat_and_lifecycle_token()
        path = f'/i/api/1.1/live_video_stream/status/{media_key}?{payload}'
        headers = self._headers.basic()
        r = await self._request(path, headers=headers, method="GET")
        text = await r.text()
        chat_token_regex = re.compile(r'\"chatToken"\s?:\s?\"(.*)\"', re.I)
        res = chat_token_regex.findall(text)
        chat_token = res[0].strip()
        life_cycle_token_regex = re.compile(
            r'\"lifecycleToken"\s?:\s?\"(.*)\"', re.IGNORECASE)
        res = life_cycle_token_regex.findall(text)
        lifecycle_token = res[0].strip()
        return chat_token, lifecycle_token

    async def _start_watching_space(self, lifecycle_token: str, cookie: str):
        base_url = "https://proxsee.pscp.tv"
        path = "/api/v2/startWatching"
        payload = await self._payloads.proxsee_start_watching(lifecycle_token=lifecycle_token,
                                                              cookie=cookie)
        headers = self._headers.proxsee_start_watching()
        r = await self._request(
            path=path,
            headers=headers,
            payload=payload, method="POST",
            base_url=base_url
        )
        r_js = await r.json()
        print(r_js)

    async def _access_chat(self, chat_token: str, cookie: str):
        base_url = 'https://proxsee.pscp.tv'
        path = "/api/v2/accessChat"
        headers = self._headers.acccess_chat()
        payload = await self._payloads.proxsee_access_chat(chat_token, cookie)
        r = await self._request(
            path=path, base_url=base_url,
            headers=headers, payload=payload,
            method="POST"
        )
        r_js = await r.json()
        print(r_js)

    async def join_space(self, space_media_key: str):
        """Join a space"""
        periscope_login_token = await self._get_periscope_login_token()
        cookie = await self._login_proxsee_using_twitter_token(periscope_login_token)
        chat_token, lifecycle_token = await self._get_chat_and_lifecycle_token(space_media_key)
        print("Cookie:", cookie)
        print("Chat token: ", chat_token)
        print("Life cycle Token: ", lifecycle_token)
        await self._access_chat(chat_token, cookie)
        await self._start_watching_space(lifecycle_token, cookie)

    async def update_banner(self, new_banner: str):
        """Update the banner"""
        path = "/i/api/1.1/account/update_profile_banner.json"
        media_id = await self.upload_media(new_banner)
        payload = self._url_vars.update_bannner(media_id)
        headers = self._headers.basic()
        r = await self._request(path, headers=headers, method="POST", payload=payload)
        if r.status == 200:
            await self.get_me()
            return await r.json()
        print(await r.text())

    async def get_email_phone_info(self):
        """Get all info about account"""
        path = "/i/api/1.1/users/email_phone_info.json"
        headers = self._headers.basic()
        r = await self._request(path, headers=headers, method="GET")
        if r.status == 200:
            return await r.json()

        print(await r.text())

    async def get_account_history_info(self):
        headers = self._headers.basic()
        while True:
            path = "/i/api/1.1/account/personalization/p13n_data.json"
            try:
                r = await self._request(path, headers=headers, method="GET")
                if r.status == 200:
                    return await r.json()
                else:
                    return print(await r.text())
            except exceptions.Forbidden:
                path = "/i/api/1.1/account/verify_password.json"
                headers = self._headers.basic()
                payload = self._url_vars.verify_password_view_info(
                    self._password)
                r = await self._request(path, headers=headers, payload=payload, method="POST")
                if r.status == 200:
                    # Password verified.
                    continue
                else:
                    print(await r.text())
                    break
