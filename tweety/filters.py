from typing import *
from .models import Tweet


def usernames_from_tweets(tweets_list: list) -> List:
    usernames = list()
    for tweet in tweets_list:
        usernames.append(
            tweet["core"]["user"]["legacy"]["screen_name"]
        )
    return list(set(usernames))


def mentions_from_tweet(tweet: dict) -> List[str]:
    mentions = tweet["legacy"]["entities"]["user_mentions"]
    usernames = list()
    for mention in mentions:
        if mention["screen_name"] not in usernames:
            usernames.append(mention["screen_name"])
    return list(set(usernames))


def tweets_from_entries(entries: List[Dict]) -> Tuple[List[Tweet], str, str]:
    """Filter tweet objects from entries list
    Returns => List[Tweet], Next_Cursor, Previous Cursor,
    """
    tweets = []
    next_cursor = ""
    previous_cursor = ""
    for entry in entries:
        if entry["entryId"].startswith("tweet-"):
            data = entry.get("content", {}).get("itemContent", {}).get(
                "tweet_results", {}).get("result", {})
            if data != {}:
                tweets.append(Tweet(data))
        elif entry["entryId"].startswith("cursor-top"):
            previous_cursor = entry["content"]["value"]

        elif entry["entryId"].startswith("cursor-bottom"):
            next_cursor = entry["content"]["value"]

    return tweets, next_cursor, previous_cursor
