import pandas as pd
import urllib.parse
import time
import re
from datetime import datetime,timedelta
import traceback
import helper
from helper.helper_session import MySession
from helper.utils import print_message

user_info_url = "https://cexp.cex.io/api/getUserInfo"
claim_taps_url = "https://cexp.cex.io/api/claimTaps"
claim_farm_url = "https://cexp.cex.io/api/claimFarm"
start_farm_url = "https://cexp.cex.io/api/startFarm"
format_string = "%Y-%m-%dT%H:%M:%S.%fZ"

  
def exec(url,proxy_url):
    if url is None:
        return
    print_message(50*"*")
    # Assuming 'data' is defined somewhere in your Python environment
    match = re.search(r'id%2522%253A(\d+)', url)
    if not match:
        print_message("Pattern not found")
        return 
    uid = match.group(1)
    print_message(f"Process {uid}")
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

    try:
        with MySession() as session:
            session.set_proxy(proxy_url=proxy_url)
            user_info = session.exec_post(user_info_url,headers=headers,data=payload)
            if user_info is None:
                return
            
            if user_info["status"] != "ok":
                raise ValueError("Error: Couldn't fetch user data")
            if "userTelegramId" in user_info["data"]:
                print_message("Id:", user_info["data"]["userTelegramId"])
            if "username" in user_info["data"]:
                print_message("Username:", user_info["data"]["username"])
            if "balance" in user_info["data"]:
                print_message("Balance:", user_info["data"]["balance"])
            if "availableTaps" in user_info["data"] and int(user_info["data"]["availableTaps"]) > 0:
                print_message("Available Taps:", user_info["data"]["availableTaps"])
                print_message("-> CLAIMING..")

                claim_taps_result = session.exec_post(claim_taps_url, headers=headers, data={
                    "devAuthData": uid,
                    "authData": data,
                    "data": {"taps": user_info["data"]["availableTaps"]}
                })
                if claim_taps_result["status"] != "ok":
                    raise ValueError("Error: Couldn't claim taps")

                print_message("-> CLAIM SUCCESS!")
                print_message("BALANCE:", claim_taps_result["data"]["balance"])
                user_info["data"]["currentTapWindowFinishIn"] = claim_taps_result["data"]["currentTapWindowFinishIn"]

            else:
                print_message("-> NO TAPS")

            print_message("NEXT CLAIM:", str(int(user_info["data"]["currentTapWindowFinishIn"]) // 1000 // 3600) + "H" + str(int(user_info["data"]["currentTapWindowFinishIn"]) // 1000 % 60) + "M")
            print_message("FARM REWARD:", user_info["data"]["farmReward"])
            print_message("FARMING")
            
            if "farmStartedAt" in user_info["data"] and datetime.utcnow()> (datetime.strptime(user_info["data"]["farmStartedAt"], format_string)+timedelta(hours=4)):
                print_message("-> CLAIMING")
                claim_farm_result = session.exec_post(claim_farm_url, headers=headers, data={
                    "devAuthData": uid,
                    "authData": data,
                    "data": {}
                })
                if "status" in claim_farm_result and claim_farm_result["status"] != "ok":
                    print_message("Error: Couldn't claim farm")
                    raise ValueError("Error: Couldn't claim farm")

                claim_farm_result["data"]["farmReward"] = "0.00"
                user_info["data"]["farmReward"]= "0.00"
                print_message("-> CLAIM:", claim_farm_result["data"]["claimedBalance"])
                print_message("-> BALANCE:", claim_farm_result["data"]["balance"])

            elif "farmStartedAt" in user_info["data"]:
                print_message(f'-> Claim After:  {int(((datetime.strptime(user_info["data"]["farmStartedAt"], format_string)+timedelta(hours=4))-datetime.utcnow()).total_seconds()/60)} minutes')

            if "farmReward" in user_info["data"] and user_info["data"]["farmReward"] == "0.00":
                print_message("-> FARM: STARTING")
                start_farm_result = session.exec_post(start_farm_url, headers=headers, data={
                    "devAuthData": uid,
                    "authData": data,
                    "data": {}
                })
                if "status" in start_farm_result and start_farm_result["status"] != "ok":
                    raise ValueError("Error: Couldn't start farm")

                print_message("-> FARMING")
                print_message("->", start_farm_result["data"]["farmReward"])

    except Exception as e:  
        print_message(traceback.format_exc())
        print_message("Status:ERROR!")

    
    print_message(50*"*")
    print_message(50*"")


def main(delay_time):
    try:
        df=pd.read_excel("account.xlsx",dtype={"url":str},sheet_name='cexp')
        df=df[(~df['url'].isna()) & (df['url']!='')]
        df.reset_index(inplace=True)
        for idx,row in df.iterrows():
            exec(row['url'],row['proxy'])
            time.sleep(10)
        
        time.sleep(delay_time)
    except Exception as e:
        print(e)

if __name__=='__main__':
    while True:
        try:
            main(delay_time=60)                      
        except Exception as e:
            print(e)
