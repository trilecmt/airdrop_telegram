import pandas as pd
import requests
import json
import urllib.parse
import json
import time
import re

user_info_url = "https://cexp.cex.io/api/getUserInfo"
claim_taps_url = "https://cexp.cex.io/api/claimTaps"
claim_farm_url = "https://cexp.cex.io/api/claimFarm"
start_farm_url = "https://cexp.cex.io/api/startFarm"

def exec(url):
    url='https://cexp.cex.io/#tgWebAppData=query_id%3DAAELjJx_AAAAAAuMnH9Whv9r%26user%3D%257B%2522id%2522%253A2140965899%252C%2522first_name%2522%253A%2522Tri%25202%2522%252C%2522last_name%2522%253A%2522Le%2522%252C%2522username%2522%253A%2522trilm208%2522%252C%2522language_code%2522%253A%2522en%2522%252C%2522allows_write_to_pm%2522%253Atrue%257D%26auth_date%3D1716571408%26hash%3Df028ad0ce7070e95c60d119f03b9c1eca8837a3b6b1bab227ea4a902a45f2da2&tgWebAppVersion=7.2&tgWebAppPlatform=ios&tgWebAppThemeParams=%7B%22bg_color%22%3A%22%23ffffff%22%2C%22text_color%22%3A%22%23000000%22%2C%22hint_color%22%3A%22%23707579%22%2C%22link_color%22%3A%22%233390ec%22%2C%22button_color%22%3A%22%233390ec%22%2C%22button_text_color%22%3A%22%23ffffff%22%2C%22secondary_bg_color%22%3A%22%23f4f4f5%22%2C%22header_bg_color%22%3A%22%23ffffff%22%2C%22accent_text_color%22%3A%22%233390ec%22%2C%22section_bg_color%22%3A%22%23ffffff%22%2C%22section_header_text_color%22%3A%22%23707579%22%2C%22subtitle_text_color%22%3A%22%23707579%22%2C%22destructive_text_color%22%3A%22%23e53935%22%7D'
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

    # Define payload for the first POST request
    payload = {
        "devAuthData": uid,
        "authData": data,
        "platform": "android",
        "data": {}
    }

    try:
        # Make the first POST request to get user info
        response = requests.post(user_info_url, headers=headers, data=json.dumps(payload))
        user_info = response.json()

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

        if "farmStartedAt" in user_info["data"] and (int((time.time() * 1000 - int(user_info["data"]["farmStartedAt"])) / 1000) - 14400) > 0:
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
            print("-> CLAIM:", claim_farm_result["data"]["claimedBalance"])
            print("-> BALANCE:", claim_farm_result["data"]["balance"])

        elif "farmStartedAt" in user_info["data"]:
            print("-> Claim After:", str(int((14400 - (int(time.time() * 1000) - int(user_info["data"]["farmStartedAt"])) / 1000) / 60)) + " minutes")

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
        message = f"Error: {str(e)}"
        status = "ERROR!"

    print(message)
    print("Status:", status)
    print(50*"*")
    print(50*"")

if __name__=='__main__':
    delay_time=input("Enter delay time:...")
    while True:
        try:
            df=pd.read_excel("account-cexp.xlsx",dtype={"url":str},sheet_name='cexp')
            df=df[(~df['url'].isna()) & (df['url']!='')]
            df.reset_index(inplace=True)
            for idx,row in df.iterrows():
                exec(row['url'])
                time.sleep(delay_time)
                             
        except Exception as e:
            print(e)
