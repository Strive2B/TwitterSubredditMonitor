from .user import User
from typing import *


class SpaceState:
    LIVE = "Running"
    SCHEDULED = "NotStarted"
    ENDED = "Ended"


class Space:
    def __init__(self, data: dict):
        self.data = data
        self.metadata = data.get('metadata', {})
        self.rest_id = self.metadata.get('rest_id', None)
        self.state = self.metadata.get('state', None)
        self.title = self.metadata.get('title', None)
        self.media_key = self.metadata.get('media_key', None)
        self.created_at = self.metadata.get('created_at', 0)
        self.scheduled_start = self.metadata.get('scheduled_start', 0)
        self.updated_at = self.metadata.get('updated_at', 0)
        self.disallow_join = self.metadata.get('disallow_join', False)
        self.narrow_cast_space_type = self.metadata.get(
            'narrow_cast_space_type')
        self.is_employee_only = self.metadata.get('is_employee_only', False)
        self.is_locked = self.metadata.get('is_locked', False)
        self.is_space_available_for_replay = self.metadata.get(
            'is_space_available_for_replay', True)
        self.conversation_controls = self.metadata.get(
            'conversation_controls', 0)
        self.total_replay_watched = self.metadata.get(
            'total_replay_watched', 0)
        self.total_live_listeners = self.metadata.get(
            'total_live_listeners', 0)
        self.creator = User(self.metadata.get(
            "creator_results", {}).get("result"))
        self.is_subscribed = self.data.get("is_subscribed", False)
        participants = self.data.get("participants", {})
        self.total_participants = participants.get("total", 0)
        self.admins = self._extract_usernames(participants.get("admins", []))
        self.speakers = self._extract_usernames(
            participants.get("speakers", []))
        self.listeners = self._extract_usernames(
            participants.get("listeners", []))

    def _extract_usernames(self, items):
        usernames = []
        for item in items:
            usernames.append(item["twitter_screen_name"])
        return usernames

    @property
    def all_participants(self) -> List[str]:
        to_ret = []
        to_ret.extend(self.admins)
        to_ret.extend(self.speakers)
        to_ret.extend(self.listeners)
        return to_ret

    def __repr__(self):
        return self.title



    @property
    def is_live(self) ->  bool:
        return self.state == SpaceState.LIVE

    @property 
    def is_ended(self) -> bool:
        return self.state == SpaceState.ENDED

    @property
    def is_scheduled(self) -> bool:
        return self.state == SpaceState.SCHEDULED

    