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

QUERY_LOGIN = """mutation MutationTelegramUserLogin($webAppData: TelegramWebAppDataInput!) {
            telegramUserLogin(webAppData: $webAppData) {
                access_token
                __typename
            }
        }"""
url = 'https://api-gw-tg.memefi.club/graphql'


def create_payload_login(query):
    tg_web_data = unquote(unquote(query))
    query_id = tg_web_data.split('query_id=', maxsplit=1)[1].split('&user', maxsplit=1)[0]
    user_data = tg_web_data.split('user=', maxsplit=1)[1].split('&auth_date', maxsplit=1)[0]
    auth_date = tg_web_data.split('auth_date=', maxsplit=1)[1].split('&hash', maxsplit=1)[0]
    hash_ = tg_web_data.split('hash=', maxsplit=1)[1].split('&', maxsplit=1)[0]
    user_data_dict = json.loads(unquote(user_data))
    data = {
        "operationName": "MutationTelegramUserLogin",
        "variables": {
            "webAppData": {
                "auth_date": int(auth_date),
                "hash": hash_,
                "query_id": query_id,
                "checkDataString": f"auth_date={auth_date}\nquery_id={query_id}\nuser={unquote(user_data)}",
                "user": {
                    "id": user_data_dict["id"],
                    "allows_write_to_pm": user_data_dict.get("allows_write_to_pm",True),
                    "first_name": user_data_dict["first_name"],
                    "last_name": user_data_dict["last_name"],
                    "username": user_data_dict.get("username", "Username không được đặt"),
                    "language_code": user_data_dict["language_code"],
                    "version": "7.2",
                    "platform": "ios"
                }
            }
        },
        "query": QUERY_LOGIN
    }
    return data
            
async def exec(profile):
    profile_id=profile['id']
    try:
        query=profile['query']
        print_message(f'#{profile_id} {query}')
        header = {'Accept': 'application/json', 'Accept-Language': 'en-US,en;q=0.9', 'Content-Type': 'application/json', 'Origin': 'https://tg-app.memefi.club', 'Referer': 'https://tg-app.memefi.club/', 'Sec-Ch-Ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"', 'Sec-Ch-Ua-mobile': '?1', 'Sec-Ch-Ua-platform': '"Android"', 'Sec-Fetch-Dest': 'empty', 'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Site': 'same-site', 'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36'}
        from helper.helper_client_session import ClientSession
        async with ClientSession(proxy_url=profile['proxy']) as session:
            print_message(f"#{profile_id} Checking new IP...")
            response =await session.exec_get(url="https://httpbin.org/ip",headers={"content-type": "application/json"})
            if response is None:
                print_message(f"#{profile_id} Get new IP Failed")
                return
            else:
                print_message(f"#{profile_id} New IP:{response['origin']}")

            json_response=await session.exec_post(url, headers=header, data=create_payload_login(query))


            print_message(f"#{profile_id} {json_response}")
            if "errors" in json_response:
                error=json_response["errors"][0]["message"]
                f = open("log_error.txt", "a")
                f.write(f'\n{str(profile_id)}-{error}')
                f.close()
                return
            
            access_token = json_response['data']['telegramUserLogin']['access_token']
            payload = {
                "operationName": "QueryTelegramUserMe",
                "variables": {},
                "query": "query QueryTelegramUserMe {\n  telegramUserMe {\n    firstName\n    lastName\n    telegramId\n    username\n    referralCode\n    isDailyRewardClaimed\n    referral {\n      username\n      lastName\n      firstName\n      bossLevel\n      coinsAmount\n      __typename\n    }\n    isReferralInitialJoinBonusAvailable\n    league\n    leagueIsOverTop10k\n    leaguePosition\n    _id\n    opens {\n      isAvailable\n      openType\n      __typename\n    }\n    __typename\n  }\n}"
                }
            
            header['Authorization']= f'Bearer {access_token}'

            json_response=await session.exec_post(url, headers=header, data=payload)
            print_message(f'#{profile_id} Id:{json_response['data']['telegramUserMe']['telegramId']}')    
            current_energy = 0 
            max_energy = 0
            time_att = 1
            att_dmg = 0
            refill_amt = 3
            current_coin = 0
            current_boss_health= 1000
            
            
            async def get_user_info()-> str:        
                payload = {
                "operationName": "QueryTelegramUserMe",
                "variables": {},
                "query": "query QueryTelegramUserMe {\n  telegramUserMe {\n    firstName\n    lastName\n    telegramId\n    username\n    referralCode\n    isDailyRewardClaimed\n    referral {\n      username\n      lastName\n      firstName\n      bossLevel\n      coinsAmount\n      __typename\n    }\n    isReferralInitialJoinBonusAvailable\n    league\n    leagueIsOverTop10k\n    leaguePosition\n    _id\n    opens {\n      isAvailable\n      openType\n      __typename\n    }\n    __typename\n  }\n}"
                }
                response_data = await session.exec_post(url, headers=header, data=payload)
                data = response_data["data"]
                key = next(iter(data)) 
                print_message(f'#{profile_id} UserName: {data[key]["firstName"]+" " + data[key]["lastName"]}')
                print_message(f'#{profile_id} UserId: {data[key]["telegramId"]}')
                time.sleep(2)
                
            async def print_response(response_data:dict):
                nonlocal current_energy
                nonlocal att_dmg
                nonlocal refill_amt
                nonlocal max_energy
                nonlocal current_coin
                nonlocal current_boss_health
                data = response_data["data"]
                key = next(iter(response_data["data"]))            
                current_energy = data[key]['currentEnergy']
                max_energy = data[key]['maxEnergy']
                current_coin = data[key]['coinsAmount']   
                att_dmg = data[key]['weaponLevel'] +1
                refill_amt = data[key]['freeBoosts']['currentRefillEnergyAmount'] 
                current_boss_health  = data[key]['currentBoss']["currentHealth"]
                if current_boss_health == 0:
                    sleep(3,7)
                    await move_to_next_boss()
                    sleep(1,3)
                    await get_game_config()            
                print_message(f"#{profile_id} Current Coin: {format_number(current_coin)}, Energy: {current_energy}/{max_energy}. Recharge left: {refill_amt}") 
                return data[key]['nonce']
            
            async def get_game_config()-> str:
                print_message(f"#{profile_id} ===Getting Game Config===")
                payload = {
                "operationName": "QUERY_GAME_CONFIG",
                "variables": {},
                "query": "query QUERY_GAME_CONFIG {\n  telegramGameGetConfig {\n    ...FragmentBossFightConfig\n    __typename\n  }\n}\n\nfragment FragmentBossFightConfig on TelegramGameConfigOutput {\n  _id\n  coinsAmount\n  currentEnergy\n  maxEnergy\n  weaponLevel\n  energyLimitLevel\n  energyRechargeLevel\n  tapBotLevel\n  currentBoss {\n    _id\n    level\n    currentHealth\n    maxHealth\n    __typename\n  }\n  freeBoosts {\n    _id\n    currentTurboAmount\n    maxTurboAmount\n    turboLastActivatedAt\n    turboAmountLastRechargeDate\n    currentRefillEnergyAmount\n    maxRefillEnergyAmount\n    refillEnergyLastActivatedAt\n    refillEnergyAmountLastRechargeDate\n    __typename\n  }\n  bonusLeaderDamageEndAt\n  bonusLeaderDamageStartAt\n  bonusLeaderDamageMultiplier\n  nonce\n  __typename\n}"
                }        
                response_data =await session.exec_post(url, headers=header, data=payload) 
                last_id =await print_response(response_data =response_data)
                time.sleep(3)    
                return last_id
            
            def get_date_format(date_str : str):
                date_format = '%Y-%m-%dT%H:%M:%S.%fZ'
                if date_str is None:
                    return ""
                else:
                    return datetime.strptime(date_str, date_format) + timedelta (hours=7)
            
            
            async def get_tapbot_config():        
                print_message(f"#{profile_id}===Getting Tapbot Config===")
                payload= {
                "operationName": "TapbotConfig",
                "variables": {},
                "query": "fragment FragmentTapBotConfig on TelegramGameTapbotOutput {\n  damagePerSec\n  endsAt\n  id\n  isPurchased\n  startsAt\n  totalAttempts\n  usedAttempts\n  __typename\n}\n\nquery TapbotConfig {\n  telegramGameTapbotGetConfig {\n    ...FragmentTapBotConfig\n    __typename\n  }\n}"
                }
                response_data =await session.exec_post(url, headers=header, data=payload)
                data = response_data["data"]
                key = next(iter(data))
                is_purchase = data[key]["isPurchased"]
                remain= data[key]["totalAttempts"] - data[key]["usedAttempts"]        
                # current_coin = data[key]['coinsAmount']
                end_at = get_date_format(data[key]["endsAt"])
                format_print = "%H:%M %d/%m/%Y"
                if not is_purchase:
                    print_message(f"#{profile_id} TapBot is not purchased")
                    if current_coin >= 200000:
                        sleep(3,10)
                        await tapbot_buying()
                        sleep(3,5)
                        await get_tapbot_config()
                    else:
                        print(f"#{profile_id}===Not Enough Coin to buy TapBot===")
                elif end_at == "":
                    print_message(f"#{profile_id} TapBot is not activated")
                    print_message(f"#{profile_id} TapBot remain time: {remain}")
                    if remain > 0:
                        sleep(3,10)
                        await tapbot_activate()
                        sleep(3,5)
                        await get_tapbot_config()
                else:
                    print_message(f"#{profile_id} TapBot remain time: {remain}")
                    print_message(f"#{profile_id} Tapbot claim time: {end_at}")
                    if end_at <= datetime.now():
                        sleep(3,10)
                        await tapbot_claim()
                        sleep(3,5)
                        await get_tapbot_config()
                    
                
            async def tapbot_claim():
                print_message(f"#{profile_id}===Claiming Tapbot===")
                payload = {
                "operationName": "TapbotClaim",
                "variables": {},
                "query": "fragment FragmentTapBotConfig on TelegramGameTapbotOutput {\n  damagePerSec\n  endsAt\n  id\n  isPurchased\n  startsAt\n  totalAttempts\n  usedAttempts\n  __typename\n}\n\nmutation TapbotClaim {\n  telegramGameTapbotClaimCoins {\n    ...FragmentTapBotConfig\n    __typename\n  }\n}"
                }
                response_data = await session.exec_post(url, headers=header, data=payload)
            
            async def tapbot_activate():
                print_message(f"#{profile_id}===Activating Tapbot===")
                payload = {
                "operationName": "TapbotStart",
                "variables": {},
                "query": "fragment FragmentTapBotConfig on TelegramGameTapbotOutput {\n  damagePerSec\n  endsAt\n  id\n  isPurchased\n  startsAt\n  totalAttempts\n  usedAttempts\n  __typename\n}\n\nmutation TapbotStart {\n  telegramGameTapbotStart {\n    ...FragmentTapBotConfig\n    __typename\n  }\n}"
                }
                response_data = await session.exec_post(url, headers=header, data=payload)       
                
            async def tapbot_buying():
                print_message(f"#{profile_id}===Buying Tapbot===")
                payload = {
                "operationName": "telegramGamePurchaseUpgrade",
                "variables": {"upgradeType": "TapBot"},
                "query": "fragment FragmentTapBotConfig on TelegramGameTapbotOutput {\n  damagePerSec\n  endsAt\n  id\n  isPurchased\n  startsAt\n  totalAttempts\n  usedAttempts\n  __typename\n}\n\nmutation TapbotStart {\n  telegramGameTapbotStart {\n    ...FragmentTapBotConfig\n    __typename\n  }\n}"
                }
                response_data =await session.exec_post(url, headers=header, data=payload)
            
            async def move_to_next_boss():
                print_message(f"#{profile_id}===Moving to Next Boss")
                payload = {
                "operationName": "telegramGameSetNextBoss",
                "variables": {},
                "query": "mutation telegramGameSetNextBoss {\n  telegramGameSetNextBoss {\n    ...FragmentBossFightConfig\n    __typename\n  }\n}\n\nfragment FragmentBossFightConfig on TelegramGameConfigOutput {\n  _id\n  coinsAmount\n  currentEnergy\n  maxEnergy\n  weaponLevel\n  energyLimitLevel\n  energyRechargeLevel\n  tapBotLevel\n  currentBoss {\n    _id\n    level\n    currentHealth\n    maxHealth\n    __typename\n  }\n  freeBoosts {\n    _id\n    currentTurboAmount\n    maxTurboAmount\n    turboLastActivatedAt\n    turboAmountLastRechargeDate\n    currentRefillEnergyAmount\n    maxRefillEnergyAmount\n    refillEnergyLastActivatedAt\n    refillEnergyAmountLastRechargeDate\n    __typename\n  }\n  bonusLeaderDamageEndAt\n  bonusLeaderDamageStartAt\n  bonusLeaderDamageMultiplier\n  nonce\n  __typename\n}"
                }
                response_data =await session.exec_post(url, headers=header, data=payload)
            
            
            async def attack(last_id: str):
                nonlocal time_att        
                count_tap = random.randint(5, 40)
                if count_tap * att_dmg > current_energy:
                    count_tap = round(current_energy/att_dmg)-1
                payload = {
                    "operationName": "MutationGameProcessTapsBatch",
                    "variables": {
                        "payload": {
                        "nonce": last_id,
                        "tapsCount":  count_tap
                        }
                    },
                    "query": "mutation MutationGameProcessTapsBatch($payload: TelegramGameTapsBatchInput!) {\n  telegramGameProcessTapsBatch(payload: $payload) {\n    ...FragmentBossFightConfig\n    __typename\n  }\n}\n\nfragment FragmentBossFightConfig on TelegramGameConfigOutput {\n  _id\n  coinsAmount\n  currentEnergy\n  maxEnergy\n  weaponLevel\n  energyLimitLevel\n  energyRechargeLevel\n  tapBotLevel\n  currentBoss {\n    _id\n    level\n    currentHealth\n    maxHealth\n    __typename\n  }\n  freeBoosts {\n    _id\n    currentTurboAmount\n    maxTurboAmount\n    turboLastActivatedAt\n    turboAmountLastRechargeDate\n    currentRefillEnergyAmount\n    maxRefillEnergyAmount\n    refillEnergyLastActivatedAt\n    refillEnergyAmountLastRechargeDate\n    __typename\n  }\n  bonusLeaderDamageEndAt\n  bonusLeaderDamageStartAt\n  bonusLeaderDamageMultiplier\n  nonce\n  __typename\n}"
                }
                response_data =await session.exec_post(url, headers=header, data=payload) 
                print_message(f"#{profile_id} --Attack time: {time_att}, tap {count_tap} times")
                last_id =await print_response(response_data =response_data)
                time_att += 1
                return last_id

            async def action_attack(last_id):
                while current_energy> att_dmg *10:
                    last_id =await  attack(last_id)            
                    sleep(9,15)
            
            async def get_recharge_boost():
                nonlocal time_att  
                print_message(f"#{profile_id}===Getting Boost===")
                payload = {
                "operationName": "telegramGameActivateBooster",
                "variables": {
                    "boosterType": "Recharge"
                },
                "query": "mutation telegramGameActivateBooster($boosterType: BoosterType!) {\n  telegramGameActivateBooster(boosterType: $boosterType) {\n    ...FragmentBossFightConfig\n    __typename\n  }\n}\n\nfragment FragmentBossFightConfig on TelegramGameConfigOutput {\n  _id\n  coinsAmount\n  currentEnergy\n  maxEnergy\n  weaponLevel\n  energyLimitLevel\n  energyRechargeLevel\n  tapBotLevel\n  currentBoss {\n    _id\n    level\n    currentHealth\n    maxHealth\n    __typename\n  }\n  freeBoosts {\n    _id\n    currentTurboAmount\n    maxTurboAmount\n    turboLastActivatedAt\n    turboAmountLastRechargeDate\n    currentRefillEnergyAmount\n    maxRefillEnergyAmount\n    refillEnergyLastActivatedAt\n    refillEnergyAmountLastRechargeDate\n    __typename\n  }\n  bonusLeaderDamageEndAt\n  bonusLeaderDamageStartAt\n  bonusLeaderDamageMultiplier\n  nonce\n  __typename\n}"
                }
                response_data =await session.exec_post(url, headers=header, data=payload)
                last_id =await print_response(response_data=response_data)
                time_att = 0
                time.sleep(3)
                return last_id
            
            try:
                print_message(f"#{profile_id} *********************************************************")
                        
                await get_user_info()        
                last_id = await get_game_config()
                await action_attack(last_id)
                while refill_amt>0:
                    last_id = await get_recharge_boost()
                    await action_attack(last_id)
                    if time_att >=50 and current_energy == max_energy:
                        print(f"#{profile_id} ===The is something wrong with the game===")
                        return 
                sleep(3,6)     
                await get_tapbot_config() 
                print_message(f"#{profile_id} *********************************************************")

                
            except Exception as e:        
                print(traceback.format_exc())
                pass
    except Exception as e:        
        print_message(f'#{profile_id} ERROR............')
        print(traceback.format_exc())
        pass


async def limited_exec(semaphore, profile):
    async with semaphore:
        await exec(profile)

async def main(count_process):
    
    df=pd.read_excel("account.xlsx",dtype={"query":str},sheet_name='memefi')
    df=df[(~df['query'].isna()) & (df['query']!='')]
    if "proxy" not in df.columns:
            df["proxy"] = ""
    df['proxy']=df['proxy'].fillna('')
    
    profiles=[]
    for idx,row in df.iterrows():
        profile={
            "id":idx+1,
            "query":row["query"],
            "proxy":row["proxy"]
        }
        profiles.append(profile)
        # await exec(profile)
    semaphore = asyncio.Semaphore(count_process)  # Limit to 5 concurrent tasks
    tasks = [limited_exec(semaphore, profile) for profile in profiles]
    await asyncio.gather(*tasks)

if __name__=="__main__":
    count_process=1#int(input("Enter count process:"))
    while True:
        asyncio.run(main(count_process))
        time.sleep(60)

# def main(delay_time):
#     try:
#         df=pd.read_excel("account.xlsx",dtype={"url":str},sheet_name='memefi')
#         df=df[(~df['token'].isna()) & (df['token']!='')]
#         df.reset_index(inplace=True)
#         if "list_upgrade" not in df.columns:
#             df["list_upgrade"] = ""
#         if "proxy" not in df.columns:
#             df["proxy"] = ""
#         df['proxy']=df['proxy'].fillna('')
#         for idx,row in df.iterrows():
#             exec("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7Il9pZCI6IjY2NWRkN2JkNDgxMjkwOTJkZjlkNjgwMSIsInVzZXJuYW1lIjoiam9uMTEwOCJ9LCJzZXNzaW9uSWQiOiI2NjYzMDlkYjM3YWEzZjk4OWVkNjlhOWMiLCJzdWIiOiI2NjVkZDdiZDQ4MTI5MDkyZGY5ZDY4MDEiLCJpYXQiOjE3MTc3NjY2MTksImV4cCI6MTcxODM3MTQxOX0.X4Z2_y3Knwq3-TmZXylSlq9hyOviRJgpvDzsB6UfeDc"
#                 #  ,row['token'],
#                  ,proxy_url=""
#                  #row['proxy'])
#             )
#             time.sleep(10)
            
#         time.sleep(delay_time)
#     except Exception as e:
#         print(e)

# if __name__=='__main__':
#     while True:
#         try:
#             main(delay_time=120)                      
#         except Exception as e:
#             print(e)