import asyncio
import pandas as pd
import requests
import requests
import json
import time
from colorama import init, Fore, Style
import sys
import os
import random

from helper.utils import print_message
init(autoreset=True)
from helper.helper_client_session import ClientSession

url_login="https://api.tapswap.ai/api/account/login"

async def exec(profile):
    profile_id=profile['id']
    async with ClientSession(proxy_url=profile['proxy']) as session:
        response =await session.exec_get(url="https://httpbin.org/ip",headers={"content-type": "application/json"})
        if response is None:
            print_message(f"❌ #{profile_id} Get new IP Failed")
            return
        profile_id=f"{profile_id}[{response['origin']}]"
        

        async def get_access_token(tao_data_dc):
            headers = {
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.9",
                "Content-Type": "application/json",
                "Connection": "keep-alive",
                "Origin": "https://app.tapswap.club",
                "Referer": "https://app.tapswap.club/",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "cross-site",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
                "sec-ch-ua": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "Windows",
                "x-app": "tapswap_server",
                "x-cv": "622",
                "x-bot": "no",
            }
            chr_value, query_id = tao_data_dc.split('|')
            payload = {
                "init_data": query_id,
                "referrer": "",
                "chr" : int(chr_value),
                "bot_key": "app_bot_1"
            }
            data = await session.exec_post(url_login, headers=headers, data=payload,log=True)
            if data is not None:
                if 'access_token' in data:
                    access_token = data['access_token']
                    name = data['player']['full_name']
                    coin = data['player']['shares']
                    energy = data['player']['energy']
                    level_energy = data['player']['energy_level']
                    level_charge = data['player']['charge_level']
                    level_tap = data['player']['tap_level']
                    boosts = data['player']['boost']
                    energy_boost = next((b for b in boosts if b["type"] == "energy"), None)
                    turbo_boost = next((b for b in boosts if b["type"] == "turbo"), None)
                    boost_ready = turbo_boost['cnt']
                    energy_ready = energy_boost['cnt']
                    return access_token, energy, boost_ready, energy_ready
            return None, None, None, None
        
        async def submit_taps(access_token, energy, boost_ready, energy_ready, content_id, time_stamp, tao_data_dc):
            global turbo_activated
            turbo_not_ready_notified = False 

            while True:
                url = "https://api.tapswap.ai/api/player/submit_taps"
                headers = {
                    "Accept": "*/*",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Authorization": f"Bearer {access_token}",
                    "Connection": "keep-alive",
                    "Content-Id": content_id,
                    "Content-Type": "application/json",
                    "Origin": "https://app.tapswap.club",
                    "Referer": "https://app.tapswap.club/",
                    "Sec-Fetch-Dest": "empty",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Site": "cross-site",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
                    "sec-ch-ua": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": "Windows",
                    "x-app": "tapswap_server",
                    "x-bot": "no",
                    "x-cv": "622",
                }
                total_taps=random.randint(50, 250)
                # total_taps = random.randint(100000, 1000000) if turbo_activated else random.randint(50, 250)
                response_data =await session.exec_post(url, headers=headers, data={"taps": total_taps, "time": int(time_stamp)})
                if response_data is not None:
                    energy_dc = response_data.get("player", {}).get("energy", 0)
                    coin_balance = response_data.get("player", {}).get("shares", 0)
                    print_message(f"✅ {profile_id} Tap thành công: balance {coin_balance} / năng lượng còn lại {energy_dc}", flush=True)
                    if energy_dc < 50:         
                        return print_message(f"❌ {profile_id} Năng lượng thấp.Move next...\n")
                else:
                    return
                
        content_id =profile['content_id']
        time_stamp = profile['time_stamp']
        chr_value = profile['chr']
        query_id = profile['query']
        tao_data_dc = chr_value + '|' + query_id
        access_token, energy, boost_ready, energy_ready =await  get_access_token(tao_data_dc.strip())
        if access_token:
            await submit_taps(access_token, energy, boost_ready, energy_ready, content_id, time_stamp, tao_data_dc.strip())


    turbo_activated = False    
    def apply_turbo_boost(access_token, proxy):
        proxies = {
            "http": f"{proxy}",
        }
        global turbo_activated
        url = "https://api.tapswap.ai/api/player/apply_boost"
        headers = {
                "Authorization": f"Bearer {access_token}",
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.9",
                "Content-Type": "application/json",
                "Connection": "keep-alive",
                "Origin": "https://app.tapswap.club",
                "Referer": "https://app.tapswap.club/",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "cross-site",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
                "sec-ch-ua": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "Windows",
                "x-app": "tapswap_server",
                "x-cv": "622",
                "x-bot": "no",
            }

        
        payload = {"type": "turbo"}
        if turbo_activated == False:
            response = requests.post(url, headers=headers, json=payload, proxies=proxies)
            if response.status_code == 201:

                print(f"\r{Fore.GREEN+Style.BRIGHT}Turbo được kích hoạt thành công", flush=True)
                turbo_activated = True
                return True

            else:
                print(f"{Fore.RED+Style.BRIGHT}Không thể kích hoạt turbo, mã trạng thái: {response.json()}")
                return False
        else:
            print(f"\r{Fore.GREEN+Style.BRIGHT}Turbo đã kích hoạt")
            return True


    not_enough_balance = {
        "tap": False,
        "energy": False,
        "charge": False
    }
    
    def upgrade_level(headers, upgrade_type, proxy):
        proxies = {
            "http": f"{proxy}",
        }
        global not_enough_balance
        if not_enough_balance[upgrade_type]:
            return False
        for i in range(5):
            print(f"\r{Fore.WHITE+Style.BRIGHT}Đang nâng cấp {upgrade_type} {'.' * (i % 4)}", end='', flush=True)
        url = "https://api.tapswap.ai/api/player/upgrade"
        payload = {"type": upgrade_type}
        response = requests.post(url, headers=headers, json=payload, proxies=proxies)
        if response.status_code == 201:
            print(f"\r{Fore.GREEN+Style.BRIGHT}Nâng cấp {upgrade_type} thành công", flush=True)
            return True
        else:
            response_json = response.json()
            if 'message' in response_json and 'not_enough_shares' in response_json['message']:
                print(f"\r{Fore.RED+Style.BRIGHT}Không đủ balance để nâng cấp {upgrade_type}", flush=True)
                not_enough_balance[upgrade_type] = True
                return False
            else:
                print(f"\r{Fore.RED+Style.BRIGHT}Lỗi khi nâng cấp {upgrade_type}: {response_json['message']}", flush=True)
            return False

    
        
async def limited_exec(semaphore, profile):
    async with semaphore:
        await exec(profile)
        
async def main(count_process,delay_time): 
    df=pd.read_excel("account.xlsx",dtype={"time":int},sheet_name='tapswap')
    df=df[(~df['query'].isna()) & (df['query']!='')]
    if "proxy" not in df.columns:
            df["proxy"] = ""
    df['proxy']=df['proxy'].fillna('')
    
    profiles=[]
    for idx,row in df.iterrows():
        profile={
            "id":idx+1,
            "query":row["query"],
            "content_id":str(row["content_id"]),
            "chr":str(row["chr"]),
            "time_stamp":str(row["time_stamp"]),
            "proxy":row["proxy"]
        }
        profiles.append(profile)
        
    semaphore = asyncio.Semaphore(count_process)  # Limit to 5 concurrent tasks
    tasks = [limited_exec(semaphore, profile) for profile in profiles]
    await asyncio.gather(*tasks)
    for __second in range(delay_time, 0, -1):
        sys.stdout.write(f"\r{Fore.CYAN}Chờ thời gian nhận tiếp theo trong {Fore.CYAN}{Fore.WHITE}{__second // 60} phút {Fore.WHITE}{__second % 60} giây")
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write("\rĐã đến thời gian nhận tiếp theo!\n")

if __name__=="__main__":
    count_process=int(input("Nhập số luồng xử lý:"))
    delay_time=int(input("Nhập thời gian dừng(theo phút):"))
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    while True:
        asyncio.run(main(count_process,delay_time*60))
        
        


