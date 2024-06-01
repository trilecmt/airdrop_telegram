import time
import pandas as pd
import requests
from pprint import pprint
import json
import helper
import pandas as pd
import random
from helper.helper_session import MySession
from helper.utils import print_message

MINIMUM_BALANCE = 1000000
MAXIMUM_BUGET = 3000000
MINIMUM_RIO = -90
TIME_BUY_UPGRADE = 10

url_boost = "https://api.hamsterkombat.io/clicker/boosts-for-buy"
url_get_info = "https://api.hamsterkombat.io/clicker/sync"        
url_upgrade_for_buy = "https://api.hamsterkombat.io/clicker/upgrades-for-buy"
url_tap = "https://api.hamsterkombat.io/clicker/tap"

"""
    RIO = (Profit After Upgraded - Price to Upgraded) * 100 / Price to Upgrade
"""


def exec(token, list_names: str,proxy_url:str=None):
    session=MySession()
    session.set_proxy(proxy_url)

    list_names = [_.strip() for _ in list_names.split(",") if _ != ""]
    balance = 0
    time_upgraded = 1
    
    def get_header(content_length):
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
        
    def get_remain_available_tap():
        
        response_info  = session.exec_post(url_get_info, headers=get_header(content_length="0"), data={})
        print_message(f"-User Id: {response_info['clickerUser']['id']}")
        print_message(f"-Current Level: {response_info['clickerUser']['level']}")
        available_tap = response_info['clickerUser']['availableTaps']
        print_message(f"-Available Tap Sync: {available_tap}")
        print_message(f"-Earn per Tap: {response_info['clickerUser']['earnPerTap']}")
        return available_tap
    
    def click(available_tap):
        global balance
        print_message("=================")  
        response_data = session.exec_post(url_tap, headers=get_header(content_length="53"), data={
            "count": random.randint(1, 30),
            "availableTaps": available_tap,
            "timestamp": int(time.time())
        })        
        avai_tap = response_data['clickerUser']['availableTaps']
        balance = round(response_data['clickerUser']['balanceCoins'],0)     
        earn_per_tap = response_data['clickerUser']["earnPerTap"]   
        click_count = round(available_tap/earn_per_tap)+1   
        print_message(f"-> Available Tap: {avai_tap}")
        print_message(f"-> Current Coin: {helper.utils.format_number(balance)}")
        return avai_tap
    
    def get_boost():
        print_message("===Getting Boost===")
        response_info  = session.exec_post(url_boost, headers=get_header(content_length="0"), data={})
        boost_list = response_info["boostsForBuy"]
        for element in boost_list:
            if element["id"] == "BoostFullAvailableTaps":
                remain_boost = element["maxLevel"] - element["level"] -1
                cooldown = element["cooldownSeconds"]
        if cooldown == 0 and remain_boost>0:
            url = "https://api.hamsterkombat.io/clicker/buy-boost"
            payload = {
                "boostId": "BoostFullAvailableTaps",
                "timestamp": int(time.time())
            }
            response_info  = session.exec_post(url, headers=get_header(content_length="59"), data=payload)
            available_tap = response_info['clickerUser']['availableTaps']
            print_message(f"Available Tap After Boost: {available_tap}")
            return available_tap
        elif cooldown > 0 :
            print_message("NEXT BOOST:", str(int( cooldown//(60*60))).zfill(2) + "H" + str(int( cooldown %(60*60) // 60 )).zfill(2) + "M" + str(int( cooldown %(60*60) % 60 )).zfill(2) + "S")
            return 0
        else:
            print_message("No More Boost Left")
            return 0
    
    def looping_click(available_tap):
        while True:
            remain_tap = click(available_tap)
            time.sleep(5)
            if remain_tap ==0:
                break
    
    def get_list_upgrade():
        print_message("===Getting List Upgrade===")
        response_info  = session.exec_post(url_upgrade_for_buy, headers=get_header(content_length="0"), data={})
        list_upgrade = response_info["upgradesForBuy"]
        return list_upgrade
    
    def buy_upgrade(list_upgrade, list_names):
        nonlocal  time_upgraded 
        print_message(f"===Buying Upgrade for {time_upgraded} time===")
        list_upgrade = pd.DataFrame(list_upgrade)
        list_upgrade["roi"] = (list_upgrade["profitPerHour"] -list_upgrade["price"] ) *100 / list_upgrade["price"] 
        list_upgrade = list_upgrade[(list_upgrade["price"]<MAXIMUM_BUGET)& (list_upgrade["roi"]> MINIMUM_RIO)  & (list_upgrade["profitPerHourDelta"]!= 0) & (list_upgrade["isExpired"]==False) & (list_upgrade["isAvailable"]==True) & ((list_upgrade["cooldownSeconds"].isna()) | (list_upgrade["cooldownSeconds"]==0))].reset_index(drop=True)
        list_upgrade = list_upgrade[['id','name','price','profitPerHour','profitPerHourDelta','roi']]
        if len(list_names) > 0:
            list_upgrade = list_upgrade[list_upgrade["name"].isin(list_names)]
        list_upgrade.sort_values(["roi"],ascending=False,ignore_index=True,inplace=True)
        if list_upgrade.empty:
            print_message("===No more upgrades available===")
            time_upgraded =11
            return
        list_upgrade = list_upgrade.to_dict("records")
        itemupgrade = list_upgrade[0]
        name = itemupgrade["name"]
        id = itemupgrade["id"]
        price = helper.utils.format_number(itemupgrade["price"])
        profit = helper.utils.format_number(itemupgrade["profitPerHour"])
        profit_increase = helper.utils.format_number(itemupgrade["profitPerHourDelta"])
        roi = round(itemupgrade["roi"],2)
        print_message(f"Buying {name} for {price}, ROI: {roi}, Profit Increased: {profit_increase}. Profit After Ugraded: {profit}")
        url_buy_upgrade = "https://api.hamsterkombat.io/clicker/buy-upgrade"
        payload = {
            "upgradeId": id,
            "timestamp": int(time.time())
        }
        response_info  = helper.post_api(url_buy_upgrade, headers=get_header(content_length="54"), payload=payload)
        balance= helper.utils.format_number(round(response_info["clickerUser"]["balanceCoins"],0))
        passive_earn = helper.utils.format_number(response_info["clickerUser"]["earnPassivePerHour"])
        
        print_message(f"Current Balance: {balance}, Current Passive Earn Per Hour : {passive_earn}")
        time_upgraded +=1
        return response_info["upgradesForBuy"]
            
    try:
        print_message("*********************************************************")        
        available_tap =  get_remain_available_tap()        
        looping_click(available_tap)
        time.sleep(5)
        available_tap = get_boost()
        if available_tap != 0:
            looping_click(available_tap)
        list_upgrade = get_list_upgrade()
        while time_upgraded <= TIME_BUY_UPGRADE:
            list_upgrade = buy_upgrade(list_upgrade,list_names)
            time.sleep(5)        
        
        print("*********************************************************") 
    except Exception as e:
        import traceback
        print_message(traceback.format_exc())
        pass


def main(delay_time):
    try:
        df=pd.read_excel("account.xlsx",dtype={"url":str},sheet_name='hamster')
        df=df[(~df['url'].isna()) & (df['url']!='')]
        df.reset_index(inplace=True)
        if "list_upgrade" not in df.columns:
            df["list_upgrade"] = ""
        if "proxy" not in df.columns:
            df["proxy"] = ""
        df['proxy']=df['proxy'].fillna('')
        for idx,row in df.iterrows():
            exec(row['token'], row['list_upgrade'],proxy_url=row['proxy'])
            time.sleep(10)
            
        time.sleep(delay_time)
    except Exception as e:
        print_message(e)

if __name__=='__main__':
    while True:
        try:
            main(delay_time=60)                      
        except Exception as e:
            print_message(e)