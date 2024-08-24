import random
import sys
import pandas as pd
import urllib.parse
import time
import re
from datetime import datetime,timedelta
import traceback
import helper
from helper.helper_session import MySession
from helper.utils import print_message


from colorama import init, Fore, Style
init(autoreset=True)

GAME='CEXP'

from helper.helper_schedule import ScheduleDB

schedule=ScheduleDB()

user_info_url = "https://cexp.cex.io/api/getUserInfo"
claim_taps_url = "https://cexp.cex.io/api/claimTaps"
claim_farm_url = "https://cexp.cex.io/api/claimFarm"
start_farm_url = "https://cexp.cex.io/api/startFarm"
format_string = "%Y-%m-%dT%H:%M:%S.%fZ"

  
def exec(profile):
    url,proxy_url=profile['url'],profile['proxy']
    if url is None:
        return None,None
    match = re.search(r'id%2522%253A(\d+)', url)
    if not match:
        match = re.search(r'id%22%3A(\d+)', url)
        if not match:
            print_message(f"❌ #{profile['name']} Pattern not found")
            return None,None
    uid = match.group(1)
    parsed_url = urllib.parse.urlparse(url)
    
    query_string = parsed_url.fragment
    query_params = urllib.parse.parse_qs(query_string)
    if len(query_params)==4:
        data=query_params['tgWebAppData'][0]
    else:
        data =query_string.split("tgWebAppData=")[1].split("&tgWebAppVersion")[0]# query_params['tgWebAppData'][0]
    # Define headers
    headers = {
        "content-type": "application/json"
    }
    payload = {
        "devAuthData": uid,
        "authData": data,
        "platform": "android",
        "data": {}
    }
    try:
        with MySession() as session:
            session.set_proxy(proxy_url=proxy_url)
            response = session.exec_get(url="https://httpbin.org/ip",headers={"content-type": "application/json"})
            if response is None:
                print_message(f"❌ #{profile['name']} Proxy không lấy được IP")
                return
            
            profile_id=f"{profile["name"]}[{response['origin']}]" 
            user_info = session.exec_post(user_info_url,headers=headers,data=payload)
            if user_info is None:
                 print_message(f"❌ #{profile_id} Không lấy được thông tin user.Move next...")     
                 return 
            if user_info["status"] != "ok":
                 print_message(f"❌ #{profile_id} Không lấy được thông tin user.Move next...")   
                 return


            def buy_upgrade():
                user_info = session.exec_post(user_info_url,headers=headers,data=payload)
                if user_info is None or user_info["status"] != "ok":
                    print_message(f"❌ #{profile_id} Không lấy được thông tin user.Move next...")     
                    return False
                current_balance=float(user_info["data"].get("balance_USD"))
                game_config = session.exec_post("https://cexp.cex.io/api/v2/getGameConfig",headers=headers,data=payload)
                user_card_response=session.exec_post("https://cexp.cex.io/api/v2/getUserCards",headers=headers,data=payload)
                upgrade_cards_config=game_config["upgradeCardsConfig"]
                
                user_cards=[]
                for user_card in user_card_response['cards']:
                    user_cards.append({
                        "upgradeId":user_card,
                        "level":user_card_response['cards'].get(user_card).get("lvl"),
                        "profit":user_card_response['cards'].get(user_card).get("totalCEXP")
                    })

                cards = []
                for card in upgrade_cards_config:
                    for sub_card in card.get('upgrades', []):  
                        if sub_card.get("levels")==[]:
                            continue
                        level=0
                        if sub_card.get("upgradeId") in [user_card['upgradeId'] for user_card in user_cards]:
                            level=[user_card['level'] for user_card in user_cards if user_card['upgradeId']==sub_card.get("upgradeId")][0]
                        if level==len(sub_card['levels']):
                            continue
                        cards.append({
                            "dependency":sub_card.get("dependency"),
                            "upgradeId":sub_card.get("upgradeId"),
                            "categoryId":card.get("categoryId"),
                            "level":level,
                            "cost":sub_card.get("levels")[level][0],
                            "ccy":sub_card.get("levels")[level][1],
                            "effect":sub_card.get("levels")[level][2],
                            "effectCcy":sub_card.get("levels")[level][3],
                            "roi":sub_card.get("levels")[level][2]/sub_card.get("levels")[level][0]
                        })
                if len(cards)==0:
                    print_message(f"❌ #{profile_id} Không có card để mua.Move next...")
                    return False
                
                for card in cards:
                    if card['dependency']=={}:
                        continue
                    if card['upgradeId']=='poolFees':
                        pass
                    if "upgradeId" in card['dependency']:
                       
                        required_card=card['dependency']['upgradeId']
                        required_level=card['dependency']['level']
                        if len([card for card in cards if card['upgradeId']==required_card and card['level']>=required_level])==0:
                            card['is_available']=False
                available_cards = [card for card in cards if card.get("is_available",True) and current_balance>=card['cost']]
                available_cards = sorted(available_cards, key=lambda x: x['roi'], reverse=True)
                for picked_card in available_cards:
                    # if current_balance<picked_card['cost']:
                    #     print_message(f"❌ #{profile_id} Không đủ tiền mua card {picked_card['upgradeId']} cần {picked_card['cost']}/{current_balance}.Move next...")   
                    #     continue
                    add_payload=payload.copy()
                    add_payload["data"]={
                        "categoryId":picked_card['categoryId'],
                        "ccy":picked_card['ccy'],
                        "cost":picked_card['cost'],
                        "effect":picked_card['effect'],
                        "effectCcy":picked_card['effectCcy'],
                        "nextLevel":picked_card['level']+1,
                        "upgradeId":picked_card['upgradeId']
                    }
                    buy_card_response=session.exec_post("https://cexp.cex.io/api/v2/buyUpgrade",headers=headers,data=add_payload,log=True)
                    if buy_card_response is None or buy_card_response["status"] != "ok":
                        print_message(f"❌ #{profile_id} Không mua được card {picked_card['upgradeId']}.Move next...")   
                        return False
                    else:
                        print_message(f"✅ #{profile_id} Mua card {picked_card['upgradeId']} thành công")
                        return True
            

            def swap_btc():
                try:
                    user_info = session.exec_post(user_info_url,headers=headers,data=payload)
                    if user_info is None or user_info["status"] != "ok":
                        print_message(f"❌ #{profile_id} Không lấy được thông tin user.Move next...")     
                        return
                    current_balance=float(user_info["data"].get("balance_BTC")) / (10 ** user_info["data"].get("precision_BTC"))
                    convert_data_response=session.exec_post("https://cexp.cex.io/api/v2/getConvertData",headers=headers,data=payload)
                    if convert_data_response is None or convert_data_response["status"] != "ok":
                        print_message(f"❌ #{profile_id} Không lấy được thông tin convert.Move next...")   
                        return
                  
                    copy_payload=payload.copy()
                    copy_payload["data"]={  
                        "fromAmount":round(current_balance*0.9,4),
                        "fromCcy":"BTC",
                        "price":convert_data_response["convertData"]["lastPrices"][-1],
                        "toCcy":"USD"
                    }
                    convert_data_response=session.exec_post("https://cexp.cex.io/api/v2/convert",headers=headers,data=copy_payload,log=True)
                    if convert_data_response is None or convert_data_response["status"] != "ok":
                        print_message(f"❌ #{profile_id} Không lấy được thông tin convert.Move next...")   
                        return
                    else:
                        print_message(f"✅ #{profile_id} Convert {round(current_balance*0.9,4)} BTC thành công")
                    
                except Exception as e:
                    print_message(f"❌ #{profile_id} Không lấy được thông tin convert.Move next...")   
                    return False

            def claim_from_ref():
                try:
                    user_info = session.exec_post("https://cexp.cex.io/api/v2/claimFromChildren",headers=headers,data=payload)
                    if user_info is None or user_info["status"] != "ok":
                        print_message(f"❌ #{profile_id} Không lấy được thông tin user.Move next...")     
                        return
                    print_message(f"✅ #{profile_id} Claim từ ref thành công")
                except Exception as e:
                    print_message(f"❌ #{profile_id} Không lấy được thông tin user.Move next...")   
                    return

            claim_from_ref()
            swap_btc()
            while buy_upgrade()==True:
                print_message(f"✅ #{profile_id} Chuyển mua card tiếp theo...")

            #claim
            claim_response=session.exec_post("https://cexp.cex.io/api/v2/claimCrypto",headers=headers,data=payload)
            if claim_response is None or claim_response["status"] != "ok":
                print_message(f"❌ #{profile_id} Không claim được.Move next...")   
                return None
            print_message(f"✅ #{profile_id} Claim thành công. Balance= {claim_response['data']['BTC']['balance_BTC']} BTC") 
            
                # copy_payload=payload.copy()
                # copy_payload["data"]={
                #     "tapsEnergy": "912",
                #     "tapsToClaim": "184",
                #     "tapsTs": int(datetime.now().timestamp())*1000
                # }
                # claim_response=session.exec_post("https://cexp.cex.io/api/v2/claimMultiTaps",headers=headers,data=copy_payload,log=True)
                # if claim_response is None or claim_response["status"] != "ok":
                #     print_message(f"❌ #{profile_id} Không claim được.Move next...")   
                #     return None
                # print_message(f"✅ #{profile_id} Claim thành công. Balance= {claim_response['data']['BTC']['balance_BTC']} BTC") 
            # tap()
            
            # else:
            #     print_message(f"❌ #{profile_id} Không tap thành công.")   
            #     tap_time=int((datetime.utcnow()+timedelta(minutes=5)).timestamp())
            # else:
            #     print_message("-> NO TAPS")
            # tap_time=int(user_info["data"]["currentTapWindowFinishIn"])
            # print_message(f"✅ #{profile_id} NEXT CLAIM:", str(int(user_info["data"]["currentTapWindowFinishIn"]) // 1000 // 3600) + "H" + str(int(user_info["data"]["currentTapWindowFinishIn"]) // 1000 % 60) + "M")
            
            # print_message(f"✅ #{profile_id} FARM REWARD:", user_info["data"]["farmReward"])
            # print_message(f"✅ #{profile_id} FARMING")
            
            if "farmStartedAt" in user_info["data"] and datetime.utcnow()> (datetime.strptime(user_info["data"]["farmStartedAt"], format_string)+timedelta(hours=4)):
                claim_farm_result = session.exec_post(claim_farm_url, headers=headers, data={
                    "devAuthData": uid,
                    "authData": data,
                    "data": {}
                })
                if claim_farm_result is None or ("status" in claim_farm_result and claim_farm_result["status"] != "ok"):
                    print_message(f"❌ #{profile_id} farm lỗi.Move next...")   
                    return tap_time,farm_time
                
                # claim_farm_result["data"]["farmReward"] = "0.00"
                user_info["data"]["farmReward"]= "0.00"
                print_message(f"✅ #{profile_id} CLAIM: {claim_farm_result['data']['claimedBalance']}, BALANCE:{claim_farm_result['data']['balance']}")
            elif "farmStartedAt" in user_info["data"]:
                farm_time=(datetime.strptime(user_info["data"]["farmStartedAt"], format_string)+timedelta(hours=4))
                print_message(f'❌ #{profile_id} Farm :  {int(((datetime.strptime(user_info["data"]["farmStartedAt"], format_string)+timedelta(hours=4))-datetime.utcnow()).total_seconds()/60)} minutes')

            if "farmReward" in user_info["data"] and user_info["data"]["farmReward"] == "0.00":
                start_farm_result = session.exec_post(start_farm_url, headers=headers, data={
                    "devAuthData": uid,
                    "authData": data,
                    "data": {}
                })
                if start_farm_result is None or ("status" in start_farm_result and start_farm_result["status"] != "ok"):
                    print_message(f"❌ #{profile_id} farm lỗi.Move next...")  
                    return tap_time,farm_time
                print_message(f"✅ #{profile_id} FARM: {start_farm_result['data']['farmReward']}")
                farm_time=None# (datetime.strptime(user_info["data"]["farmStartedAt"], format_string)+timedelta(hours=4))
        return tap_time,farm_time

    except Exception as e:  
        print_message(f"✅ #{profile_id} Status:ERROR!")
        print_message(traceback.format_exc())
        return None,None


def main():
    try:
        df=pd.read_excel("account.xlsx",dtype={"url":str,'name':str},sheet_name='cexp')
        df=df[(~df['url'].isna()) & (df['url']!='')]
        df["proxy"] = df["proxy"].fillna(value="")
        df.reset_index(inplace=True)
        for idx,row in df.iterrows():
            profile={
                "id":idx+1,
                "name":str(row["profile"]),
                "url":row["url"],
                "proxy":row["proxy"]
            }    

            exec(profile)  
            # db_profile=schedule.get_profile(game=GAME, profile_name=profile['name'])
            # start_time=datetime.utcnow()
            # if db_profile is None or db_profile["next_run_date"] < start_time:
            #     tap_time,farm_time=exec(profile)
            #     if tap_time is None:
            #         tap_time=(datetime.utcnow()+timedelta(minutes=5))
            #     if farm_time is None:
            #         farm_time=(datetime.utcnow()+timedelta(minutes=5))
            #     schedule_time=min(tap_time,farm_time)
                # schedule.update_profile(
                #     game=GAME,
                #     profile_name=profile["name"],
                #     latest_run_date=start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                #     next_run_date=schedule_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                # )

    except Exception as e:
        print(e)

if __name__=='__main__':
    delay_min= 30#int(input("Nhập thời gian nghỉ (phút):"))
    while True:
        main()       
        for __second in range(delay_min*60, 0, -1):
            sys.stdout.write(f"\r{Fore.CYAN}Chờ thời gian nhận tiếp theo trong {Fore.CYAN}{Fore.WHITE}{__second // 60} phút {Fore.WHITE}{__second % 60} giây")
            sys.stdout.flush()
            time.sleep(1)
        sys.stdout.write("")
