import time
import pandas as pd
import requests
from pprint import pprint
import json
import helper
import random
import traceback
from helper.helper_session import MySession
from helper.utils import print_message, sleep, format_number, get_query_id
from datetime import datetime, timedelta

def exec(profile_url, proxy_url:str):
    session=MySession()
    session.set_proxy(proxy_url)
    url_api= "https://api.gamee.com/"
    token = ""   
    
    try:
        query_id = get_query_id(profile_url)
        header_login = {
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9",
            "Client-Language": "en",        
            "Origin": "https://prizes.gamee.com",
            "Referer": "https://prizes.gamee.com/",
            "Sec-Fetch-Dest": "empty",
            "Content-Length" : "480",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Content-Type": "text/plain;charset=UTF-8",
            "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="24"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "X-Install-Uuid" : "07d3e518-03e2-4646-8dc0-a2beb7e4f0b2"
        }   
        payload = {
            "id": "user.authentication.loginUsingTelegram",
            "jsonrpc": "2.0",
            "method": "user.authentication.loginUsingTelegram",
            "params": {"initData": query_id},
        }
        response_data = session.exec_post(url_api, headers=header_login, data=payload)
        
        if response_data is not None:
            print_message("Id:", response_data["result"]["user"]["id"])
            print_message("Name:", response_data["result"]["user"]["personal"]["firstname"] + " " + response_data["result"]["user"]["personal"]["lastname"] )
            token = response_data["result"]["tokens"]["authenticate"]
            sleep(2)            
        else:
            raise("===Cannot Get User Token====")
        
        header = {
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9",
            "Client-Language": "en",        
            "Origin": "https://prizes.gamee.com",
            "Referer": "https://prizes.gamee.com/",
            "Sec-Fetch-Dest": "empty",
            "Content-Length" : "480",
            "Sec-Fetch-Mode": "cors",
            "Authorization": f"Bearer {token}",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Content-Type": "text/plain;charset=UTF-8",
            "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="24"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "X-Install-Uuid" : "07d3e518-03e2-4646-8dc0-a2beb7e4f0b2"
        }
        payload = {"jsonrpc":"2.0","id":"miningEvent.get","method":"miningEvent.get","params":{"miningEventId":7}}
        response_mining = session.exec_post(url_api, headers=header, data=payload)
        balance = response_mining["result"]["miningEvent"]["miningUser"]["cumulativeMicroTokenMined"]/1000000
        print_message("Balance:", format_number(balance) )
        mining_ended = response_mining["result"]["miningEvent"]["miningUser"]["miningSessionEnded"]
        if mining_ended:
            print_message("===Mining Session Ended===")
            print_message("===Claiming==")
            sleep(2)  
            payload = {
                "id": "miningEvent.startSession",
                "jsonrpc": "2.0",
                "method": "miningEvent.startSession",
                "params": {"miningEventId": 7},
            }
            result = session.exec_post(url_api, headers=header, data=payload)
            if result is not None:
                print_message("===Claimed Successful==")
                return
            else:
                print_message("===Claimed Failed==")
                return
        else:
            print_message("===Mining Session Is Not Finished Yet===")
            return
    
    except Exception as e:
        print_message(traceback.format_exc())
    
def main(delay_time):
    try:
        df=pd.read_excel("account.xlsx",dtype={"url":str},sheet_name='gamee')
        df=df[(~df['url'].isna()) & (df['url']!='')]
        df["proxy"] = df["proxy"].fillna(value="")
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