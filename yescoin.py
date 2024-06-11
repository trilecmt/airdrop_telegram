import asyncio
import time
from urllib.parse import unquote
import pandas as pd
from pprint import pprint
import json
import random
import traceback
from helper.utils import print_message, sleep, format_number
from datetime import datetime, timedelta

url_collect = 'https://api.yescoin.gold/game/collectCoin';
url_account_info = 'https://api.yescoin.gold/account/getAccountInfo';
url_game_info = 'https://api.yescoin.gold/game/getGameInfo';

            
async def exec(profile):
    profile_id=profile['id']
    try:
        token=profile['token']
        if "{" in token and "}" in token:
            token=json.loads(token).get("token")         
        header = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
            'Origin': 'https://www.yescoin.gold',
            'Referer': 'https://www.yescoin.gold/',
            'Sec-Ch-Ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'Token': token,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        };
        from helper.helper_client_session import ClientSession
        async with ClientSession(proxy_url=profile['proxy']) as session:
            response =await session.exec_get(url="https://httpbin.org/ip",headers={"content-type": "application/json"})
            if response is None:
                print_message(f"❌ #{profile_id} Get new IP Failed")
                return

            json_response=await session.exec_get(url_game_info, headers=header)
            if json_response is None:
                return print_message(f"❌ #{profile_id} ERROR {json_response}")

            coin_pool=json_response['data']['coinPoolTotalCount']
            coin_left=json_response['data']['coinPoolLeftCount']
            if coin_left<150:
                return print_message(f"❌ #{profile_id} Mana too low.Move Next...")  
            json_response=await session.exec_post(url_collect, headers=header,data=random.randint(50,100))
            if json_response is None:
                return print_message(f"❌ #{profile_id} ERROR {json_response}")
            json_response=await session.exec_get(url_account_info, headers=header)
            if json_response is None:
                return print_message(f"❌ #{profile_id} ERROR {json_response}")     
            print_message(f"✅ #{profile_id}[{response['origin']}] Mana: {coin_left}/{coin_pool}  =>Claim success.Balance: {json_response['data']['currentAmount']}, User Level: {json_response['data']['userLevel']}, Rank: {json_response['data']['rank']}")

    except Exception as e:        
        print_message(f'❌ #{profile_id} ERROR............')
        print(traceback.format_exc())
        pass


async def limited_exec(semaphore, profile):
    async with semaphore:
        await exec(profile)

async def main(count_process):
    
    df=pd.read_excel("account.xlsx",dtype={"token":str},sheet_name='yescoin')
    df=df[(~df['token'].isna()) & (df['token']!='')]
    if "proxy" not in df.columns:
            df["proxy"] = ""
    df['proxy']=df['proxy'].fillna('')
    
    profiles=[]
    for idx,row in df.iterrows():
        profile={
            "id":idx+1,
            "token":row["token"],
            "proxy":row["proxy"]
        }
        profiles.append(profile)
        # await exec(profile)
    semaphore = asyncio.Semaphore(count_process)  # Limit to 5 concurrent tasks
    tasks = [limited_exec(semaphore, profile) for profile in profiles]
    await asyncio.gather(*tasks)

if __name__=="__main__":
    count_process=int(input("Enter #CPU:"))
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    while True:
        asyncio.run(main(count_process))
        time.sleep(10)

