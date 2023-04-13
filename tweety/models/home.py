from ..api import Client
from .tweet import Tweet
from typing import *


class Timeline:
    def __init__(self, client: Client, data: Dict):
        self._client = client
        self._data = data
        self.tweets = self._parse_tweets()

    def _parse_tweets(self) -> List[Tweet]:
        tweets = []

        return tweets
