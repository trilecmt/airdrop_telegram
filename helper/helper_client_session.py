
import random
import re
import requests
import time
import datetime
import json
from helper.utils import print_message
import aiohttp
import asyncio

class ClientSession:
    def __init__(self,proxy_url=None) -> None:
        self._session = aiohttp.ClientSession()
        if proxy_url is not None and proxy_url!='':  
            if not proxy_url.startswith("http"):
                if len(proxy_url.split(":"))==2:       
                    host=proxy_url.split(":")[0]
                    port=proxy_url.split(":")[1]
                    proxy_url=f'http://{host}:{port}'
                else:
                    username=proxy_url.split(":")[2]
                    password=proxy_url.split(":")[3]
                    host=proxy_url.split(":")[0]
                    port=proxy_url.split(":")[1]
                    proxy_url=f'http://{username}:{password}@{host}:{port}'
            self.proxy=proxy_url# {'http':proxy_url,'https':proxy_url}     
        else:
            self.proxy=None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args, **kwargs):
        await self.close()

    async def close(self) -> None:
        if not self._session.closed:
            await self._session.close()

            
    async def exec_post(self, url,headers, data,retry_count=1,log=False): 
        for i in range(retry_count):
            if self.proxy is None:
                async with self._session.post(url, headers=headers, json=data) as r:
                    try:
                        if r.status in [200,201]:
                            data = await r.json()
                            return data
                        else:
                            if log:
                                print_message(f'Status: {r.status}')
                                print_message(f'Status: {r.text}')
                    except aiohttp.ContentTypeError:
                        pass
            else:
                async with self._session.post(url, headers=headers, json=data,proxy=self.proxy) as r:
                    try:
                        if r.status in [200,201]:
                            data = await r.json()
                            return data
                        else:
                            if log:
                                print_message(f'Status: {r.status}')
                                print_message(f'Status: {r.text}')
                    except aiohttp.ContentTypeError:
                        pass
                        
          
   
    async def exec_get(self, url,headers,retry_count=1,log=False): 
        for i in range(retry_count):
            try:
                if self.proxy is None:
                    async with self._session.get(url, headers=headers) as r:
                        try:
                            if r.status in [200,201]:
                                data = await r.json()
                                return data
                            else:
                                pass
                        except aiohttp.ContentTypeError:
                            pass
                else:
                    async with self._session.get(url, headers=headers,proxy=self.proxy) as r:
                        try:
                            if r.status in [200,201]:
                                data = await r.json()
                                return data
                            else:
                                pass
                        except aiohttp.ContentTypeError:
                            pass
            except Exception as e:
                print_message(e)
                    
   

