

import os
import aiohttp
from .static import USER_AGENTS_LIST
import random


class Headers:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
        self.guest_token = None
        self.csrf_token = self.rc()
        self.user_agent = self.new_agent()
        self.login_referer = "https://twitter.com/i/flow/login"
        self.home_referer = 'https://twitter.com/home'

    def new_agent(self):
        return random.choice(USER_AGENTS_LIST)

    def rc(self, length=32):
        return os.urandom(int(length/2)).hex()

    async def load(self) -> "Headers":
        self.guest_token = await self._get_guest_token()
        return self

    async def _get_guest_token(self):
        headers = self.basic()
        async with self.session.post("https://api.twitter.com/1.1/guest/activate.json",
                                     headers=headers) as resp:
            await resp.read()
            data = await resp.json()
            # print(data)
            return data["guest_token"]

    def logged_in(self, new_agent=False):
        if new_agent:
            user_agent = self.new_agent()
        else:
            user_agent = self.user_agent

        headers = {
            'authority': 'twitter.com',
            'x-twitter-client-language': 'en',
            'x-csrf-token': self.csrf_token,
            'sec-ch-ua-mobile': '?0',
            'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            'content-type': 'application/json',
            'user-agent': user_agent,
            'x-twitter-auth-type': 'OAuth2Session',
            'x-twitter-active-user': 'yes',
            'sec-ch-ua-platform': '"Linux"',
            'accept': '*/*',
            'origin': 'https://twitter.com',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': self.home_referer,
            'accept-language': 'en-US,en;q=0.9',
        }
        return headers

    def basic(self):
        return {
            'authority': 'twitter.com',
            'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            'x-twitter-client-language': 'en',
            # The length of x-csrf-token for login is 32
            'x-csrf-token': self.csrf_token,
            'x-twitter-active-user': 'yes',
            'user-agent': self.user_agent,
            'content-type': 'application/x-www-form-urlencoded',
            'accept': '*/*',
            'sec-gpc': '1',
            'origin': 'https://twitter.com',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': self.login_referer,
            'accept-language': 'en-US,en;q=0.9',
            # 'Cookie': 'att=1-FoLw9bYoOrChtA4scKATHilgxMBWoMwjCQKvYNZQ; guest_id=v1%3A164175159972370562; guest_id_ads=v1%3A164175159972370562; guest_id_marketing=v1%3A164175159972370562; personalization_id="v1_s99wGN9B1j2Xp/12tkX/bw=="'
        }

    async def login_flow(self):
        headers = {
            'authority': 'twitter.com',
            'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            'x-twitter-client-language': 'en',
            # The length of x-csrf-token for login is 32
            'x-csrf-token': self.csrf_token,
            'x-guest-token': self.guest_token,
            'x-twitter-active-user': 'yes',
            'user-agent': self.user_agent,
            'content-type': 'application/json',
            'accept': '*/*',
            'sec-gpc': '1',
            'origin': 'https://twitter.com',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': self.login_referer,
            'accept-language': 'en-US,en;q=0.9',
            # 'Cookie': 'att=1-FoLw9bYoOrChtA4scKATHilgxMBWoMwjCQKvYNZQ; guest_id=v1%3A164175159972370562; guest_id_ads=v1%3A164175159972370562; guest_id_marketing=v1%3A164175159972370562; personalization_id="v1_s99wGN9B1j2Xp/12tkX/bw=="'
        }

        return headers

    def json_content(self, new_agent=False):
        if new_agent:
            user_agent = self.new_agent()
        else:
            user_agent = self.user_agent

        return {
            'authority': 'twitter.com',
            'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            'x-twitter-client-language': 'en',
            # The length of x-csrf-token for login is 32
            'x-csrf-token': self.csrf_token,
            'x-twitter-active-user': 'yes',
            'user-agent': user_agent,
            'content-type': 'application/json',
            'accept': '*/*',
            'sec-gpc': '1',
            'origin': 'https://twitter.com',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': self.login_referer,
            'accept-language': 'en-US,en;q=0.9',
        }

    def send_dm(self):
        basic = self.basic()
        basic["content-type"] = 'application/x-www-form-urlencoded'
        return basic

    async def manual_load(self, csrf_token: str, cookies: str):
        self.csrf_token = csrf_token
        headers = {
            'authority': 'twitter.com',
            'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            'x-twitter-client-language': 'en',
            # The length of x-csrf-token for login is 32
            'x-csrf-token': self.csrf_token,
            # 'x-guest-token': self.guest_token,
            'x-twitter-active-user': 'yes',
            'user-agent': self.user_agent,
            'content-type': 'application/json',
            'accept': '*/*',
            'sec-gpc': '1',
            'origin': 'https://twitter.com',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': self.home_referer,
            'accept-language': 'en-US,en;q=0.9',
            'Cookie': cookies
        }
        return headers

    async def upload_media_init(self):
        ...
        headers = {
            'authority': 'upload.twitter.com',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            'content-length': '0',
            'origin': 'https://twitter.com',
            'referer': 'https://twitter.com/',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="101"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': self.user_agent,
            'x-csrf-token': self.csrf_token,
            'x-twitter-auth-type': 'OAuth2Session'
        }
        return headers

    async def upload_media_append(self):
        headers = {
            'authority': 'upload.twitter.com',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            'origin': 'https://twitter.com',
            'referer': 'https://twitter.com/',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="101"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': self.user_agent,
            'x-csrf-token': self.csrf_token,
            'x-twitter-auth-type': 'OAuth2Session'
        }

        return headers

    async def upload_media_final(self):
        headers = {
            'authority': 'upload.twitter.com',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            'content-length': '0',
            'origin': 'https://twitter.com',
            'referer': 'https://twitter.com/',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="101"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': self.user_agent,
            'x-csrf-token': self.csrf_token,
            'x-twitter-auth-type': 'OAuth2Session'
        }

        return headers

    def proxsee(self):
        headers = {
            "content-type": "application/json",
            "user-agent": self.user_agent,
            "X-Periscope-User-Agent": "Twitter/m5",
            "X-Attempt": str(1),
        }
        return headers

    def proxsee_start_watching(self):
        headers = {
            'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            "content-type": "application/json",
            "user-agent": self.user_agent,
            "X-Periscope-User-Agent": "Twitter/video-analytics",
            "X-Attempt": str(1),
            'x-csrf-token': self.csrf_token,
        }
        return headers

    def acccess_chat(self):
        headers = {
            "content-type": "application/json",
            "User-Agent": self.user_agent,
            "X-Periscope-User-Agent": "Twitter/m5",
            "X-Attempt": str(1),
        }
        return headers
