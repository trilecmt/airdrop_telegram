import time
import requests
import brotli
from pprint import pprint
import json
import helper
import numpy as np
import random

def exec(token):
    headers_info = {
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Content-Length": "0",
            "Host": "api.hamsterkombat.io",
            "Origin": "https://hamsterkombat.io",
            "Referer": "https://hamsterkombat.io/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Authorization": f"Bearer {token}",
        }
    
    def get_remain_available_tap():
        url_get_info = "https://api.hamsterkombat.io/clicker/sync"        
        response_info  = helper.post_api(url_get_info, headers=headers_info, payload={})
        available_tap = response_info['clickerUser']['availableTaps']
        print(f"Available Tap Sync: {available_tap}")
        earn_per_tap = response_info['clickerUser']["earnPerTap"]
        click_count = round(available_tap/earn_per_tap)+1
        return click_count, available_tap
    
    
    
    def click(click_count, available_tap):
        print("=================")
        url = "https://api.hamsterkombat.io/clicker/tap"
        headers = {
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
            "Connection": "keep-alive",
            "Content-Length": "53",
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
        
        payload = {
            "count": random.randint(1, click_count),
            "availableTaps": available_tap,
            "timestamp": int(time.time())
        }
        
        response_data = helper.post_api(url, headers=headers, payload=payload)        

        id = response_data['clickerUser']['id']
        lvl = response_data['clickerUser']['level']
        avai_tap = response_data['clickerUser']['availableTaps']
        balance = round(response_data['clickerUser']['balanceCoins'],0)     
        earn_per_tap = response_data['clickerUser']["earnPerTap"]   
        click_count = round(available_tap/earn_per_tap)+1
        print(f"User Id: {id}")
        print(f"Current Level: {lvl}")
        print(f"Available Tap: {avai_tap}")
        print(f"Current Coin: {balance}")
        return avai_tap
    
    def get_boost():
        print("===Getting Boost===")
        url_boost = "https://api.hamsterkombat.io/clicker/boosts-for-buy"
        
        response_info  = helper.post_api(url_boost, headers=headers_info, payload={})
        boost_list = response_info["boostsForBuy"]
        for element in boost_list:
            if element["id"] == "BoostFullAvailableTaps":
                remain_boost = element["maxLevel"] - element["level"] -1
                cooldown = element["cooldownSeconds"]
        if cooldown == 0 and remain_boost>0:
            url = "https://api.hamsterkombat.io/clicker/buy-boost"
            headers = {
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "en-US,en;q=0.9",
                "Connection": "keep-alive",
                "Content-Length": "59",
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
            }
            payload = {
                "boostId": "BoostFullAvailableTaps",
                "timestamp": int(time.time())
            }
            response_info  = helper.post_api(url_boost, headers=headers, payload=payload)
            available_tap = response_info['clickerUser']['availableTaps']
            print(f"Available Tap After Boost: {available_tap}")
            earn_per_tap = response_info['clickerUser']["earnPerTap"]
            click_count = round(available_tap/earn_per_tap)+1
            return click_count, available_tap
        elif cooldown > 0 :
            print("NEXT BOOST:", str(int( cooldown//(60*60))).zfill(2) + "H" + str(int( cooldown %(60*60) // 60 )).zfill(2) + "M" + str(int( cooldown %(60*60) % 60 )).zfill(2) + "S")
            return 0,0
        else:
            print("No More Boost Left")
            return 0,0
    
    def looping_click(available_tap, click_count):
        while True:
            remain_tap = click(available_tap, click_count)
            time.sleep(2)
            if remain_tap ==0:
                break
    
    try:
        print("*********************************************************")        
        click_count, available_tap =  get_remain_available_tap()        
        looping_click(available_tap, click_count)
        time.sleep(5)
        click_count, available_tap = get_boost()
        if click_count != 0:
            looping_click(available_tap, click_count)        
        print("*********************************************************")

        
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        pass

if __name__=="__main__":
    while True:
        exec(token='1717072879997cx0e93iKMY6FncfQfl7LXxSXon5gAAx9lFiXs0iCAdJCs5S8h7BennGLOwoFwmAE1266458602')
        time.sleep(120)