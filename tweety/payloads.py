from urllib import parse
import json
import random
import os


def rc(len):
    return os.urandom(len).hex()[len:]


class Payloads:
    def escape_json(self, d: dict):
        return json.dumps(d).replace('"', '\"')

    async def login_flow_start(self):
        payload = {"input_flow_data": {"flow_context": {"debug_overrides": {},
                                                        "start_location": {"location": "splash_screen"}}},
                   "subtask_versions": {"contacts_live_sync_permission_prompt": 0,
                                        "email_verification": 0,
                                        "topics_selector": 1,
                                        "wait_spinner": 1,
                                        "cta": 4}}

        return json.dumps(payload)

    async def send_ref_payload(self, flow_token: str):
        reference = """{"rf":{"aabfb3f2a44e6872ef0e73fc0bb6216ba254ce61bba010e0fa74c583dfd21c46":-185,"a1ccdc032d49b6bc60fd8c247a82dfe523d580a3de8385b756967fbb3fda22f8":4,"cec1d788be8325c3f325ff5db569f2f292fe22593ad80e85ebeb4714985f9770":71,"a5edf25f704a8949380a729e29adc393bc1f82ca88423faf4f0b4ce78a7118fa":132},"s":"qKiBOilLsyThXGIjNfVzLzfxpHFL1KgSB8P8bYu06RypkWWgbDstF-1X-sGGgg6bFxP2H2InlI7_xqeyvLdqbl8v8dGhvTnbKGcqq1dITysCobMIsBzifkfxr092S0kXADBRtnh26BJC2pPf9nbZdD47x4UG6uYYWXEz0sKao0_VPKdJfEHQYmvCfyJnDCTE9lj1RpUJ8EQsYES_MoXqIey25bhPf9-OpNKfRYVEyY-skE6cRbh4s5-bz8uzygnIbdo4xrXpUxSfXO5kHmhe7Q3dLkWE045qadQ1I4rtb55hqQkJsz4x4I245YiDRYwTVC20W36ZNCXz2pCZS8UT9wAAAYF63SO0"}"""
        payload = {"flow_token": flow_token,
                   "subtask_inputs": [{"subtask_id": "LoginJsInstrumentationSubtask",
                                       "js_instrumentation": {"response": reference,
                                                              "link": "next_link"}}]}

        return json.dumps(payload)

    async def send_email(self, email: str, flow_token: str):
        payload = {"flow_token": flow_token,
                   "subtask_inputs": [{"subtask_id": "LoginEnterUserIdentifierSSO",
                                       "settings_list": {"setting_responses": [{"key": "user_identifier",
                                                                                "response_data": {"text_data": {"result": email}}}],
                                                         "link": "next_link"}}]}
        return json.dumps(payload)

    async def send_alt_id(self, flow_token: str, alt: str):
        payload = {"flow_token": flow_token, "subtask_inputs": [
            {"subtask_id": "LoginEnterAlternateIdentifierSubtask",
             "enter_text": {"text": alt, "link": "next_link"}}]}
        return json.dumps(payload)

    async def send_password(self, password: str, flow_token: str):
        payload = {"flow_token": flow_token, "subtask_inputs": [
            {"subtask_id": "LoginEnterPassword", "enter_password": {"password": password, "link": "next_link"}}]}

        return json.dumps(payload)

    async def send_phone(self, phone_number: str, flow_token: str):
        payload = {"flow_token": flow_token,
                   "subtask_inputs": [{"subtask_id": "LoginAcid",
                                       "enter_text": {"text": phone_number, "link": "next_link"}}]}

        return json.dumps(payload)

    async def send_duplicate_account_check(self, flow_token: str):
        payload = {"flow_token": flow_token, "subtask_inputs": [
            {"subtask_id": "AccountDuplicationCheck", "check_logged_in_account": {"link": "AccountDuplicationCheck_false"}}]}
        return json.dumps(payload)

    async def post_tweet(self, text: str, query_id: str,
                         in_reply_to_tweet_id: str = None,
                         quoted_tweet_id: str = None,
                         media_ids=[]):
        variables = {"tweet_text": text,
                     "media": {"media_entities": [],
                               "possibly_sensitive": False},
                     "withDownvotePerspective": False,
                     "withReactionsMetadata": False,
                     "withReactionsPerspective": False,
                     "withSuperFollowsTweetFields": True,
                     "withSuperFollowsUserFields": True,
                     "semantic_annotation_ids": [],
                     "dark_request": False}
        features = {"dont_mention_me_view_api_enabled": True,
                    "interactive_text_enabled": True,
                    "responsive_web_uc_gql_enabled": False,
                    "vibe_tweet_context_enabled": False,
                    "responsive_web_edit_tweet_api_enabled": False}
        if len(media_ids) > 0:
            media = {
                "media_entities": [{"media_id": str(media_id), "tagged_users": []} for media_id in media_ids]
            }
            variables.update({
                "media": media,
                "possibly_sensitive": False
            })
        if in_reply_to_tweet_id is not None:
            variables.update({
                "reply": {
                    "in_reply_to_tweet_id": str(in_reply_to_tweet_id),
                    "exclude_reply_user_ids": []
                }
            })
        elif quoted_tweet_id is not None:
            variables.update({
                "attachment_url": f"https://twitter.com/i/status/{quoted_tweet_id}"
            })
        return json.dumps({"variables": self.escape_json(variables), "features": features,
                           "queryId": str(query_id)})

    async def retweet(self, tweet_id: str, query_id: str):
        """Retweet a tweet with specific id."""
        variables = self.escape_json(
            {"tweet_id": str(tweet_id), "dark_request": False})
        payload = {"variables": variables,
                   "queryId": str(query_id)}
        return json.dumps(payload)

    async def favorite_tweet(self, tweet_id: str, query_id: str):
        """Favorite/like a tweet with id."""
        ...
        variables = self.escape_json({"tweet_id": str(tweet_id)})
        payload = {"variables": variables, "queryId": str(query_id)}

        return json.dumps(payload)

    async def upload_media(self):
        """Upload media to twitter for attaching to tweet."""
        url = "https://upload.twitter.com/i/media/upload.json?command=INIT&total_bytes=38563&media_type=image/png&media_category=tweet_image"

    async def login_recaptcha(self, flow_token: str, recaptcha_response: str):
        payload = {"flow_token": flow_token,
                   "subtask_inputs": [{"subtask_id": "LoginPrivacyWarningRecaptchaSubtask",
                                       "cta": {"link": "next_link"}},
                                      {"subtask_id": "LoginThrowRecaptchaSubtask",
                                       "recaptcha": {"link": "next_link",
                                                     "recaptcha_response": recaptcha_response}}]}

        return json.dumps(payload)

    async def login_acid(self, flow_token: str, acid: str):
        """Payload to send the phone/email number"""
        payload = {"flow_token": str(flow_token),
                   "subtask_inputs": [{"subtask_id": "LoginAcid",
                                       "enter_text": {"text": str(acid), "link": "next_link"}}]}

        return json.dumps(payload)

    async def update_profile_picture(self, media_id: int):
        ...
        return f"""include_profile_interstitial_type=1&include_blocking=1&include_blocked_by=1&include_followed_by=1&include_want_retweets=1&include_mute_edge=1&include_can_dm=1&include_can_media_tag=1&include_ext_has_nft_avatar=1&skip_status=1&return_user=true&media_id={media_id}"""

    async def proxsee_login(self, login_token: str):
        payload = {"jwt": login_token, "vendor_id": "m5-proxsee-login-a2011357b73e",
                   "create_user": False, "direct": True}

        return json.dumps(payload)

    async def proxsee_start_watching(self, lifecycle_token: str, cookie: str):
        payload = {"life_cycle_token": lifecycle_token,
                   "auto_play": False, "cookie": cookie}

        return json.dumps(payload)

    async def proxsee_access_chat(self, chat_token: str, cookie: str):
        payload = {"chat_token": chat_token, "cookie": cookie}
        return json.dumps(payload)


class URLVars:
    req_ids = [
        "2a229340-b91a-11ec-aa32-5338c15e1b15",
        "bd8a2130-b919-11ec-aa32-5338c15e1b15",
        "0c72b670-b91c-11ec-87a3-fd5ffc66fc25",
        "b73fe1d0-b91d-11ec-9323-5364e1115943",
        "11f149f0-aa89-11ec-bcb0-5fd2ab64d501"
    ]

    def gen_req_id(self):
        return f"{rc(8)}-{rc(4)}-{rc(4)}-{rc(4)}-{12}"

    def encode_follows_vars(self, user_id: int, count=1000, cursor: str = -1):
        payload = {'userId': user_id,
                   'count': count,
                   'cursor': str(cursor),
                   'withTweetQuoteCount': False,
                   'includePromotedContent': False,
                   'withSuperFollowsUserFields': True,
                   'withUserResults': True,
                   'withBirdwatchPivots': False,
                   'withReactionsMetadata': False,
                   'withReactionsPerspective': False,
                   'withSuperFollowsTweetFields': True}
        return parse.quote(str(json.dumps(payload)))

    def encode_screen_name_vars(self, screen_name: str):
        return parse.quote(str(json.dumps({"screen_name": screen_name,
                                           "withSafetyModeUserFields": False,
                                           "withSuperFollowsUserFields": False})))

    def encode_tweet_details_vars(self, tweet_id: int, cursor: str = None):
        payload = {"focalTweetId": str(tweet_id),
                   "cursor": cursor,
                   "referrer": "tweet",
                   "with_rux_injections": False,
                   "includePromotedContent": True,
                   "withCommunity": True,
                   "withTweetQuoteCount": True,
                   "withBirdwatchNotes": False,
                   "withSuperFollowsUserFields": True,
                   "withUserResults": False,
                   "withBirdwatchPivots": False,
                   "withReactionsMetadata": False,
                   "withReactionsPerspective": False,
                   "withSuperFollowsTweetFields": True,
                   "withVoice": True}
        if cursor:
            payload.update({
                "cursor": cursor
            })
        return parse.quote(str(json.dumps(payload)))

    def decode_variables(self, variables_string: str):
        return json.loads(parse.unquote(variables_string))

    def viewer_vars(self):
        payload = {"withCommunitiesMemberships": True,
                   "withCommunitiesCreation": True, "withSuperFollowsUserFields": True}
        return parse.quote(str(json.dumps(payload)))

    def hastags_scrape_variables(self):
        return "include_profile_interstitial_type=1&include_blocking=1&include_blocked_by=1&include_followed_by=1&include_want_retweets=1&include_mute_edge=1&include_can_dm=1&include_can_media_tag=1&include_ext_has_nft_avatar=1&skip_status=1&cards_platform=Web-12&include_cards=1&include_ext_alt_text=true&include_quote_count=true&include_reply_count=1&tweet_mode=extended&include_entities=true&include_user_entities=true&include_ext_media_color=true&include_ext_media_availability=true&include_ext_sensitive_media_warning=true&include_ext_trusted_friends_metadata=true&send_error_codes=true&simple_quoted_tweet=true&cd=HBgZI0FsbGFtYUtoYWRpbUh1c3NhaW5SaXp2aRgkN2M5YjI2OTQtZTdmNy00NWEwLTgyZTEtYTc5ZDU3ODRhNzE3AAA=&q=#AllamaKhadimHussainRizvi&count=20&query_source=typed_query&pc=1&spelling_corrections=1&ext=mediaStats,highlightedLabel,hasNftAvatar,voiceInfo,enrichments,superFollowMetadata"

    def tweet_likers(self, tweet_id: int, cursor: str = None, count=100):
        payload = {"tweetId": str(tweet_id), "count": count, "includePromotedContent": True,
                   "withSuperFollowsUserFields": True,
                   "withDownvotePerspective": False,
                   "withReactionsMetadata": True,
                   "withReactionsPerspective": False,
                   "withSuperFollowsTweetFields": True,
                   "__fs_dont_mention_me_view_api_enabled": False,
                   "__fs_interactive_text_enabled": True,
                   "__fs_responsive_web_uc_gql_enabled": False}
        if cursor:
            payload.update({
                "cursor": cursor
            })

        return parse.quote(str(json.dumps(payload)))

    def retweeters(tweet_id: int, cursor=None, count=100):
        payload = {"tweetId": str((tweet_id)), "count": count, "cursor": str(cursor), "includePromotedContent": True,
                   "withSuperFollowsUserFields": True,
                   "withDownvotePerspective": False,
                   "withReactionsMetadata": False,
                   "withReactionsPerspective": False,
                   "withSuperFollowsTweetFields": True,
                   "__fs_dont_mention_me_view_api_enabled": False,
                   "__fs_interactive_text_enabled": True,
                   "__fs_responsive_web_uc_gql_enabled": False}
        return parse.quote(str(json.dumps(payload)))

    def latest_from_hashtag(self, hashtag: str, cursor: str = None, count=100):
        payload = f"""include_profile_interstitial_type=1
    &include_blocking=1
    &include_blocked_by=1
    &include_followed_by=1
    &include_want_retweets=1
    &include_mute_edge=1
    &include_can_dm=1
    &include_can_media_tag=1
    &include_ext_has_nft_avatar=1
    &skip_status=1
    &cards_platform=Web-12
    &include_cards=1
    &include_ext_alt_text=true
    &include_quote_count=true
    &include_reply_count=1
    &tweet_mode=extended
    &include_entities=true
    &include_user_entities=true
    &include_ext_media_color=true
    &include_ext_media_availability=true
    &include_ext_sensitive_media_warning=true
    &include_ext_trusted_friends_metadata=true
    &send_error_codes=true
    &simple_quoted_tweet=true
    &q=%23{hashtag.replace("#", "")}
    &vertical=trends
    &tweet_search_mode=live
    &count={count}
    &query_source=trend_click
    &pc=1
    &spelling_corrections=1"""
        ext = "mediaStats,highlightedLabel,hasNftAvatar,voiceInfo,enrichments,superFollowMetadata"
        encoded_ext = parse.quote(str(ext))

        payload = f"{payload}&ext={encoded_ext}"
        if cursor:
            payload = f"{payload}&cursor={cursor}"

        return payload

    def send_dm(self, text: str, conversation_id: str):
        encoded_txt = parse.quote(text)
        payload = f'cards_platform=Web-12&include_cards=1&include_ext_alt_text=true&include_quote_count=true&include_reply_count=1&tweet_mode=extended&dm_users=false&include_groups=true&include_inbox_timelines=true&include_ext_media_color=true&supports_reactions=true&text={encoded_txt}&conversation_id={conversation_id}&recipient_ids=false&request_id={self.gen_req_id()}&ext=mediaColor%2CaltText%2CmediaStats%2ChighlightedLabel%2ChasNftAvatar%2CvoiceInfo%2Cenrichments%2CsuperFollowMetadata'
        return payload

    def get_me(self):
        return "include_mention_filter=true&include_nsfw_user_flag=true&include_nsfw_admin_flag=true&include_ranked_timeline=true&include_alt_text_compose=true&ext=ssoConnections&include_country_code=true&include_ext_dm_nsfw_media_filter=true&include_ext_sharing_audiospaces_listening_data_with_followers=true"

    def get_home_timeline(self):
        return "include_profile_interstitial_type=1&include_blocking=1&include_blocked_by=1&include_followed_by=1&include_want_retweets=1&include_mute_edge=1&include_can_dm=1&include_can_media_tag=1&include_ext_has_nft_avatar=1&skip_status=1&cards_platform=Web-12&include_cards=1&include_ext_alt_text=true&include_quote_count=true&include_reply_count=1&tweet_mode=extended&include_entities=true&include_user_entities=true&include_ext_media_color=true&include_ext_media_availability=true&include_ext_sensitive_media_warning=true&include_ext_trusted_friends_metadata=true&send_error_codes=true&simple_quoted_tweet=true&earned=1&count=20&lca=true&ext=mediaStats,highlightedLabel,hasNftAvatar,replyvotingDownvotePerspective,voiceInfo,enrichments,superFollowMetadata,unmentionInfo"

    def update_profile(self, name="", description="", location=""):
        name = parse.quote(name)
        description = parse.quote(description)
        return f"displayNameMaxLength=50&name={name}&description={description}&location={location}"

    def upload_media_init(self, total_bytes: int, image_extension: str):
        return f"command=INIT&total_bytes={total_bytes}&media_type=image%2F{image_extension}"

    def upload_media_append(self, media_id: int):
        return f"command=APPEND&media_id={media_id}&segment_index=0"

    def upload_media_final(self, media_id: int):
        return f"command=FINALIZE&media_id={media_id}"

    def search(self, search_term: str,
               search_filter: str,
               count=20,
               cursor=None):
        payload = f"""
        include_profile_interstitial_type=1
        &include_blocking=1
        &include_blocked_by=1
        &include_followed_by=1
        &include_want_retweets=1
        &include_mute_edge=1
        &include_can_dm=1
        &include_can_media_tag=1
        &include_ext_has_nft_avatar=1
        &skip_status=1
        &cards_platform=Web-12
        &include_cards=1
        &include_ext_alt_text=true
        &include_quote_count=true
        &include_reply_count=1
        &tweet_mode=extended
        &include_entities=true
        &include_user_entities=true
        &include_ext_media_color=true
        &include_ext_media_availability=true
        &include_ext_sensitive_media_warning=true
        &include_ext_trusted_friends_metadata=true
        &send_error_codes=true
        &simple_quoted_tweet=true
        &q={search_term}
        &result_filter={search_filter}
        &count={count}
        &query_source=typed_query
        &pc=1
        &spelling_corrections=1
        """
        ext = "mediaStats,highlightedLabel,hasNftAvatar,voiceInfo,enrichments,superFollowMetadata,unmentionInfo"
        encoded_ext = parse.quote(str(ext))

        payload = f"{payload}&ext={encoded_ext}"
        if cursor:
            payload = f"{payload}&cursor={cursor}"

        return payload

    def update_username(self, username: str):
        return f"include_mention_filter=true&include_nsfw_user_flag=true&include_nsfw_admin_flag=true&include_ranked_timeline=true&include_alt_text_compose=true&screen_name={username}"

    async def get_user_tweets(self, user_id: int,
                              count=100,
                              cursor: str = None):
        """Get user tweets"""
        variables = {"userId": str(user_id),
                     "count": count,
                     "includePromotedContent": True,
                     "withQuickPromoteEligibilityTweetFields": True,
                     "withSuperFollowsUserFields": True,
                     "withDownvotePerspective": True,
                     "withReactionsMetadata": False,
                     "withReactionsPerspective": False,
                     "withSuperFollowsTweetFields": True,
                     "withVoice": True,
                     "withV2Timeline": True}
        if cursor is not None:
            variables.update({
                "cursor": cursor,
            })
        features = {"dont_mention_me_view_api_enabled": True,
                    "interactive_text_enabled": True,
                    "responsive_web_uc_gql_enabled": False,
                    "vibe_tweet_context_enabled": False,
                    "responsive_web_edit_tweet_api_enabled": False,
                    "standardized_nudges_misinfo": False,
                    "responsive_web_enhance_cards_enabled": False}

        return f"variables={parse.quote(json.dumps(variables))}&features={parse.quote(json.dumps(features))}"

    async def get_space_info(self, space_id: str):
        variables = {"id": space_id, "isMetatagsQuery": False,
                     "withSuperFollowsUserFields": True,
                     "withDownvotePerspective": True,
                     "withReactionsMetadata": False,
                     "withReactionsPerspective": False,
                     "withSuperFollowsTweetFields": True,
                     "withReplays": True}

        features = {"dont_mention_me_view_api_enabled": True,
                    "interactive_text_enabled": True,
                    "responsive_web_uc_gql_enabled": False,
                    "vibe_tweet_context_enabled": False,
                    "responsive_web_edit_tweet_api_enabled": False,
                    "standardized_nudges_misinfo": False,
                    "responsive_web_enhance_cards_enabled": False}

        return f"variables={parse.quote(json.dumps(variables))}&features={parse.quote(json.dumps(features))}"

    def follow_user(self, user_id: int):
        return f"""include_profile_interstitial_type=1&include_blocking=1&include_blocked_by=1&include_followed_by=1&include_want_retweets=1&include_mute_edge=1&include_can_dm=1&include_can_media_tag=1&include_ext_has_nft_avatar=1&skip_status=1&user_id={user_id}"""

    def get_chat_and_lifecycle_token(self):
        return f"""client=web&use_syndication_guest_id=false&cookie_set_host=twitter.com"""

    def update_bannner(self, media_id: int):
        return f"""include_profile_interstitial_type=1&include_blocking=1&include_blocked_by=1&include_followed_by=1&include_want_retweets=1&include_mute_edge=1&include_can_dm=1&include_can_media_tag=1&include_ext_has_nft_avatar=1&skip_status=1&return_user=true&media_id={media_id}"""

    def verify_password_view_info(self, password: str):
        return f"""password={password}"""
