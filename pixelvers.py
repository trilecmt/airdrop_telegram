import io
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
PET={
    "1":"0a6306e5-cc33-401a-9664-a872e3eb2b71",
    "2":"571523ae-872d-49f0-aa71-53d4a41cd810",
    "3":"78e0146f-0dfb-4af8-a48d-4033d3efdd39",
    "4":"7c3a95c6-75a3-4c62-a20e-896a21132060",
    "5":"8074e9c5-f6c2-4012-bfa2-bcc98ceb5175",
    "6":"d364254e-f22f-4a43-9a1c-5a7c71ea9ecd",
    "7":"dc5236dc-06be-456b-a311-cccedbd213ca",
    "8":"e8c505ed-df93-47e0-bd2e-0e664d09ba86",
    "9":"ef0adeca-be18-4503-9e9a-d93c22bd7a6e",
    "10":"f097634a-c8e8-4de9-b707-575d20c5fd88",
    "11":"50e9e942-36d5-4f19-9bb7-c892cb956fff",
    "12":"7ee9ed52-c808-4187-a942-b53d972cd399",
    "13":"36621a17-81f3-4d5d-b4e1-4b0cf51d4610",
    "14":"90a07a32-431a-4299-be59-598180ee4a8c",
    "15":"45f2e16e-fb64-4e15-a3fa-2fb99c8d4a04",
    "16":"3bfab57c-a57f-48d9-8819-c93c9f531478",
    "17":"341195b4-f7d8-4b9c-a8f1-448318f32e8e",
    "18":"bc3f938f-8f4c-467b-a57d-2b40cd500f4b",
    "19":"f82a3b59-913d-4c57-8ffd-9ac954105e2d",
    "20":"d59cd843-1b53-4131-9966-641d41aa634b",
}


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
    def __init__(self,proxies,profile_name):
        self.profile_name=profile_name
        self.session=requests.Session()
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

    def process_account(self, data, id_pets:list):
        self.get_me(data)
        self.daily_reward(data)
        self.get_mining_proccess(data)
        self.auto_buy_pet(data)
        self.auto_upgrade_pet(data)
        if id_pets is not None and len(id_pets)==4:
             self.daily_combo(data, id_pets)
            
    def api_call(self, url, data=None, headers=None, method='GET'): 
        for i in range(5):
            try:
                if method == 'GET':
                    if self.proxies is not None:
                        res = self.session.get(url, headers=headers,proxies=self.proxies)
                    else:
                        res =self.session.get(url, headers=headers)
                elif method == 'POST':
                    if self.proxies is not None:
                        res =self.session.post(url, headers=headers, data=data,proxies=self.proxies)
                    else:
                        res =self.session.post(url, headers=headers, data=data)
                else:
                    raise ValueError(f'Unsupported method: {method}')
                
                if res.status_code == 401:
                    self.log(f'{merah}{res.text}')

                open('.http.log', 'a', encoding='utf-8').write(f'{res.text}\n')
                return res
            except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout, requests.exceptions.Timeout):
                self.log(f'{merah}Connection error / connection timeout !')
                continue

    def get_me(self, data: Data):
        url = 'https://api-clicker.pixelverse.xyz/api/users'
        headers = self.prepare_headers(data)
        res =  self.api_call(url, None, headers)
        if res.status_code not in [200,201]:
            return
        data= res.json()
        balance = data.get('clicksCount', 'N/A')
        self.log(f'{hijau}Total Balance : {putih}{balance}')

    def daily_reward(self, data: Data):
        url = 'https://api-clicker.pixelverse.xyz/api/daily-rewards'
        headers = self.prepare_headers(data)
        res = self.api_call(url, None, headers)
        if res.status_code not in [200,201]:
            return
        data= res.json()
        if data.get('todaysRewardAvailable'):
            url_claim = 'https://api-clicker.pixelverse.xyz/api/daily-rewards/claim'
            res = self.api_call(url_claim, '', headers, method='POST')
            if res.status_code not in [200,201]:
                return
            data= res.json()
            amount = data.get('amount', 'N/A')
            self.log(f'{hijau}Success claim today reward : {putih}{amount}')
        else:
            self.log(f'{kuning}Already claim today reward !')

    def get_mining_proccess(self, data: Data):
        url = "https://api-clicker.pixelverse.xyz/api/mining/progress"
        headers = self.prepare_headers(data)
        res = self.api_call(url, None, headers)
        
        if res.status_code  in [200,201]:
            try:
                response_json = res.json()
            except json.JSONDecodeError:
                self.log(f'{merah}Failed to decode JSON response.')
                return
            
            available = response_json.get('currentlyAvailable', 0)
            min_claim = response_json.get('minAmountForClaim', float('inf'))
            self.log(f'{putih}Amount available : {hijau}{available}')
            
            if available > min_claim:
                url_claim = 'https://api-clicker.pixelverse.xyz/api/mining/claim'
                res = self.api_call(url_claim, '', headers, method='POST')
                if res.status_code in [200,201]:
                    try:
                        claim_response = res.json()
                    except json.JSONDecodeError:
                        self.log(f'{merah}Failed to decode JSON response.')
                        return
                    
                    claim_amount = claim_response.get('claimedAmount', 'N/A')
                    self.log(f'{hijau}Claim amount : {putih}{claim_amount}')
                else:
                    self.log(f'{merah}Empty response from claim API. {res.status_code}')
            else:
                self.log(f'{kuning}Amount too small to make claim !')
        else:
            self.log(f'{merah}Empty response from mining progress API.')

    def auto_buy_pet(self, data: Data):
        url = 'https://api-clicker.pixelverse.xyz/api/pets/buy?tg-id={self.tg_id}&secret={self.secret}'
        headers = self.prepare_headers(data)
        res_buy_pet = self.api_call(url, data=json.dumps({}), headers=headers, method='POST')
        if res_buy_pet.status_code == 200 or res_buy_pet.status_code == 201:
            try:
                buy_pet_data = res_buy_pet.json()
                pet_name = buy_pet_data.get('pet', {}).get('name', 'Unknown')
                self.log(f'{hijau}Successfully buy a new pet! You got {kuning}{pet_name}!')
            except json.JSONDecodeError:
                self.log(f'{merah}Failed to decode JSON response from buy pet API.')
        else:
            self.log(f'{merah}Not yet time to buy another pet or Insufficient points')

    def auto_upgrade_pet(self, data: Data):
        url = 'https://api-clicker.pixelverse.xyz/api/pets'
        headers = self.prepare_headers(data)
        res = self.api_call(url, None, headers)
        if res.status_code not in [200,201]:
            return
        data=  res.json()
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
                res_upgrade = self.api_call(url_upgrade, '', headers, method='POST')
                if res_upgrade.status_code == 200 or res_upgrade.status_code == 201:
                    self.log(f'{hijau}Success Upgrading Pet! Pet ID: {putih}{pet_id} ({pet_name})')
                else:
                    data= res_upgrade.json()
                    error_message = data.get('message', 'Unknown error')
                    self.log(f'{merah}Failed to Upgrade Pet! Pet ID: {putih}{pet_id}, {merah}Error: {error_message}')
        else:
            self.log(f'{kuning}No Pets Available for Upgrade')

    def daily_combo(self, data: Data, id_pets):
        url_current_game = "https://api-clicker.pixelverse.xyz/api/cypher-games/current"
        headers = self.prepare_headers(data)
        res_current_game = self.api_call(url_current_game, None, headers)
        
        if res_current_game.status_code  in [200,201]:
            try:
                game_data = res_current_game.json()
            except json.JSONDecodeError:
                self.log(f'{merah}Failed to decode JSON response from current game API.')
                return

            if game_data['status'] == "ACTIVE":
                game_id = game_data.get('id')
                available_options = game_data.get('options', [])
                pet_id_index_map = {option["optionId"]: len(available_options) - option["order"] - 1 for option in available_options}

                id_pets = [pet_id.strip() for pet_id in id_pets]
                payload = {pet_id: len(id_pets) - id_pets.index(pet_id) - 1 for pet_id in id_pets}

                url_answer = f"https://api-clicker.pixelverse.xyz/api/cypher-games/{game_id}/answer"
                headers['Content-Type'] = 'application/json'
                res_answer = self.api_call(url_answer, data=json.dumps(payload), headers=headers, method='POST')

                if res_answer.status_code == 200 or res_answer.status_code == 201:
                    try:
                        answer_data = res_answer.json()
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
        print(f"{hitam}[{now}]{reset} {self.profile_name}{message}")


def exec(profile):
    try:
        app = PixelTod(utils.get_proxies(profile['proxy'],type=1),profile_name=profile['name'])
        print_message(f"✅ #{profile['name']} Bắt đầu")
        response = app.api_call(url="https://httpbin.org/ip",headers={"content-type": "application/json"})
        if response.status_code!=200:
            return print_message(f"❌ #{profile['name']} Proxy không lấy được IP")
        data= response.json()
        app.profile_id=f"{profile['name']}[{data['origin']}]"   
        data_parse = app.data_parsing(profile['query'])
        user = json.loads(data_parse['user'])
        userid = str(user['id'])
        username = user.get('username')
        secret = app.get_secret(userid)
        new_data = Data(profile['query'], userid, username, secret)
        app.process_account(new_data, profile['daily_combo'])

    except Exception as e:
          print_message(f"❌ Lỗi khi xử lí profile {profile['name']}")
          print_message(traceback.format_exc())
    finally:
        print_message(f"✅ #{profile['name']} Kết thúc.Move next")

def limited_exec(semaphore, profile):
     with semaphore:
         exec(profile)

def main(delay):
    try:
        code=utils.get_daily_code()
        uid_codes=None
        if code is not None:
            vectors=code.get("comboPixel",None)   
            if vectors is not None:
                uid_codes=[PET[code] for code in str(vectors).split(",")]
        df=pd.read_excel("account.xlsx",dtype={"query":str,"profile":str},sheet_name='pixelvers')
        df=df[(~df['query'].isna()) & (df['query']!='')]
        for col in ['proxy']:
            if col not in df.columns:
                df[col] = ""
            df[col]=df[col].fillna('')
        for idx,row in df.iterrows():
            profile={
                "id":idx+1,
                "name":row['profile'],
                "query":row["query"],
                "proxy":row["proxy"],
                "daily_combo":uid_codes
            }
            exec(profile)
        #     profiles.append(profile)
        # semaphore = io.Semaphore(count_process)  # Limit to 5 concurrent tasks
        # tasks = [limited_exec(semaphore, profile) for profile in profiles]
        #  io.gather(*tasks)
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
            main(delay)     
        except Exception as e:
            print_message(traceback.format_exc())

        
                
        
        
            