
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
            print_message(f'Changed proxy success==> success')      
        else:
            print("Countinue without proxy.")
            self.proxy=None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args, **kwargs):
        await self.close()

    async def close(self) -> None:
        if not self._session.closed:
            await self._session.close()

            
    async def exec_post(self, url,headers, data): 
        if self.proxy is None:
            async with self._session.post(url, headers=headers, json=data) as r:
                try:
                    if r.status == 200:
                        data = await r.json()
                        return data
                    else:
                        return None
                except aiohttp.ContentTypeError:
                    return None
        else:
            async with self._session.post(url, headers=headers, json=data,proxy=self.proxy) as r:
                try:
                    if r.status == 200:
                        data = await r.json()
                        return data
                    else:
                        return None
                except aiohttp.ContentTypeError:
                    return None
          
   
    async def exec_get(self, url,headers): 
        try:
            if self.proxy is None:
                async with self._session.get(url, headers=headers) as r:
                    try:
                        if r.status == 200:
                            data = await r.json()
                            return data
                        else:
                            return None
                    except aiohttp.ContentTypeError:
                        return None
            else:
                async with self._session.get(url, headers=headers,proxy=self.proxy) as r:
                    try:
                        if r.status == 200:
                            data = await r.json()
                            return data
                        else:
                            return None
                    except aiohttp.ContentTypeError:
                        return None
        except Exception as e:
            print_message(e)
                
   

