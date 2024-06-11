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
    content_id =profile['content_id']
    time_stamp = profile['time_stamp']
    chr_value = profile['chr']
    query_id = profile['query']
    tap_level=profile['tap_level']
    energy_level=profile['energy_level']
    
    async with ClientSession(proxy_url=profile['proxy']) as session:
        response =await session.exec_get(url="https://httpbin.org/ip",headers={"content-type": "application/json"})
        if response is None:
            print_message(f"❌ #{profile_id} Get new IP Failed")
            return
        profile_id=f"{profile_id}[{response['origin']}]"
        
        headers = {
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.9",
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
        
        async def upgrade_level(upgrade_type):
            url = "https://api.tapswap.ai/api/player/upgrade"
            payload = {"type": upgrade_type}
            response = await session.exec_post(url, headers=headers, data=payload)
            return response is not None
        
        async def buy_boost(boost_type):
            url = "https://api.tapswap.ai/api/player/apply_boost"
            payload = {"type": boost_type}
            response =await session.exec_post(url, headers=headers, data=payload)
            return response
            
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
        
        async def submit_taps(tap_level,energy_limit, energy, boost_ready, energy_ready, content_id, time_stamp, tao_data_dc):
            global turbo_activated
            is_checked_multitap=False
            is_checked_energy_limit=False
            is_checked_charge_level=False

            async def __tap(total_taps):
                url = "https://api.tapswap.ai/api/player/submit_taps"
                response_data =await session.exec_post(url, headers=headers, data={"taps": total_taps, "time": int(time_stamp)},log=True)
                if response_data is not None:
                    print_message(f"✅ {profile_id} Tap thành công: balance {response_data.get('player', {}).get('shares', 0)} / năng lượng còn lại {response_data.get('player', {}).get('energy', 0)}")
                else:
                    print_message(f"❌ {profile_id} Tap thất bại")
                return response_data

            response_data=None
            for index in range(5):
                response_data=await __tap(random.randint(50, 250))
                if response_data.get("player", {}).get("energy", 0) < 50:         
                    break
            
            if response_data is None:
                return
            
            for boost in response_data.get("player").get("boost"):
                if boost.get("type")=="energy":
                    #mua NL
                    for k in range(boost['end'],boost['cnt']):
                        _r=await buy_boost("energy")
                        if _r is not None:
                            print_message(f"✅ {profile_id} Mua Energy thành công: balance {response_data.get('player', {}).get('shares', 0)} / năng lượng còn lại {response_data.get('player', {}).get('energy', 0)}")
                            for index in range(5):
                                response_data=await __tap(random.randint(50, 250))
                                if response_data.get("player", {}).get("energy", 0) < 50:         
                                    break
                        
                if boost.get("type")=="turbo":
                    #mua NL
                    for k in range(boost['end'],boost['cnt']):
                        _r=await buy_boost("turbo")
                        if _r is not None:
                            print_message(f"✅ {profile_id} Mua Turbo thành công: balance {response_data.get('player', {}).get('shares', 0)} / năng lượng còn lại {response_data.get('player', {}).get('energy', 0)}")
                            for index in range(22):
                                response_data=await __tap(random.randint(100000, 1000000))

                #         return print_message(f"❌ {profile_id} Năng lượng thấp.Move next...\n")

            if response_data is not None:
                if response_data.get("player").get("tap_level")< tap_level:
                    for i in range(response_data.get("player").get("tap_level")+1,tap_level+1):
                        r=await upgrade_level(upgrade_type="tap")
                        if r:
                            print_message(f"✅ {profile_id} Nâng cấp Tap Level {i} thành công...")
                        else:
                            print_message(f"❌ {profile_id} Nâng cấp Tap Level {i} thất bại...")
                            break
                 
                if response_data.get("player").get("energy_level")< energy_level:
                    for i in range(response_data.get("player").get("energy_level")+1,energy_level+1):
                        r=await upgrade_level(upgrade_type="energy")
                        if r:
                            print_message(f"✅ {profile_id} Nâng cấp Energy Level {i} thành công...")
                        else:
                            print_message(f"❌ {profile_id} Nâng cấp Energy Level {i} thất bại...")
                            break
                    
                if response_data.get("player").get("charge_level")< 5:
                    for i in range(response_data.get("player").get("charge_level")+1,6):
                        r=await upgrade_level(upgrade_type="charge")
                        if r:
                            print_message(f"✅ {profile_id} Nâng cấp Charge Level {i} thành công...")
                        else:
                            print_message(f"❌ {profile_id} Nâng cấp Charge Level {i} thất bại...")
                            break

                
        tao_data_dc = chr_value + '|' + query_id
        access_token, energy, boost_ready, energy_ready =await  get_access_token(tao_data_dc.strip())
        if access_token:
            headers['Authorization']=f"Bearer {access_token}"
            await submit_taps(tap_level,energy_level, energy, boost_ready, energy_ready, content_id, time_stamp, tao_data_dc.strip())


        
async def limited_exec(semaphore, profile):
    async with semaphore:
        await exec(profile)
        
async def main(count_process,delay_time): 
    df=pd.read_excel("account.xlsx",dtype={"time":int},sheet_name='tapswap')
    df=df[(~df['query'].isna()) & (df['query']!='')]
    if "proxy" not in df.columns:
            df["proxy"] = ""
    df['proxy']=df['proxy'].fillna('')
    
    if "tap_level" not in df.columns:
            df["tap_level"] = 14
    if "energy_level" not in df.columns:
            df["energy_level"] = 9
                    
    profiles=[]
    for idx,row in df.iterrows():
        profile={
            "id":idx+1,
            "query":row["query"],
            "content_id":str(row["content_id"]),
            "chr":str(row["chr"]),
            "time_stamp":str(row["time_stamp"]),
            "proxy":row["proxy"],
            "tap_level":row["tap_level"],
            "energy_level":row["energy_level"],
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
        
        


