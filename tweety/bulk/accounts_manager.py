
from ..api import Client
from typing import *
import asyncio


class AccountsManager:
    def __init__(self,
                 accounts_file: str,
                 captcha_key: str = None,
                 login_threads: int = 10):
        self._accounts_file = accounts_file
        self._captcha_key = captcha_key
        self._login_threads = login_threads
        self._all_clients: List[Client] = []
        self._logged_in_clients: List[Client] = []

    async def login_accounts_async(self):
        """Login all the accounts"""
        for client in self._all_clients:
            client = await client.async_init()
            if not client.logged_in:
                try:
                    await client.login()
                except Exception as e:
                    print(f"Could not login account because {e}")
                    await client.close()
                    continue
            if client.logged_in:
                self._logged_in_clients.append(client)

    async def login_accounts_async(self):
        semaphore = asyncio.Semaphore(self._login_threads)
        tasks = []

        async def _login(client: Client):
            client = await client.async_init()
            if not client.logged_in:
                try:
                    async with semaphore:
                        await client.login()
                except Exception as e:
                    print(f"Could not login account because {e}")
                    await client.close()
            if client.logged_in:
                self._logged_in_clients.append(client)

        for client in self._all_clients:
            tasks.append(asyncio.create_task(_login(client)))
        await asyncio.gather(*tasks)

    async def close_clients(self):
        """Close all the sessions"""
        tasks = []
        for client in self._logged_in_clients:
            tasks.append(asyncio.create_task(client.close()))
        await asyncio.gather(*tasks)

    def read_format1(self):
        """FORMAT1: username:password:email"""
        lines = open(self._accounts_file, 'r').readlines()
        for line in lines:
            username = line.split(":")[0].strip()
            password = line.split(":")[1].strip()
            email = line.split(":")[2].strip()
            client = Client(username=username, password=password,
                            email=email, captcha_api_key=self._captcha_key)
            client.raw_info = line
            self._all_clients.append(client)

    def read_format2(self):
        """FORMAT2: email:password:phone"""
        lines = open(self._accounts_file, 'r').readlines()
        for line in lines:
            email = line.split(":")[0].strip()
            password = line.split(":")[1].strip()
            phone = line.split(":")[2].strip()
            client = Client(password=password,
                            email=email,
                            phone=phone,
                            captcha_api_key=self._captcha_key)
            client.raw_info = line
            self._all_clients.append(client)

    def read_format3(self):
        """FORMAT3: username:password:phone:email"""
        lines = open(self._accounts_file, 'r').readlines()
        for line in lines:
            username = line.split(":")[0].strip()
            password = line.split(":")[1].strip()
            phone = line.split(":")[2].strip()
            email = line.split(":")[3].strip()
            client = Client(username=username,
                            password=password,
                            email=email,
                            phone=phone,
                            captcha_api_key=self._captcha_key)
            client.raw_info = line
            self._all_clients.append(client)

    def read_format4(self):
        lines = open(self._accounts_file, 'r').readlines()
        for line in lines:
            username = line.split(":")[0].strip()
            password = line.split(":")[1].strip()
            phone = line.split(":")[2].strip()
            client = Client(username=username,
                            password=password,
                            phone=phone,
                            captcha_api_key=self._captcha_key)
            client.raw_info = line
            self._all_clients.append(client)


class AccountsManager:
    def __init__(self, accounts_file: str, captcha_key: str = None):
        self._accounts_file = accounts_file
        self._captcha_key = captcha_key
        self._all_clients: List[Client] = []
        self._logged_in_clients: List[Client] = []

    async def login_accounts_sync(self):
        """Login all the accounts"""
        for client in self._all_clients:
            client = await client.async_init()
            if not client.logged_in:
                try:
                    await client.login()
                except Exception as e:
                    print(f"Could not login account because {e}")
                    await client.close()
                    continue
            if client.logged_in:
                self._logged_in_clients.append(client)

    async def close_clients(self):
        """Close all the sessions"""
        tasks = []
        for client in self._logged_in_clients:
            tasks.append(asyncio.create_task(client.close()))
        await asyncio.gather(*tasks)

    def read_format1(self):
        """FORMAT1: username:password:email"""
        lines = open(self._accounts_file, 'r').readlines()
        for line in lines:
            username = line.split(":")[0].strip()
            password = line.split(":")[1].strip()
            email = line.split(":")[2].strip()
            client = Client(username=username, password=password,
                            email=email, captcha_api_key=self._captcha_key)
            client.raw_info = line
            self._all_clients.append(client)

    def read_format2(self):
        """FORMAT2: email:password:phone"""
        lines = open(self._accounts_file, 'r').readlines()
        for line in lines:
            email = line.split(":")[0].strip()
            password = line.split(":")[1].strip()
            phone = line.split(":")[2].strip()
            client = Client(password=password,
                            email=email,
                            phone=phone,
                            captcha_api_key=self._captcha_key)
            client.raw_info = line
            self._all_clients.append(client)

    def read_format3(self):
        """FORMAT3: username:password:phone:email"""
        lines = open(self._accounts_file, 'r').readlines()
        for line in lines:
            username = line.split(":")[0].strip()
            password = line.split(":")[1].strip()
            phone = line.split(":")[2].strip()
            email = line.split(":")[3].strip()
            client = Client(username=username,
                            password=password,
                            email=email,
                            phone=phone,
                            captcha_api_key=self._captcha_key)
            client.raw_info = line
            self._all_clients.append(client)

    def read_format4(self):
        lines = open(self._accounts_file, 'r').readlines()
        for line in lines:
            username = line.split(":")[0].strip()
            password = line.split(":")[1].strip()
            phone = line.split(":")[2].strip()
            client = Client(username=username,
                            password=password,
                            phone=phone,
                            captcha_api_key=self._captcha_key)
            client.raw_info = line
            self._all_clients.append(client)
