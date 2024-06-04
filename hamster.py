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


url_get_info = "https://api.hamsterkombat.io/clicker/sync"    
url_boost = "https://api.hamsterkombat.io/clicker/boosts-for-buy"
url_tap = "https://api.hamsterkombat.io/clicker/tap"
url_buy_boost = "https://api.hamsterkombat.io/clicker/buy-boost"
url_ugrade_for_buy = "https://api.hamsterkombat.io/clicker/upgrades-for-buy"
url_buy_upgrade = "https://api.hamsterkombat.io/clicker/buy-upgrade"
url_claim_daily_combo="https://api.hamsterkombat.io/clicker/claim-daily-combo"
url_check_task = "https://api.hamsterkombat.io/clicker/list-tasks"
url_check_in = "https://api.hamsterkombat.io/clicker/check-task"


def exec(profile):
    profile_id=profile['id']
    token = profile['token']
    list_upgrade = profile['list_upgrade']
    proxy_url = profile['proxy_url']
    limit_buy_card = profile['limit_buy_card']
    input_daily_combo_cards = [_ for _ in profile['input_daily_combo_cards'] if _ != ""]
    session=MySession()
    ip=session.set_proxy(proxy_url)
    profile_id=f'{profile_id}[{ip}]'
    balance = 0
    time_upgraded = 1
     
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
        
    def get_user_data():
        nonlocal balance
        response_info  = session.exec_post(url_get_info, headers=get_header(), data={})
        available_tap = response_info['clickerUser']['availableTaps']
        balance = round(response_info['clickerUser']['balanceCoins'],0)     
        print_message(f"#{profile_id} User Id: {response_info['clickerUser']['id']}")
        print_message(f"#{profile_id} Current Level: {response_info['clickerUser']['level']}")
        print_message(f"#{profile_id} Available Tap Sync: {available_tap}")
        print_message(f"#{profile_id} Earn per Tap: {response_info['clickerUser']['earnPerTap']}")
        return response_info
    
    def claim_login():
        print_message(f"#{profile_id} =>Checking Daily Login Info")
        response_info  = session.exec_post(url_check_task, headers=get_header(), data={})
        for task in response_info["tasks"]:
            if task["id"] == "streak_days" and task["isCompleted"] == False:
                sleep(1,3)
                print_message(f"#{profile_id} Daily Login Not Claimed")
                print_message(f"#{profile_id} Claiming Daily Login Rewards")
                payload = {"taskId": "streak_days"}
                response_info = session.exec_post(url_check_in, headers=get_header(content_length= "24"), data=payload)
                day_streak = response_info["task"]["days"]
                for _ in  response_info["task"]["rewardsByDays"]:
                    if _["days"] == day_streak:
                        print_message(f"#{profile_id} Claim Sucess for Streak {day_streak} Days - {_['rewardCoins']} Coin")
            elif task["id"] == "streak_days" and task["isCompleted"] == True:
                print_message(f"#{profile_id} Daily Login Claimed===")
    
    def click(available_tap):
        nonlocal balance
        # print_message("======")
        response_data = session.exec_post(url_tap, headers=get_header(content_length="53"), data={
            "count": random.randint(10, 30),
            "availableTaps": available_tap,
            "timestamp": int(time.time())
        })        
        avai_tap = response_data['clickerUser']['availableTaps']
        balance = round(response_data['clickerUser']['balanceCoins'],0)     
        earn_per_tap = response_data['clickerUser']["earnPerTap"]   
        click_count = round(available_tap/earn_per_tap)+1
        
        print_message(f"#{profile_id} Available Tap: {avai_tap}")
        print_message(f"#{profile_id} Current Coin: {helper.utils.format_number(balance)}")
        return avai_tap
    
    def get_boost():
        def buy_boost(id: str):
            nonlocal balance
            response_info  = session.exec_post(url_buy_boost, headers=get_header(content_length="52"), data={
                "boostId": id,
                "timestamp": int(time.time())
            })
            if response_info is not None:
                print_message(f"#{profile_id}===Get {id} Successed===")
                balance = round(response_info['clickerUser']['balanceCoins'],0)   
            return response_info
        
        multi_tap_level= int(utils.read_config(section='HAMSTER',key='multi_tap_level'))
        energy_level=int(utils.read_config(section='HAMSTER',key='energy_level'))
        print_message(f"#{profile_id} => Getting Boost")
        response_info  = session.exec_post(url_boost, headers=get_header(), data={})
        sleep(3,5)
        boost_list = response_info["boostsForBuy"]
        for element in boost_list:
            if element["id"] == "BoostFullAvailableTaps":
                remain_boost = element["maxLevel"] - element["level"] + 1
                cooldown = element["cooldownSeconds"]
            elif element["id"] == "BoostEarnPerTap":
                if element["level"] < multi_tap_level and balance > element["price"]:
                    print_message(f'#{profile_id} -Buying MultiTapLevel to level {element["level"] + 1} with price: {format_number(element["price"])}')
                    buy_boost("BoostEarnPerTap")
                    sleep(3,5)
            elif element["id"] == "BoostMaxTaps":
                if element["level"] < energy_level and balance > element["price"]:
                    print_message(f'#{profile_id} -Buying EngergyMax to level {element["level"] + 1} with price: {format_number(element["price"])}')
                    buy_boost("BoostMaxTaps")
                    sleep(3,5)                
        if cooldown == 0 and remain_boost>0: 
            response_info  =  buy_boost("BoostFullAvailableTaps") 
            available_tap = response_info['clickerUser']['availableTaps']
            print_message(f"#{profile_id} Available Tap After Boost: {available_tap}")
            return available_tap
        elif cooldown > 0 :
            print_message(f"#{profile_id} NEXT BOOST:", str(int( cooldown//(60*60))).zfill(2) + "H" + str(int( cooldown %(60*60) // 60 )).zfill(2) + "M" + str(int( cooldown %(60*60) % 60 )).zfill(2) + "S")
            return 0
        else:
            print_message(f"#{profile_id} No More Boost Left")
            return 0
    
    def looping_click(available_tap):
        while True:
            remain_tap = click(available_tap)
            sleep(9,15)
            if remain_tap ==0:
                break
    
    def claim_daily_combo():
        print_message(f"#{profile_id} =>Claming daily combo...")
        response_info  = session.exec_post(url_claim_daily_combo, headers=get_header(), data={})
        if response_info is not None:
            print_message(f"#{profile_id} Claimed daily combo success.")
        else:
            print_message(f"#{profile_id} Claimed daily combo failed.")

    def get_list_upgrade():
        print_message(f"#{profile_id} => Getting List Upgrade")
        response_info  = session.exec_post(url_ugrade_for_buy, headers=get_header(), data={})
        return response_info["upgradesForBuy"],response_info["dailyCombo"]
    
    try:
           
        user_data =  get_user_data()     
        claim_login()
        available_tap=user_data['clickerUser']['availableTaps']
        looping_click(available_tap)
        time.sleep(5)
        available_tap = get_boost()
        if available_tap != 0:
            looping_click(available_tap)
        
        for i in range(50):    
            user_data =  get_user_data()   
            current_balance= round(user_data['clickerUser']['balanceCoins'],0)
            list_upgrade_cards,daily_combo = get_list_upgrade()
            if daily_combo['isClaimed']==False:
                daily_combo_cards=[card for card in list_upgrade_cards if card['name'].replace("...","") in input_daily_combo_cards and card['id'] not in daily_combo['upgradeIds']]
                if len(daily_combo_cards)==0 and len(input_daily_combo_cards)!=0:
                    claim_daily_combo()
                else:
                    try:
                        for card in daily_combo_cards:
                            print_message(f"#{profile_id} Try buy card daily event:{card['name']}->> {card['price']}")
                            if current_balance<card['price']:
                                print_message(f"#{profile_id} Not enough money {current_balance} / {card['price']}")
                                break
                            elif card['isAvailable'] == False:
                                print_message(f"#{profile_id} Card {card['name']} is not available")
                                continue
                                #If the combo card not available, process to buy other card.
                            else:      
                                response_info  = session.exec_post(url_buy_upgrade, headers=get_header(content_length="54"), data={
                                    "upgradeId": card['id'],
                                    "timestamp": int(time.time())
                                })
                                if response_info is not None: 
                                    print_message(f"#{profile_id} Buy daily card:Buy success {picked_upgrade_card['name']} with price {picked_upgrade_card['price']}, ROI: {picked_upgrade_card['ROI']}") 
                                else:
                                    print_message(f"#{profile_id} Buy daily card:Buy failed{picked_upgrade_card['name']} with price {picked_upgrade_card['price']}, ROI: {picked_upgrade_card['ROI']}") 
                                    
                            sleep(3,6)
                    except Exception as e:
                        pass
                        # break

            if current_balance<limit_buy_card:
                print_message(f"#{profile_id} Current balance {current_balance} reach LIMIT_BUY_CARD {limit_buy_card}")
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
            
            print_message(f"#{profile_id} Current Balance:{current_balance}")
            if current_balance>picked_upgrade_card['price']:       
                response_info  = session.exec_post(url_buy_upgrade, headers=get_header(content_length="54"), data={
                    "upgradeId": picked_upgrade_card['id'],
                    "timestamp": int(time.time())
                })
                print_message(f"#{profile_id} Bought {picked_upgrade_card['name']} with price {picked_upgrade_card['price']}, ROI: {picked_upgrade_card['ROI']}")
                sleep(2)
            else:
                print_message(f"#{profile_id} Not enough coin for buy {picked_upgrade_card['name']} with price {picked_upgrade_card['price']}, ROI: {picked_upgrade_card['ROI']}")
                break
    except Exception as e:
        print_message(traceback.format_exc())


def main(delay_time,count_processes=2):
    try:
        
        df=pd.read_excel("account.xlsx",dtype={"token":str},sheet_name='hamster')
        df=df[(~df['token'].isna()) & (df['token']!='')]
        df.reset_index(inplace=True)
        if "list_upgrade" not in df.columns:
            df["list_upgrade"] = ""
        if "proxy" not in df.columns:
            df["proxy"] = ""
        df['proxy']=df['proxy'].fillna('')
        df['daily_specical_card']=df['daily_specical_card'].fillna('')
        
        daily_combo_cards=df['daily_specical_card'].fillna(value="").iat[0].split(";")
        profiles=[]
        
        
        for idx,row in df.iterrows():
            profile={
                "id":idx+1,
                "token":row['token'],
                "list_upgrade":row['list_upgrade'],
                "proxy_url":row['proxy'],
                "limit_buy_card":row['limit_buy_card'],
                "input_daily_combo_cards":daily_combo_cards
            }
            profiles.append(profile)
            # exec(profile)
        if count_processes !=1:
            with Pool(count_processes) as p:
                p.map(exec, profiles)
        else:
            for profile in profiles:
                exec(profile)    
        print_message(f"Sleeping {utils.read_config(section="HAMSTER",key= "delay_time_in_minute")} minutes...")
        time.sleep(utils.read_config(section="HAMSTER",key= "delay_time_in_minute"))

    except Exception as e:
        print_message(traceback.format_exc())

if __name__=='__main__':
    count_processes=int(input("Enter number process:"))
    while True:        
        main(delay_time=60,count_processes=count_processes)                      
