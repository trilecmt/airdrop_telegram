import asyncio
import os
import sys
import json
import time
import hmac
import hashlib
import traceback
import aiohttp
import pandas as pd
import requests
from datetime import datetime
from colorama import *
from urllib.parse import unquote
from colorama import init, Fore, Style

from helper import utils
from helper.helper_session import MySession
from helper.utils import print_message
init(autoreset=True)

GAME='PIXELVERS'

from helper.helper_schedule import ScheduleDB
schedule=ScheduleDB()

merah = Fore.LIGHTRED_EX
hijau = Fore.LIGHTGREEN_EX
kuning = Fore.LIGHTYELLOW_EX
biru = Fore.LIGHTBLUE_EX
hitam = Fore.LIGHTBLACK_EX
reset = Style.RESET_ALL
putih = Fore.LIGHTWHITE_EX

class Data:
    def __init__(self, init_data, userid, username, secret):
        self.init_data = init_data
        self.userid = userid
        self.username = username
        self.secret = secret

class PixelTod:
    def __init__(self,proxies):
        self.proxies=proxies
        self.DEFAULT_COUNTDOWN = 10 * 60  # 5 minutes
        self.INTERVAL_DELAY = 3  # seconds
        self.base_headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en,en-US;q=0.9",
            "Host": "api-clicker.pixelverse.xyz",
            "X-Requested-With": "org.telegram.messenger",
            'origin': 'https://sexyzbot.pxlvrs.io/',
            'referer': 'https://sexyzbot.pxlvrs.io/',
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        }

    def get_secret(self, userid):
        rawr = "adwawdasfajfklasjglrejnoierjboivrevioreboidwa"
        secret = hmac.new(rawr.encode("utf-8"), str(userid).encode("utf-8"), hashlib.sha256).hexdigest()
        return secret

    def data_parsing(self, data):
        return {key: value for key, value in (i.split('=') for i in unquote(data).split('&'))}

    async def process_account(self, data, id_pets:str):
        await self.get_me(data)
        await self.daily_reward(data)
        await self.get_mining_proccess(data)
        await self.auto_buy_pet(data)
        await self.auto_upgrade_pet(data)
        if id_pets!="":
            await self.daily_combo(data, id_pets)
            
    async def api_call(self, url, data=None, headers=None, method='GET'):
        async with aiohttp.ClientSession() as session:
            for i in range(5):
                try:
                    if method == 'GET':
                        if self.proxies is not None:
                            res =await session.get(url, headers=headers,proxy=self.proxies)
                        else:
                            res =await session.get(url, headers=headers)
                    elif method == 'POST':
                        if self.proxies is not None:
                            res =await session.post(url, headers=headers, data=data,proxy=self.proxies)
                        else:
                            res =await session.post(url, headers=headers, data=data)
                    else:
                        raise ValueError(f'Unsupported method: {method}')
                    
                    if res.status == 401:
                        self.log(f'{merah}{res.text}')

                    open('.http.log', 'a', encoding='utf-8').write(f'{res.text}\n')
                    return res
                except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout, requests.exceptions.Timeout):
                    self.log(f'{merah}Connection error / connection timeout !')
                    continue

    async def get_me(self, data: Data):
        url = 'https://api-clicker.pixelverse.xyz/api/users'
        headers = self.prepare_headers(data)
        res = await self.api_call(url, None, headers)
        if res.status not in [200,201]:
            return
        data=await res.json()
        balance = data.get('clicksCount', 'N/A')
        self.log(f'{hijau}Total Balance : {putih}{balance}')

    async def daily_reward(self, data: Data):
        url = 'https://api-clicker.pixelverse.xyz/api/daily-rewards'
        headers = self.prepare_headers(data)
        res =await self.api_call(url, None, headers)
        if res.status not in [200,201]:
            return
        data=await res.json()
        if data.get('todaysRewardAvailable'):
            url_claim = 'https://api-clicker.pixelverse.xyz/api/daily-rewards/claim'
            res =await self.api_call(url_claim, '', headers, method='POST')
            if res.status not in [200,201]:
                return
            data=await res.json()
            amount = data.get('amount', 'N/A')
            self.log(f'{hijau}Success claim today reward : {putih}{amount}')
        else:
            self.log(f'{kuning}Already claim today reward !')

    async def get_mining_proccess(self, data: Data):
        url = "https://api-clicker.pixelverse.xyz/api/mining/progress"
        headers = self.prepare_headers(data)
        res =await self.api_call(url, None, headers)
        
        if res.status  in [200,201]:
            try:
                response_json =await res.json()
            except json.JSONDecodeError:
                self.log(f'{merah}Failed to decode JSON response.')
                return
            
            available = response_json.get('currentlyAvailable', 0)
            min_claim = response_json.get('minAmountForClaim', float('inf'))
            self.log(f'{putih}Amount available : {hijau}{available}')
            
            if available > min_claim:
                url_claim = 'https://api-clicker.pixelverse.xyz/api/mining/claim'
                res =await self.api_call(url_claim, '', headers, method='POST')
                if res.status in [200,201]:
                    try:
                        claim_response =await res.json()
                    except json.JSONDecodeError:
                        self.log(f'{merah}Failed to decode JSON response.')
                        return
                    
                    claim_amount = claim_response.get('claimedAmount', 'N/A')
                    self.log(f'{hijau}Claim amount : {putih}{claim_amount}')
                else:
                    self.log(f'{merah}Empty response from claim API.')
            else:
                self.log(f'{kuning}Amount too small to make claim !')
        else:
            self.log(f'{merah}Empty response from mining progress API.')

    async def auto_buy_pet(self, data: Data):
        url = 'https://api-clicker.pixelverse.xyz/api/pets/buy?tg-id={self.tg_id}&secret={self.secret}'
        headers = self.prepare_headers(data)
        res_buy_pet =await self.api_call(url, data=json.dumps({}), headers=headers, method='POST')
        if res_buy_pet.status == 200 or res_buy_pet.status == 201:
            try:
                buy_pet_data =await res_buy_pet.json()
                pet_name = buy_pet_data.get('pet', {}).get('name', 'Unknown')
                self.log(f'{hijau}Successfully buy a new pet! You got {kuning}{pet_name}!')
            except json.JSONDecodeError:
                self.log(f'{merah}Failed to decode JSON response from buy pet API.')
        else:
            self.log(f'{merah}Not yet time to buy another pet or Insufficient points')

    async def auto_upgrade_pet(self, data: Data):
        url = 'https://api-clicker.pixelverse.xyz/api/pets'
        headers = self.prepare_headers(data)
        res =await self.api_call(url, None, headers)
        if res.status not in [200,201]:
            return
        data= await res.json()
        pets = data.get('data', [])
        if pets:
            pets_info = ', '.join([f'{pet["name"].strip()} Lv.{pet["userPet"]["level"]}' for pet in pets])
            self.log(f'{hijau}Success Getting Pet List: {pets_info}')
            for pet in pets:
                pet_name = pet["name"].strip()
                pet_level = pet["userPet"]["level"]
                pet_id = pet['userPet']['id']
                self.log(f'{putih}Selecting Pet ID: {hijau}{pet_id} ({pet_name} Lv.{pet_level})')
                url_upgrade = f'https://api-clicker.pixelverse.xyz/api/pets/user-pets/{pet_id}/level-up'
                res_upgrade =await self.api_call(url_upgrade, '', headers, method='POST')
                if res_upgrade.status == 200 or res_upgrade.status == 201:
                    self.log(f'{hijau}Success Upgrading Pet! Pet ID: {putih}{pet_id} ({pet_name})')
                else:
                    data=await res_upgrade.json()
                    error_message = data.get('message', 'Unknown error')
                    self.log(f'{merah}Failed to Upgrade Pet! Pet ID: {putih}{pet_id}, {merah}Error: {error_message}')
        else:
            self.log(f'{kuning}No Pets Available for Upgrade')

    async def daily_combo(self, data: Data, id_pets):
        url_current_game = "https://api-clicker.pixelverse.xyz/api/cypher-games/current"
        headers = self.prepare_headers(data)
        res_current_game =await self.api_call(url_current_game, None, headers)
        
        if res_current_game.status  in [200,201]:
            try:
                game_data =await res_current_game.json()
            except json.JSONDecodeError:
                self.log(f'{merah}Failed to decode JSON response from current game API.')
                return

            if game_data['status'] == "ACTIVE":
                game_id = game_data.get('id')
                available_options = game_data.get('options', [])
                pet_id_index_map = {option["optionId"]: len(available_options) - option["order"] - 1 for option in available_options}

                id_pets = [pet_id.strip() for pet_id in id_pets.split(",")]
                payload = {pet_id: len(id_pets) - id_pets.index(pet_id) - 1 for pet_id in id_pets}

                url_answer = f"https://api-clicker.pixelverse.xyz/api/cypher-games/{game_id}/answer"
                headers['Content-Type'] = 'application/json'
                res_answer =await self.api_call(url_answer, data=json.dumps(payload), headers=headers, method='POST')

                if res_answer.status == 200 or res_answer.status == 201:
                    try:
                        answer_data =await res_answer.json()
                        reward_amount = answer_data.get('rewardAmount', 'N/A')
                        self.log(f'{hijau}Successfully submitted the daily combo! Reward Amount: {reward_amount}')
                    except json.JSONDecodeError:
                        self.log(f'{merah}Failed to decode JSON response from answer API.')
                else:
                    self.log(f'{merah}Failed to submit the daily combo. {res_answer.text}')
            else:
                self.log(f'{kuning}Daily Combo already claimed!')
        else:
            self.log(f'{merah}Daily Combo Already Claimed!')

    def prepare_headers(self, data: Data):
        headers = self.base_headers.copy()
        headers.update({
            'initData': data.init_data,
            'secret': data.secret,
            'tg-id': data.userid
        })
        if data.username:
            headers['username'] = data.username
        return headers

    def log(self, message):
        now = datetime.now().isoformat(" ").split(".")[0]
        print(f"{hitam}[{now}]{reset} {self.profile_id}{message}")


async def exec(profile):
    try:
        app = PixelTod(utils.get_proxies(profile['proxy'],type=0))
        response =await app.api_call(url="https://httpbin.org/ip",headers={"content-type": "application/json"})
        if response.status!=200:
            return print_message(f"❌ #{profile['name']} Proxy không lấy được IP")
        data=await response.json()
        app.profile_id=f"{profile["name"]}[{data['origin']}]"   
        data_parse = app.data_parsing(profile['query'])
        user = json.loads(data_parse['user'])
        userid = str(user['id'])
        username = user.get('username')
        secret = app.get_secret(userid)
        new_data = Data(profile['query'], userid, username, secret)
        await app.process_account(new_data, profile['daily_combo'])

    except Exception as e:
          print_message(f"❌ Lỗi khi xử lí profile {profile['name']}")
          print_message(traceback.format_exc())
    finally:
        print_message(f"✅ #{profile['name']} Kết thúc.Move next")

async def limited_exec(semaphore, profile):
    async with semaphore:
        await exec(profile)

async def main(delay):
    try:
        df=pd.read_excel("account.xlsx",dtype={"query":str,"profile":str,"daily_combo":str},sheet_name='pixelvers')
        df=df[(~df['query'].isna()) & (df['query']!='')]
        for col in ['proxy','daily_combo']:
            if col not in df.columns:
                df[col] = ""
            df[col]=df[col].fillna('')
        daily_combo=df["daily_combo"].iat[0]
        profiles=[]
        for idx,row in df.iterrows():
            profile={
                "id":idx+1,
                "name":row['profile'],
                "query":row["query"],
                "proxy":row["proxy"],
                "daily_combo":daily_combo
            }
            await exec(profile)
        #     profiles.append(profile)
        # semaphore = asyncio.Semaphore(count_process)  # Limit to 5 concurrent tasks
        # tasks = [limited_exec(semaphore, profile) for profile in profiles]
        # await asyncio.gather(*tasks)
        for __second in range(delay*60, 0, -1):
            sys.stdout.write(f"\r{Fore.CYAN}Chờ thời gian nhận tiếp theo trong {Fore.CYAN}{Fore.WHITE}{__second // 60} phút {Fore.WHITE}{__second % 60} giây")
            sys.stdout.flush()
            time.sleep(1)

    except KeyboardInterrupt:
        sys.exit()
    except Exception as e:    
        print_message(traceback.format_exc())

if __name__ == "__main__":
    # count_process=int(input("Nhập số CPU:"))
    delay=int(input("Nhập thời gian nghỉ(phút):"))
    while True:
        try:
          asyncio.run(main(delay))        
        except Exception as e:
            print_message(traceback.format_exc())

        
                
        
        
            