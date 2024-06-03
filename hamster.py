import time
import pandas as pd
from pprint import pprint
import json
import helper
import pandas as pd
import random
from helper.helper_session import MySession
from helper.utils import print_message, sleep

url_get_info = "https://api.hamsterkombat.io/clicker/sync"    
url_boost = "https://api.hamsterkombat.io/clicker/boosts-for-buy"
url_tap = "https://api.hamsterkombat.io/clicker/tap"
url_buy_boost = "https://api.hamsterkombat.io/clicker/buy-boost"
url_ugrade_for_buy = "https://api.hamsterkombat.io/clicker/upgrades-for-buy"
url_buy_upgrade = "https://api.hamsterkombat.io/clicker/buy-upgrade"
url_claim_daily_combo="https://api.hamsterkombat.io/clicker/claim-daily-combo"

def exec(token, list_names: str,proxy_url:str,limit_buy_card:int,input_daily_combo_cards:list):
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
        
    def get_user_data():
        response_info  = session.exec_post(url_get_info, headers=get_header(content_length="0"), data={})
        available_tap = response_info['clickerUser']['availableTaps']
        print_message(f"User Id: {response_info['clickerUser']['id']}")
        print_message(f"Current Level: {response_info['clickerUser']['level']}")
        print_message(f"Available Tap Sync: {available_tap}")
        print_message(f"Earn per Tap: {response_info['clickerUser']['earnPerTap']}")
        return response_info
    
    def click(available_tap):
        global balance
        print_message("=================")
        
        response_data = session.exec_post(url_tap, headers=get_header(content_length="53"), data={
            "count": random.randint(10, 30),
            "availableTaps": available_tap,
            "timestamp": int(time.time())
        })        
        avai_tap = response_data['clickerUser']['availableTaps']
        balance = round(response_data['clickerUser']['balanceCoins'],0)     
        earn_per_tap = response_data['clickerUser']["earnPerTap"]   
        click_count = round(available_tap/earn_per_tap)+1
        
        print_message(f"Available Tap: {avai_tap}")
        print_message(f"Current Coin: {helper.utils.format_number(balance)}")
        return avai_tap
    
    def get_boost():
        print_message("===Getting Boost===")
        response_info  = session.exec_post(url_boost, headers=get_header(content_length="0"), data={})
        boost_list = response_info["boostsForBuy"]
        for element in boost_list:
            if element["id"] == "BoostFullAvailableTaps":
                remain_boost = element["maxLevel"] - element["level"] + 1
                cooldown = element["cooldownSeconds"]
        if cooldown == 0 and remain_boost>0: 
            response_info  = session.exec_post(url_buy_boost, headers=get_header(content_length="59"), data={
                "boostId": "BoostFullAvailableTaps",
                "timestamp": int(time.time())
            })
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
    
    def claim_daily_combo():
        print_message("Claming daily combo...")
        response_info  = session.exec_post(url_claim_daily_combo, headers=get_header(content_length="0"), data={})
        if response_info is not None:
            print_message("Claimed daily combo success.")
        else:
            print_message("Claimed daily combo failed.")

    def get_list_upgrade():
        print_message("===Getting List Upgrade===")
        response_info  = session.exec_post(url_ugrade_for_buy, headers=get_header(content_length="0"), data={})
        return response_info["upgradesForBuy"],response_info["dailyCombo"]
    
    try:
        print_message("*********************************************************")        
        user_data =  get_user_data()     
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
                            print_message(f"Try buy card daily event:{card['name']}->> {card['price']}")
                            if current_balance<card['price']:
                                print_message(f"Not enough money {current_balance} / {card['price']}")
                                break
                            elif card['isAvailable'] == False:
                                print_message(f"Card {card['name']} is not available")
                                continue
                                #If the combo card not available, process to buy other card.
                            else:      
                                response_info  = session.exec_post(url_buy_upgrade, headers=get_header(content_length="54"), data={
                                    "upgradeId": card['id'],
                                    "timestamp": int(time.time())
                                })
                                if response_info is not None: 
                                    print_message(f"Buy daily card:Buy success {picked_upgrade_card['name']} with price {picked_upgrade_card['price']}, ROI: {picked_upgrade_card['ROI']}") 
                                else:
                                    print_message(f"Buy daily card:Buy failed{picked_upgrade_card['name']} with price {picked_upgrade_card['price']}, ROI: {picked_upgrade_card['ROI']}") 
                                    
                            sleep(3,6)
                    except Exception as e:
                        pass
                        # break

            if current_balance<limit_buy_card:
                print_message(f"Current balance {current_balance} reach LIMIT_BUY_CARD {limit_buy_card}")
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
            
            print_message(f"Current Balance:{current_balance}")
            if current_balance>picked_upgrade_card['price']:       
                response_info  = session.exec_post(url_buy_upgrade, headers=get_header(content_length="54"), data={
                    "upgradeId": picked_upgrade_card['id'],
                    "timestamp": int(time.time())
                })
                print_message(f"Bought {picked_upgrade_card['name']} with price {picked_upgrade_card['price']}, ROI: {picked_upgrade_card['ROI']}")
                sleep(2)
            else:
                print_message(f"Not enough coin for buy {picked_upgrade_card['name']} with price {picked_upgrade_card['price']}, ROI: {picked_upgrade_card['ROI']}")
                break
          
        print_message("*********************************************************")
 
    except Exception as e:
        import traceback
        print_message(traceback.format_exc())


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
        daily_combo_cards=df['daily_specical_card'].fillna(value="").iat[0].split(";")
        for idx,row in df.iterrows():
            exec(row['token'], row['list_upgrade'],proxy_url=row['proxy'],limit_buy_card=row['limit_buy_card'],input_daily_combo_cards=daily_combo_cards)
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