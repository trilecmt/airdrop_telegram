import time
import pandas as pd
import requests
from pprint import pprint
import json
import helper
import random
import traceback
from helper.helper_session import MySession
from helper.utils import print_message, sleep, format_number
from datetime import datetime, timedelta


def exec(token, proxy_url:str):
    session=MySession()
    session.set_proxy(proxy_url)
    url= "https://api-gw-tg.memefi.club/graphql"
    header = {
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://tg-app.memefi.club",
        "Referer": "https://tg-app.memefi.club/",
        "Priority": "u=1, i",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="24"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
    }    
    current_energy = 0 
    max_energy = 0
    time_att = 1
    att_dmg = 0
    refill_amt = 3
    
    
    def get_user_info()-> str:        
        payload = {
        "operationName": "QueryTelegramUserMe",
        "variables": {},
        "query": "query QueryTelegramUserMe {\n  telegramUserMe {\n    firstName\n    lastName\n    telegramId\n    username\n    referralCode\n    isDailyRewardClaimed\n    referral {\n      username\n      lastName\n      firstName\n      bossLevel\n      coinsAmount\n      __typename\n    }\n    isReferralInitialJoinBonusAvailable\n    league\n    leagueIsOverTop10k\n    leaguePosition\n    _id\n    opens {\n      isAvailable\n      openType\n      __typename\n    }\n    __typename\n  }\n}"
        }
        response_data = session.exec_post(url, headers=header, data=payload)
        data = response_data["data"]
        key = next(iter(data)) 
        print_message(f'UserName: {data[key]["firstName"]+" " + data[key]["lastName"]}')
        print_message(f'UserId: {data[key]["telegramId"]}')
        time.sleep(2)
        
    def print_response(response_data:dict):
        nonlocal current_energy
        nonlocal att_dmg
        nonlocal refill_amt
        nonlocal max_energy
        data = response_data["data"]
        key = next(iter(response_data["data"]))            
        current_energy = data[key]['currentEnergy']
        max_energy = data[key]['maxEnergy']
        current_coin = data[key]['coinsAmount']   
        att_dmg = data[key]['weaponLevel'] +1
        refill_amt = data[key]['freeBoosts']['currentRefillEnergyAmount'] 
        print_message(f"Current Coin: {format_number(current_coin)}, Energy: {current_energy}/{max_energy}. Recharge left: {refill_amt}") 
        return data[key]['nonce']
    
    def get_game_config()-> str:
        print_message("===Getting Game Config===")
        payload = {
        "operationName": "QUERY_GAME_CONFIG",
        "variables": {},
        "query": "query QUERY_GAME_CONFIG {\n  telegramGameGetConfig {\n    ...FragmentBossFightConfig\n    __typename\n  }\n}\n\nfragment FragmentBossFightConfig on TelegramGameConfigOutput {\n  _id\n  coinsAmount\n  currentEnergy\n  maxEnergy\n  weaponLevel\n  energyLimitLevel\n  energyRechargeLevel\n  tapBotLevel\n  currentBoss {\n    _id\n    level\n    currentHealth\n    maxHealth\n    __typename\n  }\n  freeBoosts {\n    _id\n    currentTurboAmount\n    maxTurboAmount\n    turboLastActivatedAt\n    turboAmountLastRechargeDate\n    currentRefillEnergyAmount\n    maxRefillEnergyAmount\n    refillEnergyLastActivatedAt\n    refillEnergyAmountLastRechargeDate\n    __typename\n  }\n  bonusLeaderDamageEndAt\n  bonusLeaderDamageStartAt\n  bonusLeaderDamageMultiplier\n  nonce\n  __typename\n}"
        }        
        response_data = session.exec_post(url, headers=header, data=payload) 
        last_id = print_response(response_data =response_data)
        time.sleep(3)    
        return last_id
    
    def get_date_format(date_str : str):
        date_format = '%Y-%m-%dT%H:%M:%S.%fZ'
        if date_str is None:
            return ""
        else:
            return datetime.strptime(date_str, date_format) + timedelta (hours=7)
    
    
    def get_tapbot_config():        
        print_message("===Getting Tapbot Config===")
        payload= {
        "operationName": "TapbotConfig",
        "variables": {},
        "query": "fragment FragmentTapBotConfig on TelegramGameTapbotOutput {\n  damagePerSec\n  endsAt\n  id\n  isPurchased\n  startsAt\n  totalAttempts\n  usedAttempts\n  __typename\n}\n\nquery TapbotConfig {\n  telegramGameTapbotGetConfig {\n    ...FragmentTapBotConfig\n    __typename\n  }\n}"
        }
        response_data = session.exec_post(url, headers=header, data=payload)
        data = response_data["data"]
        key = next(iter(data))
        is_purchase = data[key]["isPurchased"]
        remain= data[key]["totalAttempts"] - data[key]["usedAttempts"]        
        end_at = get_date_format(data[key]["endsAt"])
        format_print = "%H:%M %d/%m/%Y"
        if not is_purchase:
            print_message(f"TapBot is not purchased")
        elif end_at == "":
            print_message(f"TapBot is not activated")
            print_message(f"TapBot remain time: {remain}")
            if remain > 0:
                sleep(3,10)
                tapbot_activate()
                sleep(3,5)
                get_tapbot_config()
        else:
            print_message(f"TapBot remain time: {remain}")
            print_message(f"Tapbot claim time: {end_at}")
            if end_at <= datetime.now():
                sleep(3,10)
                tapbot_claim()
                sleep(3,5)
                get_tapbot_config()
            
        
    def tapbot_claim():
        print_message("===Claiming Tapbot===")
        payload = {
        "operationName": "TapbotClaim",
        "variables": {},
        "query": "fragment FragmentTapBotConfig on TelegramGameTapbotOutput {\n  damagePerSec\n  endsAt\n  id\n  isPurchased\n  startsAt\n  totalAttempts\n  usedAttempts\n  __typename\n}\n\nmutation TapbotClaim {\n  telegramGameTapbotClaimCoins {\n    ...FragmentTapBotConfig\n    __typename\n  }\n}"
        }
        response_data = session.exec_post(url, headers=header, data=payload)
    
    def tapbot_activate():
        print_message("===Activating Tapbot===")
        payload = {
        "operationName": "TapbotStart",
        "variables": {},
        "query": "fragment FragmentTapBotConfig on TelegramGameTapbotOutput {\n  damagePerSec\n  endsAt\n  id\n  isPurchased\n  startsAt\n  totalAttempts\n  usedAttempts\n  __typename\n}\n\nmutation TapbotStart {\n  telegramGameTapbotStart {\n    ...FragmentTapBotConfig\n    __typename\n  }\n}"
        }
        response_data = session.exec_post(url, headers=header, data=payload)       
        
    
    def attack(last_id: str):
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
        response_data = session.exec_post(url, headers=header, data=payload) 
        print_message(f"--Attack time: {time_att}, tap {count_tap} times")
        last_id = print_response(response_data =response_data)
        time_att += 1
        return last_id

    def action_attack(last_id):
        while current_energy> att_dmg *10:
            last_id = attack(last_id)            
            time.sleep(4)
    
    def get_recharge_boost():
        nonlocal time_att  
        print_message("===Getting Boost===")
        payload = {
        "operationName": "telegramGameActivateBooster",
        "variables": {
            "boosterType": "Recharge"
        },
        "query": "mutation telegramGameActivateBooster($boosterType: BoosterType!) {\n  telegramGameActivateBooster(boosterType: $boosterType) {\n    ...FragmentBossFightConfig\n    __typename\n  }\n}\n\nfragment FragmentBossFightConfig on TelegramGameConfigOutput {\n  _id\n  coinsAmount\n  currentEnergy\n  maxEnergy\n  weaponLevel\n  energyLimitLevel\n  energyRechargeLevel\n  tapBotLevel\n  currentBoss {\n    _id\n    level\n    currentHealth\n    maxHealth\n    __typename\n  }\n  freeBoosts {\n    _id\n    currentTurboAmount\n    maxTurboAmount\n    turboLastActivatedAt\n    turboAmountLastRechargeDate\n    currentRefillEnergyAmount\n    maxRefillEnergyAmount\n    refillEnergyLastActivatedAt\n    refillEnergyAmountLastRechargeDate\n    __typename\n  }\n  bonusLeaderDamageEndAt\n  bonusLeaderDamageStartAt\n  bonusLeaderDamageMultiplier\n  nonce\n  __typename\n}"
        }
        response_data = session.exec_post(url, headers=header, data=payload)
        last_id = print_response(response_data=response_data)
        time_att = 0
        time.sleep(3)
        return last_id
    
    try:
        print_message("*********************************************************")
                
        get_user_info()        
        last_id = get_game_config()
        action_attack(last_id)
        while refill_amt>0:
            last_id = get_recharge_boost()
            action_attack(last_id)
            if time_att >=50 and current_energy == max_energy:
                print("===The is something wrong with the game===")
                return 
        sleep(3,6)
        
        get_tapbot_config() 
      
        print_message("*********************************************************")

        
    except Exception as e:        
        print(traceback.format_exc())
        pass


def main(delay_time):
    try:
        df=pd.read_excel("account.xlsx",dtype={"url":str},sheet_name='memefi')
        df=df[(~df['token'].isna()) & (df['token']!='')]
        df.reset_index(inplace=True)
        if "list_upgrade" not in df.columns:
            df["list_upgrade"] = ""
        if "proxy" not in df.columns:
            df["proxy"] = ""
        df['proxy']=df['proxy'].fillna('')
        for idx,row in df.iterrows():
            exec(row['token'],proxy_url=row['proxy'])
            time.sleep(10)
            
        time.sleep(delay_time)
    except Exception as e:
        print(e)

if __name__=='__main__':
    while True:
        try:
            main(delay_time=120)                      
        except Exception as e:
            print(e)