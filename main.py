import asyncio
from app import logger
import config
from app.reddit_monitor import SubredditMonitor
from tweety import Client
from app.tweet import tweet_thread_poster


async def main():
    logger.info(f"Starting the app.")
    twitter_client = await Client(
        email=config.TWITTER_EMAIL,
        password=config.TWITTER_PASSWORD,
        username=config.TWITTER_USERNAME,
        phone=config.TWITTER_PHONE,
        captcha_api_key=config.CAPTCHA_API_KEY
    ).async_init()
    if not twitter_client.logged_in:
        try:
            await twitter_client.login()
        except Exception as e:
            logger.debug(f"Login failed", exc_info=True)
            logger.info(f"Error while login to Twitter.")
            return await twitter_client.close()
    logger.info(f"Logged in as {twitter_client.user}")
    output_queue = asyncio.Queue()
    subreddit_monitor = await SubredditMonitor(config.TARGET_SUBREDDIT,
                                               output_queue,
                                               config.REDDIT_CLIENT_ID,
                                               config.REDDIT_CLIENT_SECRET,
                                               config.REDDIT_USER_AGENT).async_init()

    asyncio.create_task(subreddit_monitor.start())

    while True:
        submission = await output_queue.get()
        logger.debug(f"Got a new submission from queue {submission}")
        asyncio.create_task(tweet_thread_poster(twitter_client, submission))
        


if __name__ == "__main__":
    asyncio.run(main())
