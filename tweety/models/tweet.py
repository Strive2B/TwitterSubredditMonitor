from .user import User
from pprint import pprint
import datetime as dt


class Tweet:
    def __init__(self, data: dict):
        self.data = data
        self.rest_id = data.get("rest_id")
        data = data.get("legacy")
        self.id = data.get("id_str")
        self._id = self.id
        self.full_text = data.get("full_text", "")
        self.created_at = data.get("created_at")
        self.truncated = data.get("truncated")
        self.display_text_range = data.get("display_text_range")
        self.in_reply_to_status_id = data.get("'in_reply_to_status_id")
        self.in_reply_to_user_id = data.get("in_reply_to_user_id")
        self.in_reply_to_screen_name = data.get("in_reply_to_screen_name")
        self.user_id = data.get("user_id")
        self.geo = data.get("geo", None)
        self.coordinates = data.get("coordinates", None)
        self.place = data.get("place", None)
        self.contributors = data.get("contributors", None)
        self.is_quote_status = data.get("is_quote_status")
        self.retweet_count = data.get("retweet_count")
        self.favorite_count = data.get("favorite_count")
        self.reply_count = data.get("reply_count")
        self.quote_count = data.get("quote_count")
        self.conversation_id = data.get("conversation_id")
        self.favorited = data.get("favorited")
        self.retweeted = data.get("retweeted")
        self.lang = data.get("lang")
        self.ext = data.get("ext")
        self.extended_entities = data.get("extended_entities")
        self.user: User = User(self.data.get("core", {}).get("user", {}))

    def __repr__(self):
        return self.full_text

    def pprint(self):
        pprint(self.data)

    @property
    def created_at_ts(self) -> int:
        _created_at = str(self.created_at)
        month = _created_at.split(" ")[1]
        day = _created_at.split(" ")[2]
        year = _created_at.split(" ")[-1]
        time = _created_at.split(" ")[3]
        created_at = f"{month} {day} {year} {time}"
        fmt = "%b %d %Y %H:%M:%S"
        return int(dt.datetime.strptime(created_at, fmt).timestamp())
