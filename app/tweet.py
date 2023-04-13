from csv import excel
import os
from tweety import Client
from typing import *
import asyncio
from asyncpraw.models import Submission
from app import logger
from pprint import pprint
import config
from tweety import models
import aiohttp
import aiofiles
from app import gvs


async def download_image(url: str, filename: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                f = await aiofiles.open(filename, mode='wb')
                await f.write(await resp.read())
                await f.close()

    return filename


def subbody_to_texts(body: str, max_length: int):
    texts = []
    sentences = body.split(".")
    text = ""
    for sentence in sentences:
        if len(text) + len(sentence) < max_length:
            text = f"{text} {sentence.strip()}."
            continue
        texts.append(text.strip())
        text = ""
    if text.strip() != "":
        texts.append(text.strip())
    return texts


# async def get_images(url: str):
#     gallery_url = 'https://www.reddit.com/r/announcements/comments/hrrh23/now_you_can_make_posts_with_multiple_images/'
#     submission = reddit.submission(url=gallery_url)
#     image_dict = submission.media_metadata
#     for image_item in image_dict.values():
#         largest_image = image_item['s']
#         image_url = largest_image['u']
#         print(image_url)


async def tweet_thread_poster(client: Client, submission: Submission):
    await submission.load()
    logger.info(f"Posting tweets thread...")
    if submission.selftext.strip() == "":
        texts = [submission.title]
    else:
        texts = subbody_to_texts(submission.selftext, 280)
    image_link = str(submission.url)
    if "/comments" in image_link:
        image_location = None
    else:
        # Download the image from submission
        image_location = f"{gvs.DOWNLOADS_FOLDER}/{image_link.split('/')[-1]}"
        try:
            logger.info(f"Downloading image {image_link} ...")
            await download_image(image_link, image_location)
        except Exception:
            logger.error(f"Failed to download image {image_link}")
            image_location = None
    first_tweet_id = None
    logger.info(f"Posting {len(texts)} tweets in thread...")
    for i, text in enumerate(texts):
        posted = await client.post_tweet(text, in_reply_to_tweet_id=first_tweet_id, images_locations=image_location)
        if isinstance(posted, models.Tweet):
            logger.info(f"Posted tweet {i+1} with ID {posted.id}")
        else:
            logger.error(f"Failed to post the tweet.")
            logger.debug(f"Failed to post tweet: {posted}")
            await asyncio.sleep(3)
            continue
        try:
            os.remove(image_location)
        except:
            pass
        if first_tweet_id is None:
            first_tweet_id = posted.id
        await asyncio.sleep(1)
    logger.info(f"Tweets thread posted!")
