from twocaptcha import TwoCaptcha
import asyncio


class Solver:
    def __init__(self, api_key: str, site_key: str = None):
        self.site_key = site_key
        self._api_key = api_key
        self._solver = TwoCaptcha(self._api_key)

    async def get_recaptcha_code(self, site_key: str = None, page_url: str = None):
        site_key = site_key or self.site_key
        if page_url is None:
            page_url = "https://twitter.com/login"

        def code():
            code = self._solver.recaptcha(site_key, page_url)
            return code["code"]

        loop = asyncio.get_event_loop()
        task = loop.run_in_executor(None, lambda: code())
        while not task.done():
            # print("Not done yet")
            await asyncio.sleep(1)
        return task.result()
