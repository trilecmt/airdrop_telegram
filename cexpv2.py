import pandas as pd
import requests
import json
import urllib.parse
import json
import time
import re
from datetime import datetime,timedelta
import traceback

user_info_url = "https://cexp.cex.io/api/getUserInfo"
claim_taps_url = "https://cexp.cex.io/api/claimTaps"
claim_farm_url = "https://cexp.cex.io/api/claimFarm"
start_farm_url = "https://cexp.cex.io/api/startFarm"
format_string = "%Y-%m-%dT%H:%M:%S.%fZ"

  
def exec(url,proxy_url):
    if url is None:
        return
    print(50*"*")
    # Assuming 'data' is defined somewhere in your Python environment
    match = re.search(r'id%2522%253A(\d+)', url)
    if not match:
        print("Pattern not found")
        return 
    uid = match.group(1)
    print(f"Process {uid}")
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
        with requests.Session() as session:
            if proxy_url is not None and proxy_url!='':  
                session.proxies= {
                    'http':proxy_url,
                    'https':proxy_url
                }
                print('changed proxy...')
            response = session.post("https://api.myip.com/",timeout=10, headers=headers,data=json.dumps(payload))
            print(f"my ip:{response.json()['ip']}")
            response = session.post(user_info_url,timeout=10, headers=headers,data=json.dumps(payload))
            user_info = response.json()
            print(f"app ip:{response.json()['data']['ip']}")
            
 
            if user_info["status"] != "ok":
                print("Error: Couldn't fetch user data")
                raise ValueError("Error: Couldn't fetch user data")

            if "userTelegramId" in user_info["data"]:
                print("Account:", user_info["data"]["userTelegramId"])

            if "username" in user_info["data"]:
                print("Username:", user_info["data"]["username"])

            if "balance" in user_info["data"]:
                print("Balance:", user_info["data"]["balance"])

            if "availableTaps" in user_info["data"] and int(user_info["data"]["availableTaps"]) > 0:
                print("Available Taps:", user_info["data"]["availableTaps"])
                print("-> CLAIMING..")

                claim_taps_url = "https://cexp.cex.io/api/claimTaps"
                claim_taps_payload = {
                    "devAuthData": uid,
                    "authData": data,
                    "data": {"taps": user_info["data"]["availableTaps"]}
                }
                response = requests.post(claim_taps_url, headers=headers, data=json.dumps(claim_taps_payload))
                claim_taps_result = response.json()

                if claim_taps_result["status"] != "ok":
                    print("Error: Couldn't claim taps")
                    raise ValueError("Error: Couldn't claim taps")

                print("-> CLAIM SUCCESS!")
                print("BALANCE:", claim_taps_result["data"]["balance"])
                user_info["data"]["currentTapWindowFinishIn"] = claim_taps_result["data"]["currentTapWindowFinishIn"]

            else:
                print("No taps to claim!")

            print("NEXT CLAIM:", str(int(user_info["data"]["currentTapWindowFinishIn"]) // 1000 // 3600) + "H" + str(int(user_info["data"]["currentTapWindowFinishIn"]) // 1000 % 60) + "M")
            print("FARM REWARD:", user_info["data"]["farmReward"])
            print("FARMING")
            
            if "farmStartedAt" in user_info["data"] and datetime.utcnow()> (datetime.strptime(user_info["data"]["farmStartedAt"], format_string)+timedelta(hours=4)):
                print("-> CLAIMING")
                claim_farm_url = "https://cexp.cex.io/api/claimFarm"
                claim_farm_payload = {
                    "devAuthData": uid,
                    "authData": data,
                    "data": {}
                }
                response = requests.post(claim_farm_url, headers=headers, data=json.dumps(claim_farm_payload))
                claim_farm_result = response.json()

                if "status" in claim_farm_result and claim_farm_result["status"] != "ok":
                    print("Error: Couldn't claim farm")
                    raise ValueError("Error: Couldn't claim farm")

                claim_farm_result["data"]["farmReward"] = "0.00"
                user_info["data"]["farmReward"]= "0.00"
                print("-> CLAIM:", claim_farm_result["data"]["claimedBalance"])
                print("-> BALANCE:", claim_farm_result["data"]["balance"])

            elif "farmStartedAt" in user_info["data"]:
                print(f'-> Claim After:  {int(((datetime.strptime(user_info["data"]["farmStartedAt"], format_string)+timedelta(hours=4))-datetime.utcnow()).total_seconds()/60)} minutes')

            if "farmReward" in user_info["data"] and user_info["data"]["farmReward"] == "0.00":
                print("-> FARM: STARTING")

                start_farm_url = "https://cexp.cex.io/api/startFarm"
                start_farm_payload = {
                    "devAuthData": uid,
                    "authData": data,
                    "data": {}
                }
                response = requests.post(start_farm_url, headers=headers, data=json.dumps(start_farm_payload))
                start_farm_result = response.json()

                if "status" in start_farm_result and start_farm_result["status"] != "ok":
                    print("Error: Couldn't start farm")
                    raise ValueError("Error: Couldn't start farm")

                print("-> FARMING")
                print("->", start_farm_result["data"]["farmReward"])

    except Exception as e:
        
        print(traceback.format_exc())
        print("Status:ERROR!")

    
    print(50*"*")
    print(50*"")


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
