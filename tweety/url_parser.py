import json
from urllib import parse

followers_variables = {'userId': '', 'count': 0, 'cursor': '-1', 'withTweetQuoteCount': False, 'includePromotedContent': False,
                       'withSuperFollowsUserFields': True, 'withUserResults': True, 'withBirdwatchPivots': False, 'withReactionsMetadata': False, 'withReactionsPerspective': False, 'withSuperFollowsTweetFields': True}


def encode_follows_vars(user_id: int, count=1000, cursor: str = -1):
    payload = {'userId': user_id, 'count': count, 'cursor': str(cursor), 'withTweetQuoteCount': False, 'includePromotedContent': False,
               'withSuperFollowsUserFields': True, 'withUserResults': True, 'withBirdwatchPivots': False, 'withReactionsMetadata': False, 'withReactionsPerspective': False, 'withSuperFollowsTweetFields': True}
    return parse.quote(str(json.dumps(payload)))


def encode_screen_name_vars(screen_name: str):
    return parse.quote(str(json.dumps({"screen_name": screen_name,
                                       "withSafetyModeUserFields": False,
                                       "withSuperFollowsUserFields": False})))


def encode_tweet_details_vars(tweet_id: int, cursor: str = None):
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


def decode_variables(variables_string: str):
    return json.loads(parse.unquote(variables_string))


def encode_get_tweets_vars(user_id: str, cursor=None, with_tweet_quote_count=True,
                           count=50, include_promoted_content=True,
                           with_v2_timeline=False):
    """
    {"userId":"1303577160234328066","count":40,"withTweetQuoteCount":true,
    "includePromotedContent":true,
    "withQuickPromoteEligibilityTweetFields":true,"withSuperFollowsUserFields":true,
    "withBirdwatchPivots":false,"withDownvotePerspective":false,"withReactionsMetadata":false,
    "withReactionsPerspective":false,
    "withSuperFollowsTweetFields":true,"withVoice":true,"withV2Timeline":false}
    """
    payload = {"userId": str(user_id),
               "count": count,
               "withTweetQuoteCount": with_tweet_quote_count,
               "includePromotedContent": include_promoted_content,
               "withQuickPromoteEligibilityTweetFields": True,
               "withSuperFollowsUserFields": True,
               "withBirdwatchPivots": False,
               "withDownvotePerspective": False,
               "withReactionsMetadata": False,
               "withReactionsPerspective": False,
               "withSuperFollowsTweetFields": True,
               "withVoice": True,
               "withV2Timeline": with_v2_timeline}

    if cursor:
        payload.update({
            "cursor": cursor,
        })

    return parse.quote(str(json.dumps(payload)))


def viewer_vars():
    payload = {"withCommunitiesMemberships": True,
               "withCommunitiesCreation": True, "withSuperFollowsUserFields": True}
    return parse.quote(str(json.dumps(payload)))


def hastags_scrape_variables():
    return "include_profile_interstitial_type=1&include_blocking=1&include_blocked_by=1&include_followed_by=1&include_want_retweets=1&include_mute_edge=1&include_can_dm=1&include_can_media_tag=1&include_ext_has_nft_avatar=1&skip_status=1&cards_platform=Web-12&include_cards=1&include_ext_alt_text=true&include_quote_count=true&include_reply_count=1&tweet_mode=extended&include_entities=true&include_user_entities=true&include_ext_media_color=true&include_ext_media_availability=true&include_ext_sensitive_media_warning=true&include_ext_trusted_friends_metadata=true&send_error_codes=true&simple_quoted_tweet=true&cd=HBgZI0FsbGFtYUtoYWRpbUh1c3NhaW5SaXp2aRgkN2M5YjI2OTQtZTdmNy00NWEwLTgyZTEtYTc5ZDU3ODRhNzE3AAA=&q=#AllamaKhadimHussainRizvi&count=20&query_source=typed_query&pc=1&spelling_corrections=1&ext=mediaStats,highlightedLabel,hasNftAvatar,voiceInfo,enrichments,superFollowMetadata"


def tweet_likers(tweet_id: int, cursor: str = None, count=100):
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


def latest_from_hashtag(hashtag: str, cursor: str = None, count=100):
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


def send_dm(text: str, conversation_id: str):
    encoded_txt = parse.quote(text)
    payload = f'cards_platform=Web-12&include_cards=1&include_ext_alt_text=true&include_quote_count=true&include_reply_count=1&tweet_mode=extended&dm_users=false&include_groups=true&include_inbox_timelines=true&include_ext_media_color=true&supports_reactions=true&text={encoded_txt}&conversation_id={conversation_id}&recipient_ids=false&request_id=11f149f0-aa89-11ec-bcb0-5fd2ab64d501&ext=mediaColor%2CaltText%2CmediaStats%2ChighlightedLabel%2ChasNftAvatar%2CvoiceInfo%2Cenrichments%2CsuperFollowMetadata'
    return payload


def get_me():
    return "include_mention_filter=true&include_nsfw_user_flag=true&include_nsfw_admin_flag=true&include_ranked_timeline=true&include_alt_text_compose=true&ext=ssoConnections&include_country_code=true&include_ext_dm_nsfw_media_filter=true&include_ext_sharing_audiospaces_listening_data_with_followers=true"
