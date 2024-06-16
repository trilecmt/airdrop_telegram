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
    # Assuming 'data' is defined somewhere in your Python environment
    match = re.search(r'id%2522%253A(\d+)', url)
    if not match:
        print_message(f"❌ #{profile['name']} Pattern not found")
        return None,None
    uid = match.group(1)
    parsed_url = urllib.parse.urlparse(url)
    query_string = parsed_url.fragment
    query_params = urllib.parse.parse_qs(query_string)
    data = query_params['tgWebAppData'][0]
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
    tap_time=None
    farm_time=None
    try:
        with MySession() as session:
            session.set_proxy(proxy_url=proxy_url)
            response = session.exec_get(url="https://httpbin.org/ip",headers={"content-type": "application/json"})
            if response is None:
                print_message(f"❌ #{profile['name']} Proxy không lấy được IP")
                return tap_time,farm_time
            
            profile_id=f"{profile["name"]}[{response['origin']}]" 

            user_info = session.exec_post(user_info_url,headers=headers,data=payload)
            if user_info is None:
                 print_message(f"❌ #{profile_id} Không lấy được thông tin user.Move next...")     
                 return tap_time,farm_time     
            if user_info["status"] != "ok":
                 print_message(f"❌ #{profile_id} Không lấy được thông tin user.Move next...")   
                 return tap_time,farm_time       
            # if "userTelegramId" in user_info["data"]:
            #     print_message("Id:", user_info["data"]["userTelegramId"])
            # if "username" in user_info["data"]:
            #     print_message("Username:", user_info["data"]["username"])
            # if "balance" in user_info["data"]:
            #     print_message("Balance:", user_info["data"]["balance"])
            if "availableTaps" in user_info["data"]:
                if int(user_info["data"]["availableTaps"]) > 0:
                    print_message("Available Taps:", user_info["data"]["availableTaps"])
                    print_message("-> CLAIMING..")

                    claim_taps_result = session.exec_post(claim_taps_url, headers=headers, data={
                        "devAuthData": uid,
                        "authData": data,
                        "data": {"taps": user_info["data"]["availableTaps"]}
                    })
                    if claim_taps_result is None or claim_taps_result["status"] != "ok":
                        print_message(f"❌ #{profile_id} Không claim thành công.Move next...")   
                        return tap_time,farm_time
                        
                    print_message(f"✅ #{profile_id} Claim  thành công. Số dư { claim_taps_result['data']['balance']}") 
                else:
                     print_message(f"❌ #{profile_id} Không có tap. Số dư { user_info['data']['balance']}") 
                tap_time=(datetime.utcnow()+timedelta(minutes=60))

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
                farm_time=(datetime.strptime(user_info["data"]["farmStartedAt"], format_string)+timedelta(hours=4))
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
            db_profile=schedule.get_profile(game=GAME, profile_name=profile['name'])
            start_time=datetime.utcnow()
            if db_profile is None or db_profile["next_run_date"] < start_time:
                tap_time,farm_time=exec(profile)
                if tap_time is None:
                    tap_time=(datetime.utcnow()+timedelta(minutes=5))
                if farm_time is None:
                    farm_time=(datetime.utcnow()+timedelta(minutes=5))
                schedule_time=min(tap_time,farm_time)
                schedule.update_profile(
                    game=GAME,
                    profile_name=profile["name"],
                    latest_run_date=start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                    next_run_date=schedule_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                )

    except Exception as e:
        print(e)

if __name__=='__main__':
    while True:
        main()       
        for __second in range(60, 0, -1):
            sys.stdout.write(f"\r{Fore.CYAN}Chờ thời gian nhận tiếp theo trong {Fore.CYAN}{Fore.WHITE}{__second // 60} phút {Fore.WHITE}{__second % 60} giây")
            sys.stdout.flush()
            time.sleep(1)
        sys.stdout.write("")
