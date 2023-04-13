

import json
import pprint


class User:
    def __init__(self, user_details: dict):
        # self.username = user_details.get("username")
        self.data = user_details
        self.rest_id = user_details.get("rest_id")
        self.id = user_details.get("id")
        legacy = user_details.get("legacy", None)
        if not legacy:
            legacy = user_details
        self.created_at = legacy.get("created_at")
        self.default_profile_image = legacy.get("default_profile_image")
        self.profile_image_url = legacy.get(
            "profile_image_url_https", "").replace("_normal", "")
        self.profile_banner_url = legacy.get("profile_banner_url", None)
        self.verified = legacy.get("verified")
        self.description = legacy.get("description")
        self.follow_request_sent = legacy.get("follow_request_sent")
        self.has_custom_timelines = legacy.get("has_custom_timelines")
        self.favourites_count = legacy.get("favourites_count")
        self.protected = legacy.get("protected")
        self.verified = legacy.get("verified")
        self.name = legacy.get("name")
        self.screen_name = legacy.get("screen_name")
        self.username = self.screen_name
        self.statuses_count = legacy.get("statuses_count")
        self.tweets_count = self.statuses_count
        self.location = legacy.get("location")
        self.friends_count = legacy.get("friends_count")
        self.can_dm = legacy.get("can_dm", False)
        self.followers_count = legacy.get("followers_count", 0)
        self.followings_count = self.friends_count
        self.normal_followers_count = legacy.get("normal_followers_count", 0)
        urls = legacy.get("entities", {}).get("url", {}).get("urls", [])
        urls = [url.get("expanded_url", None) for url in urls]
        self.user_urls = list(filter(lambda x: x is not None, urls))

    def __repr__(self):
        return self.screen_name

    def __str__(self) -> str:
        if self.screen_name:
            return self.screen_name
        return self.rest_id

    def print(self):
        pprint.pprint(self.data)


class ConnectedUser(User):
    def __init__(self, data: dict):
        super().__init__(data)


raw = '''
{'__typename': 'User', 'id': 'VXNlcjo0ODgwMDYwNzM5', 'rest_id': '4880060739', 'affiliates_highlighted_label': {}, 'legacy': {'blocked_by': False, 'blocking': False, 'can_dm': True, 'can_media_tag': True, 'created_at': 'Sat Feb 06 04:31:36 +0000 2016', 'default_profile': False, 'default_profile_image': False, 'description': 'oh sup I post the best memes daily so smash that follow button | @sourheath | @d3adv3k', 'entities': {'description': {'urls': []}}, 'fast_followers_count': 0, 'favourites_count': 3719, 'follow_request_sent': False, 'followed_by': False, 'followers_count': 271036, 'following': True, 'friends_count': 370, 'has_custom_timelines': True, 'is_translator': False, 'listed_count': 543, 'location': 'World 6', 'media_count': 190554, 'muting': False, 'name': 'my uncle’s meme stash', 'normal_followers_count': 271036, 'notifications': False, 'pinned_tweet_ids_str': ['1245586710676647939'], 'profile_banner_extensions': {'mediaColor': {'r': {'ok': {'palette': [{'percentage': 34.34, 'rgb': {'blue': 193, 'green': 195, 'red': 193}}, {'percentage': 28.91, 'rgb': {'blue': 77, 'green': 61, 'red': 47}}, {'percentage': 14.3, 'rgb': {'blue': 144, 'green': 107, 'red': 63}}, {'percentage': 5.92, 'rgb': {'blue': 72, 'green': 84, 'red': 117}}, {'percentage': 4.38, 'rgb': {'blue': 73, 'green': 177, 'red': 230}}]}}}}, 'profile_banner_url': 'https://pbs.twimg.com/profile_banners/4880060739/1594212854', 'profile_image_extensions': {'mediaColor': {'r': {'ok': {'palette': [{'percentage': 45.09, 'rgb': {'blue': 34, 'green': 45, 'red': 87}}, {'percentage': 23.19, 'rgb': {'blue': 122, 'green': 116, 'red': 126}}, {'percentage': 14.68, 'rgb': {'blue': 64, 'green': 52, 'red': 64}}, {'percentage': 10.08, 'rgb': {'blue': 17, 'green': 45, 'red': 95}}, {'percentage': 5.04, 'rgb': {'blue': 57, 'green': 63, 'red': 140}}]}}}}, 'profile_image_url_https': 'https://pbs.twimg.com/profile_images/1432614997771923457/Epp5DQ1v_normal.jpg', 'profile_interstitial_type': '', 'protected': False, 'screen_name': 'myunclesmemes', 'statuses_count': 192818, 'translator_type': 'none', 'verified': False, 'want_retweets': True, 'withheld_in_countries': []}, 'super_follow_eligible': False, 'super_followed_by': False, 'super_following': False}
'''


'''

"{'__typename': 'User', 'id': 'VXNlcjo0ODgwMDYwNzM5', 'rest_id': "
 "'4880060739', 'affiliates_highlighted_label': {}, 'legacy': {'blocked_by': "
 "False, 'blocking': False, 'can_dm': True, 'can_media_tag': True, "
 "'created_at': 'Sat Feb 06 04:31:36 +0000 2016', 'default_profile': False, "
 "'default_profile_image': False, 'description': 'oh sup I post the best memes "
 "daily so smash that follow button | @sourheath | @d3adv3k', 'entities': "
 "{'description': {'urls': []}}, 'fast_followers_count': 0, "
 "'favourites_count': 3719, 'follow_request_sent': False, 'followed_by': "
 "False, 'followers_count': 271036, 'following': True, 'friends_count': 370, "
 "'has_custom_timelines': True, 'is_translator': False, 'listed_count': 543, "
 "'location': 'World 6', 'media_count': 190554, 'muting': False, 'name': 'my "
 "uncle’s meme stash', 'normal_followers_count': 271036, 'notifications': "
 "False, 'pinned_tweet_ids_str': ['1245586710676647939'], "
 "'profile_banner_extensions': {'mediaColor': {'r': {'ok': {'palette': "
 "[{'percentage': 34.34, 'rgb': {'blue': 193, 'green': 195, 'red': 193}}, "
 "{'percentage': 28.91, 'rgb': {'blue': 77, 'green': 61, 'red': 47}}, "
 "{'percentage': 14.3, 'rgb': {'blue': 144, 'green': 107, 'red': 63}}, "
 "{'percentage': 5.92, 'rgb': {'blue': 72, 'green': 84, 'red': 117}}, "
 "{'percentage': 4.38, 'rgb': {'blue': 73, 'green': 177, 'red': 230}}]}}}}, "
 "'profile_banner_url': "
 "'https://pbs.twimg.com/profile_banners/4880060739/1594212854', "
 "'profile_image_extensions': {'mediaColor': {'r': {'ok': {'palette': "
 "[{'percentage': 45.09, 'rgb': {'blue': 34, 'green': 45, 'red': 87}}, "
 "{'percentage': 23.19, 'rgb': {'blue': 122, 'green': 116, 'red': 126}}, "
 "{'percentage': 14.68, 'rgb': {'blue': 64, 'green': 52, 'red': 64}}, "
 "{'percentage': 10.08, 'rgb': {'blue': 17, 'green': 45, 'red': 95}}, "
 "{'percentage': 5.04, 'rgb': {'blue': 57, 'green': 63, 'red': 140}}]}}}}, "
 "'profile_image_url_https': "
 "'https://pbs.twimg.com/profile_images/1432614997771923457/Epp5DQ1v_normal.jpg', "
 "'profile_interstitial_type': '', 'protected': False, 'screen_name': "
 "'myunclesmemes', 'statuses_count': 192818, 'translator_type': 'none', "
 "'verified': False, 'want_retweets': True, 'withheld_in_countries': []}, "
 "'super_follow_eligible': False, 'super_followed_by': False, "
 "'super_following': False}\n")


'''
