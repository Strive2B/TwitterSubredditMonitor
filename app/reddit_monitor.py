"""
Class to monitor subreddit
"""

import asyncpraw
from asyncpraw import reddit
from asyncprawcore.exceptions import Forbidden
import re
import asyncio
from typing import *
from app import logger


class SubredditMonitor:
    def __init__(self, subreddit: str,
                 queue: asyncio.Queue,
                 client_id: str,
                 client_secret: str,
                 user_agent: str,
                 monitor_comments=False
                 ):
        """
        client_id: Client id obtained from the reddit dev portal
        client_secret: Client secret obtained from the reddit dev portal
        user_agent:  This should be unique and must include username of the app owner. 
                    i.e wsb by u/rehmanali944
        subreddit: The name of the subreddit you want to monitor
        queue: The queue for output data. Submissions.

        """
        self._mon_comments = monitor_comments
        self._client = asyncpraw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
        )
        self._subreddit_name = subreddit
        self._queue: asyncio.Queue = queue
        self._subreddit: reddit.Subreddit = None

    async def async_init(self) -> "SubredditMonitor":
        self._subreddit = await self._client.subreddit(
            self._subreddit_name)
        await self._subreddit.load()
        return self

    async def start(self) -> asyncio.Queue:
        ...
        asyncio.create_task(self.monitor_submissions())
        if self._mon_comments:
            asyncio.create_task(self.monitor_comments())
        return self._queue

    async def monitor_submissions(self):
        logger.debug(f'Monitoring the submissions on {self._subreddit_name}')
        while True:
            try:
                async for sub in self._subreddit.stream.submissions(skip_existing=True):
                    asyncio.create_task(self._handle_submission(sub))

            except Forbidden:
                logger.debug('Forbidden error while monitoring')

            except asyncio.TimeoutError:
                logger.debug('Timeout error while monitoring')

            except Exception as e:
                logger.info(
                    'Unhandled exception while monitoring submissions')
                logger.debug(
                    f"Exception while monitoring submissions", exc_info=True)
            finally:
                await asyncio.sleep(1)

    async def monitor_comments(self):
        logger.debug(f'Monitoring the comments on {self._subreddit_name}')
        while True:
            try:
                async for comment in self._subreddit.stream.comments(skip_existing=True):
                    asyncio.create_task(
                        self._handle_submission(comment))

            except Forbidden:
                logger.debug('Forbidden error while monitoring comments')
                await asyncio.sleep(1)

            except Exception as e:
                logger.debug(
                    'Unhandled exception while monitoring comments', exc_info=True)
                await asyncio.sleep(1)

    async def _handle_submission(self, sub: Union[reddit.Comment, reddit.Submission]):
        # logger.debug("Handling new submission.")
        await self._queue.put(sub)
