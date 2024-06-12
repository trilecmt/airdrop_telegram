import datetime
from multiprocessing import Pool
import time
import pandas as pd
from pprint import pprint
import json
import helper
import pandas as pd
import random
from helper.helper_session import MySession
from helper.utils import print_message, sleep, format_number
import traceback
import sys
import argparse  
import  helper.utils as utils
import requests
from colorama import init, Fore, Style
init(autoreset=True)

url_config = "https://api.hamsterkombat.io/clicker/config"
url_get_info = "https://api.hamsterkombat.io/clicker/sync"    
url_boost = "https://api.hamsterkombat.io/clicker/boosts-for-buy"
url_tap = "https://api.hamsterkombat.io/clicker/tap"
url_buy_boost = "https://api.hamsterkombat.io/clicker/buy-boost"
url_ugrade_for_buy = "https://api.hamsterkombat.io/clicker/upgrades-for-buy"
url_buy_upgrade = "https://api.hamsterkombat.io/clicker/buy-upgrade"
url_claim_daily_combo="https://api.hamsterkombat.io/clicker/claim-daily-combo"
url_check_task = "https://api.hamsterkombat.io/clicker/list-tasks"
url_check_in = "https://api.hamsterkombat.io/clicker/check-task"
url_claim_daily_cipher = "https://api.hamsterkombat.io/clicker/claim-daily-cipher"

def get_daily_cards():
    url = 'https://raw.githubusercontent.com/trilecmt/airdrop_telegram/main/resources/hamster_daily_cards.json'
    f = requests.get(url)
    data = f.json()
    now=(datetime.datetime.utcnow()+datetime.timedelta(hours=7))
    if now.hour<19:
        now-=datetime.timedelta(days=1)
    _data=[item for item in data if item['date']==now.strftime("%Y%m%d")]
    if len(_data)==0:
        return None,None
   
    return _data[0]["cards"],_data[0].get("cipher","")


def exec(profile):
    profile_id=profile['id']
    token = profile['token']
    list_upgrade = profile['list_upgrade']
    proxy_url = profile['proxy_url']
    limit_buy_card = profile['limit_buy_card']
    daily_combo_cards_today = profile['daily_combo_cards_today']
    cipher=profile['cipher']
    session=MySession()
    ip=session.set_proxy(proxy_url)
    profile_id=f'{profile_id}[{ip}]'
    balance = 0
    time_upgraded = 1
    list_upgrade_cards= []
     
    def get_header(content_length = "0"):
        headers = {
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Host": "api.hamsterkombat.io",
            "Origin": "https://hamsterkombat.io",
            "Referer": "https://hamsterkombat.io/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
        }
        headers["Content-Length"] =content_length
        return headers
        
    def get_user_data(is_need_user_info:bool =  True):
        nonlocal balance
        response_info  = session.exec_post(url_get_info, headers=get_header(), data={})
        available_tap = response_info['clickerUser']['availableTaps']
        balance = round(response_info['clickerUser']['balanceCoins'],0)     
        # print_message("---")
        # print_message(f"#{profile_id} User Id: {response_info['clickerUser']['id']}")
        # print_message(f"#{profile_id} Current Level: {response_info['clickerUser']['level']}")
        # print_message(f"#{profile_id} Current Balance: {format_number(balance)}")
        # print_message(f"#{profile_id} Available Tap Sync: {format_number(available_tap)}")
        # print_message(f"#{profile_id} Earn per Tap: {response_info['clickerUser']['earnPerTap']}")
        # print_message(f"#{profile_id} Earn per Hour: {format_number(response_info['clickerUser']['earnPassivePerHour'])}")
        return available_tap
    
    def claim_login():
        response_info  = session.exec_post(url_check_task, headers=get_header(), data={})
        for task in response_info["tasks"]:
            if task["id"] == "streak_days" and task["isCompleted"] == False:
                sleep(1,3)
                payload = {"taskId": "streak_days"}
                response_info = session.exec_post(url_check_in, headers=get_header(content_length= "24"), data=payload)
                day_streak = response_info["task"]["days"]
                for _ in  response_info["task"]["rewardsByDays"]:
                    if _["days"] == day_streak:
                        print_message(f"✅ #{profile_id} Claim Sucess for Streak {day_streak} Days - {_['rewardCoins']} Coin")
            elif task["id"] == "streak_days" and task["isCompleted"] == True:
                pass
    
    

    def click(available_tap):
        nonlocal balance
        # print_message("======")
        try:
            response_data = session.exec_post(url_tap, headers=get_header(content_length="53"), data={
                "count": random.randint(30, 50),
                "availableTaps": available_tap,
                "timestamp": int(time.time())
            },log=True)    
            if response_data is not None:    
                avai_tap = response_data['clickerUser']['availableTaps']
                balance = round(response_data['clickerUser']['balanceCoins'],0)     
                earn_per_tap = response_data['clickerUser']["earnPerTap"]   
                click_count = round(available_tap/earn_per_tap)+1    
                print_message(f"✅ #{profile_id} Available Tap: {avai_tap}, Current Coin: {format_number(balance)}")
                return avai_tap
            else:
                print_message(f"❌ #{profile_id} ====>>>>ERROR WHEN TAP<<<<<<<<<<")
                return 0
        except Exception as e:
            print_message(traceback.format_exc())
            return 0
    
    def get_boost():
        def buy_boost(id: str):
            nonlocal balance
            response_info  = session.exec_post(url_buy_boost, headers=get_header(content_length="52"), data={
                "boostId": id,
                "timestamp": int(time.time())
            })
            if response_info is not None:
                print_message(f"✅ #{profile_id}===Buy Boost {id} Successed===")
                balance = round(response_info['clickerUser']['balanceCoins'],0)   
            return response_info
        
        multi_tap_level= int(utils.read_config(section='HAMSTER',key='multi_tap_level'))
        energy_level=int(utils.read_config(section='HAMSTER',key='energy_level'))
        response_info  = session.exec_post(url_boost, headers=get_header(), data={})
        sleep(3,5)
        boost_list = response_info["boostsForBuy"]
        for element in boost_list:
            if element["id"] == "BoostFullAvailableTaps":
                remain_boost = element["maxLevel"] - element["level"] + 1
                cooldown = element["cooldownSeconds"]
            elif element["id"] == "BoostEarnPerTap":
                if element["level"] < multi_tap_level and balance > element["price"]:
                    buy_boost("BoostEarnPerTap")
                    sleep(3,5)
            elif element["id"] == "BoostMaxTaps":
                if element["level"] < energy_level and balance > element["price"]:
                    buy_boost("BoostMaxTaps")
                    sleep(3,5)   

        if cooldown == 0 and remain_boost>0: 
            response_info  =  buy_boost("BoostFullAvailableTaps") 
            available_tap = response_info['clickerUser']['availableTaps']
            print_message(f"#{profile_id} Available Tap After Boost: {available_tap}")
            return available_tap
        elif cooldown > 0 :
            return 0
        else:
            return 0
    
    def looping_click(available_tap):
        while True:
            remain_tap = click(available_tap)
            sleep(4,5)
            if remain_tap ==0:
                break
    
    def claim_daily_combo_reward():
        response_info  = session.exec_post(url_claim_daily_combo, headers=get_header(), data={})
        if response_info is not None:
            print_message(f"✅ #{profile_id} Claimed daily combo success.")
            return True
        else:
            print_message(f"❌ #{profile_id} Claimed daily combo failed.")
            return False
        
    def buy_card(card_id: str):
        response_info = session.exec_post(url_buy_upgrade, headers=get_header(content_length="54"), data={
            "upgradeId": card_id,
            "timestamp": int(time.time())
        })
        return response_info

    def get_list_upgrade():
        nonlocal list_upgrade_cards
        response_info  = session.exec_post(url_ugrade_for_buy, headers=get_header(), data={})
        list_upgrade_cards = response_info["upgradesForBuy"]
        return response_info["upgradesForBuy"],response_info["dailyCombo"]
    
    def check_claimed_cipher():
        response_info  = session.exec_post(url_config, headers=get_header(), data={})
        return response_info["dailyCipher"]["isClaimed"]
    
    def claim_daily_cipher(cipher:str):
        if cipher is not None and cipher!="":
            try:
                if not check_claimed_cipher():                    
                    response_info  = session.exec_post(url_claim_daily_cipher, headers=get_header(), data={
                        "cipher": cipher
                    })
                    if response_info is not None:
                        print_message(f"✅ #{profile_id} => Claimed Daily Cipher {cipher} success")
                    else:
                        print_message(f"❌ #{profile_id} => Claimed Daily Cipher {cipher} failed")
                else:
                    print_message(f"✅ #{profile_id} => Daily Cipher already claimed")
            except Exception as e:
                pass
    
    def buy_conditions_cards(card_name: str, condtion: dict):
        if condtion["_type"] == "ReferralCount":
            print_message(f"❌ #{profile_id} {card_name} need number of Ref: {condtion['referralCount']} ...")
            return False
        if condtion["_type"] == "MoreReferralsCount":
            print_message(f"❌ #{profile_id} {card_name} need more Ref: {condtion['moreReferralsCount']} ...")
            return False
        if condtion["_type"] == "ByUpgrade":
            condition_card = [item for item in list_upgrade_cards if item['id'] == condtion["upgradeId"]][0]
            print_message(f"#{profile_id} {card_name} need {condition_card['name']} with level {condition_card['level']} ...")
            if condition_card['isExpired']==True:
                print_message(f"❌ #{profile_id} Bought card {condition_card['name']} failed due to Expired")
                return False
            if condition_card['isAvailable']==True:
                while condition_card["level"] < condtion["level"]:
                    get_user_data(is_need_user_info=False) #get balance again
                    if balance > condition_card['price']:
                        response_info = buy_card(condition_card['id']) 
                        sleep(2)
                        print_message(f"#❌ {profile_id} Buy condition card {condition_card['name']} level {condition_card['level']} success with price {format_number( condition_card['price'])}")
                        condition_card = [item for item in list_upgrade_cards if item['id'] == condtion["upgradeId"]][0] #get new level of condition card in the loop
                    else:
                        print_message(f"❌ #{profile_id} Buy condition card {condition_card['name']} level {condition_card['level']} failed because not enough money: price {format_number( condition_card['price'])}")
                        return False
                return True
            if condition_card['isAvailable']==False:
                result = buy_conditions_cards(condition_card['name'], condition_card['condition'])
                return result
    
    def buy_daily_combo_card():
        if daily_combo_cards_today is None:
            print_message(f"❌ #{profile_id} Not found daily combo card in server...")
            return False
        
        list_upgrade_cards,daily_combo = get_list_upgrade()
        if daily_combo['isClaimed']:
            print_message(f"✅ #{profile_id} Claimed daily combo card")
            return True

        daily_combo_cards=[item for item in list_upgrade_cards if item['name'] in daily_combo_cards_today]
        if len(daily_combo_cards)!=3:
            print_message(f"❌ #{profile_id} Combo card must 3 cards")
            return True
        is_available=True
        for card in daily_combo_cards:
            if card['isAvailable']==False or card['isExpired']==True:
                print_message(f"❌ #{profile_id} Bought card {card['name']} failed because not Available/Expired")
                is_available= False
            if card['isAvailable']==False:
                is_available = buy_conditions_cards(card['name'], card['condition'])                
        if not is_available:
            #fix here to continue to buy card upgrade if the combo not ready
            return True
        
        #re-run the list to see if the card UnAvailable becomes Available after buy_conditions_cards
        get_list_upgrade()
        daily_combo_cards=[item for item in list_upgrade_cards if item['name'] in daily_combo_cards_today]
        for card in daily_combo_cards:
            if card['id']  in daily_combo['upgradeIds']:
                print_message(f"✅ #{profile_id} Bought card {card['name']}")
            else:
                if card['isAvailable']==True and not card['isExpired']:
                    get_user_data(is_need_user_info=False)
                    if balance > card['price']:
                        sleep(1,2)
                        response_info = buy_card(card['id'])  
                        if response_info is not None: 
                            print_message(f"✅ #{profile_id} Buy daily card:Buy success {card['name']} with price {format_number( card['price'])}") 
                        else:
                            print_message(f"❌ #{profile_id} Buy daily card:Buy failed {card['name']} with price {format_number(card['price'])}")
                            return False 
                    else:
                        print_message(f"❌ #{profile_id} Buy daily card:Buy failed {card['name']} with price {format_number(card['price'])} because not enogh money")
                        #break here to stack more money for the card
                        return False
                else:
                    print_message(f"❌ #{profile_id} Bought card {card['name']} failed because not Available/Expired")
                    #fix here to continue to buy card upgrade if the combo not ready
                    return True
        sleep(2)            
        claim_daily_combo_reward()
        return True
    
    try:
        available_tap =  get_user_data()  
        claim_login()
        claim_daily_cipher(cipher=cipher)  
        is_continue=buy_daily_combo_card()
        if not is_continue:
            return
        sleep(2,4)
        for i in range(50):    
            get_user_data(is_need_user_info=False)  
            list_upgrade_cards,daily_combo = get_list_upgrade()

            if balance<limit_buy_card:
                print_message(f"❌ #{profile_id} Current balance {balance} reach LIMIT_BUY_CARD {limit_buy_card}")
                break
           
            for card in list_upgrade_cards:
                if card['isAvailable'] and not card['isExpired'] and card.get('totalCooldownSeconds',0)==0:
                    if card["price"] == 0 or card["price"] is None:
                        card["price"] = 1
                    card['ROI']=round(100*card['profitPerHourDelta']/card['price'],2)
                else:
                    card['ROI']=None
            list_upgrade_cards=[item for item in list_upgrade_cards if item['ROI'] is not None]
            list_upgrade_cards=sorted(list_upgrade_cards, key=lambda x: x['ROI'],reverse=True)
            if len(list_upgrade_cards)==0:
                break
            picked_upgrade_card=list_upgrade_cards[0] 
            if balance>picked_upgrade_card['price']:       
                response_info  = session.exec_post(url_buy_upgrade, headers=get_header(content_length="54"), data={
                    "upgradeId": picked_upgrade_card['id'],
                    "timestamp": int(time.time())
                })
                print_message(f"✅ #{profile_id} Bought {picked_upgrade_card['name']} with price {picked_upgrade_card['price']}, ROI: {picked_upgrade_card['ROI']}")
                sleep(2)
            else:
                print_message(f"❌ #{profile_id} Not enough coin for buy {picked_upgrade_card['name']} with price {picked_upgrade_card['price']}, ROI: {picked_upgrade_card['ROI']}")
                break
    except Exception as e:
        print_message(traceback.format_exc())


def main(delay_time,count_processes=1):
    try:
        daily_combo_cards_today,cipher=get_daily_cards()
        df=pd.read_excel("account.xlsx",dtype={"token":str},sheet_name='hamster')
        if "no_click" not in df.columns:
            df["no_click"] = 0
        df=df[(~df['token'].isna()) & (df['token']!='') & (df['no_click']==1)]

        df.reset_index(inplace=True)
        if "list_upgrade" not in df.columns:
            df["list_upgrade"] = ""
        if "proxy" not in df.columns:
            df["proxy"] = ""
        df['proxy']=df['proxy'].fillna('')
     
        profiles=[]
        for idx,row in df.iterrows():
            profile={
                "id":idx+1,
                "token":row['token'],
                "list_upgrade":row['list_upgrade'],
                "proxy_url":row['proxy'],
                "limit_buy_card":row['limit_buy_card'],
                "daily_combo_cards_today":daily_combo_cards_today,
                "cipher":cipher
            }
            profiles.append(profile)
            
        if count_processes !=1:
            with Pool(count_processes) as p:
                p.map(exec, profiles)
        else:
            for profile in profiles:
                exec(profile)    
      
        print(f"\n{Fore.GREEN+Style.BRIGHT}========={Fore.WHITE+Style.BRIGHT}Tất cả tài khoản đã được xử lý thành công{Fore.GREEN+Style.BRIGHT}=========", end="", flush=True)
        print(f"\r\n\n{Fore.GREEN+Style.BRIGHT}Loading...", end="", flush=True)
        
        for __second in range(2*60*60, 0, -1):
            sys.stdout.write(f"\r{Fore.CYAN}Chờ {Fore.CYAN}{Fore.WHITE}{__second // 60} phút {Fore.WHITE}{__second % 60} giây")
            sys.stdout.flush()
            time.sleep(1)
        sys.stdout.write("\rBắt đầu xử lý...!\n")
    except Exception as e:
        print_message(traceback.format_exc())

if __name__=='__main__':
    count_processes=1#int(input("Enter number process:"))
    while True:        
        main(delay_time=60,count_processes=count_processes)                      
