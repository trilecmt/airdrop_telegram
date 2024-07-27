import sys
import requests
import time
import json
import os
from colorama import Fore, Style
import random
import warnings

from helper import utils
warnings.filterwarnings("ignore", category=DeprecationWarning)
import urllib.parse
import json
import datetime

URL_JOIN='https://api.onetime.dog/join'
URL_REWARD='https://api.onetime.dog/join'
HEADER = {
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
            'If-Modified-Since': 'Fri, 26 Jul 2024 17:56:51 GMT',
            'Origin': 'https://onetime.dog',
            'Priority': 'u=1, i',
            'Referer': 'https://onetime.dog/',
            'Sec-Ch-Ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            }


def parse_user(query):
    try:
        # Parse the query string
        query_dict = urllib.parse.parse_qs(query)

        # Decode the user information
        user_info = query_dict.get('user')[0]
        user_info_decoded = urllib.parse.unquote(user_info)
        user_info_dict = json.loads(user_info_decoded)

        # Get the user_id
        # Get the user_id and username
        user_id = str(user_info_dict.get('id',None))
        username = user_info_dict.get('username',None)
        return user_id,username
    except:
        return None,None
    

def build_proxy(proxy_url:str,type=1):
    if proxy_url is not None and proxy_url!='':  
        if not proxy_url.startswith("http"):
            if len(proxy_url.split(":"))==2:       
                host=proxy_url.split(":")[0]
                port=proxy_url.split(":")[1]
                proxy_url=f'http://{host}:{port}'
            else:
                username=proxy_url.split(":")[2]
                password=proxy_url.split(":")[3]
                host=proxy_url.split(":")[0]
                port=proxy_url.split(":")[1]
                proxy_url=f'http://{username}:{password}@{host}:{port}'
        if type==0:
            return proxy_url
        if type==1:
            return {'http':proxy_url,'https':proxy_url}
def get_ip(proxy_url):

    response=requests.get("https://httpbin.org/ip", headers={"content-type": "application/json"}, proxies=build_proxy(proxy_url))
    if response.status_code in [200,201]:
        response_json=  response.json()
        return response_json           
    else:
        return None


def main():
    import pandas as pd
    df=pd.read_excel("account.xlsx",sheet_name="dog",dtype={"proxy":str,"query_id":str})
    df['proxy']=df['proxy'].fillna("")

    records_data=df[["proxy","query_id"]].to_dict("records")
    for user in records_data:
        try:
            user_id,user_name=parse_user(user.get("query_id"))
            # url = f"https://api.onetime.dog/rewards?user_id={user_id}"      
            response_ip=get_ip(user.get("proxy"))
            if response_ip is None:
                print(f'[{user_id} Error proxy {user.get("proxy")}')
                continue
            response = requests.request("POST", "https://api.onetime.dog/join", headers=HEADER, data=user.get("query_id"),proxies=build_proxy(user.get("proxy")))
            # response = requests.request("GET", url, headers=HEADER, data=payload,proxies=build_proxy(user.get("proxy")))          
            print(f'[{user_id}][{response_ip.get("origin")}] Checkin success {response.text}')
            
        except Exception as e:
            print(e)
        
    

if __name__ == "__main__":
    while True:
        try:
            main()
        except:
            pass
        for __second in range(60*60, 0, -1):
            sys.stdout.write(f"\r{Fore.CYAN}Chờ thời gian nhận tiếp theo trong {Fore.CYAN}{Fore.WHITE}{__second // 60} phút {Fore.WHITE}{__second % 60} giây")
            sys.stdout.flush()
            time.sleep(1)
