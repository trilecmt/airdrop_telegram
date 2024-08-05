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

 
class OKX:
    def headers(self,ref_id):
        if ref_id is None:
            ref_id=''
        return {
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9",
            "App-Type": "web",
            "Content-Type": "application/json",
            "Origin": "https://www.okx.com",
            "Referer": f"https://www.okx.com/mini-app/racer?tgWebAppStartParam=linkCode_{ref_id}",
            "Sec-Ch-Ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Microsoft Edge";v="126"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
            "X-Cdn": "https://www.okx.com",
            "X-Locale": "en_US",
            "X-Utc": "7",
            "X-Zkdex-Env": "0"
        }

    def get_ip(self,proxy_url):
        response=requests.get("https://httpbin.org/ip", headers={"content-type": "application/json"}, proxies=build_proxy(proxy_url))
        if response.status_code in [200,201]:
            response_json=  response.json()
            return response_json           
        else:
            return None
    
    
    def post_to_okx_api(self,ref_id,query_id,ext_user_id, ext_user_name,proxy):
        url = f"https://www.okx.com/priapi/v1/affiliate/game/racer/info?t={int(time.time())}"
        headers = self.headers(ref_id).copy()
        headers['X-Telegram-Init-Data']= query_id
        payload = {
            "extUserId": ext_user_id,
            "extUserName": ext_user_name,
            "gameId": 1,
            "linkCode": ref_id
        }
        response = requests.post(url, headers=headers, json=payload,proxies=build_proxy(proxy))
        return response.json()

    def assess_prediction(self,ref_id,query_id, ext_user_id, predict,proxy):
        url = f"https://www.okx.com/priapi/v1/affiliate/game/racer/assess?t={int(time.time())}"
        headers = self.headers(ref_id).copy()
        headers['X-Telegram-Init-Data']= query_id
        payload = {
            "extUserId": ext_user_id,
            "predict": predict,
            "gameId": 1
        }
        response = requests.post(url, headers=headers, json=payload,proxies=build_proxy(proxy))
        return response.json()


    def check_daily_rewards(self,ref_id,query_id, ext_user_id,proxy):
        url = f"https://www.okx.com/priapi/v1/affiliate/game/racer/tasks?extUserId={ext_user_id}&t={int(time.time())}"
        headers = self.headers(ref_id).copy()
        headers['X-Telegram-Init-Data']= query_id
        try:
            response = requests.get(url, headers=headers,proxies=build_proxy(proxy))
            tasks = response.json().get("data", [])
            daily_checkin_task = next((task for task in tasks if task["id"] == 4), None)
            if daily_checkin_task:
                if daily_checkin_task["state"] == 0:
                    self.log("Bắt đầu checkin...")
                    self.perform_checkin(ref_id,query_id,ext_user_id, daily_checkin_task["id"],proxy)
                else:
                    self.log("Hôm nay bạn đã điểm danh rồi!")
        except Exception as error:
            self.log(f"Lỗi kiểm tra phần thưởng hàng ngày: {str(error)}")

    def perform_checkin(self,ref_id,query_id,ext_user_id, task_id,proxy):
        headers = self.headers(ref_id).copy()
        headers['X-Telegram-Init-Data']= query_id
        url = f"https://www.okx.com/priapi/v1/affiliate/game/racer/task?t={int(time.time())}"
        payload = {
            "extUserId": ext_user_id,
            "id": task_id
        }
        try:
            response = requests.post(url, headers=headers, json=payload,proxies=build_proxy(proxy))
            response.json()
            self.log("Điểm danh hàng ngày thành công!")
        except Exception as error:
            self.log(f"Lỗi rồi: {str(error)}")

    def get_boost(self,ref_id,query_id, ext_user_id,proxy):
        url = f"https://www.okx.com/priapi/v1/affiliate/game/racer/boosts?t={int(time.time())}"
        headers = self.headers(ref_id).copy()
        headers['X-Telegram-Init-Data']= query_id
        try:
            response = requests.get(url, headers=headers,proxies=build_proxy(proxy))
            return [item for item in response.json().get("data", []) if item['type']==3][0]
        except Exception as error:
            print(error)
            # self.log(f"Lỗi kiểm tra phần thưởng hàng ngày: {str(error)}")

    def use_boost(self,ref_id,query_id,proxy):
        url = f"https://www.okx.com/priapi/v1/affiliate/game/racer/boost?t={int(time.time())}"
        headers = self.headers(ref_id).copy()
        headers['X-Telegram-Init-Data']= query_id
        try:
            response = requests.post(url, headers=headers,data=json.dumps({"id":1}), proxies=build_proxy(proxy)) 
            if (response.json().get("code") == 0):
                self.log("Reload Fuel Tank thành công")
                return True
            else:
                self.log(f'Lỗi Reload Fuel Tank: {response.json().get("error_message")}') 
                return False
        except Exception as error:
            self.log(error)
            return False

    # async useBoost(queryId) {
    #     const url = `https://www.okx.com/priapi/v1/affiliate/game/racer/boost?t=${Date.now()}`;
    #     const headers = { ...this.headers(), 'X-Telegram-Init-Data': queryId };
    #     const payload = { id: 1 };

    #     try {
    #         const response = await axios.post(url, payload, { headers });
    #         if (response.data.code === 0) {
    #             this.log('Reload Fuel Tank thành công!'.yellow);
    #             await this.Countdown(5);
    #         } else {
    #             this.log(`Lỗi Reload Fuel Tank: ${response.data.msg}`.red);
    #         }
    #     } catch (error) {
    #         this.log(`Lỗi rồi: ${error.message}`.red);
    #     }
    # }

    def log(self, msg):
        print(f"[*] {msg}")

    def countdown(self, seconds):
        for i in range(seconds, -1, -1):
            print(f"\r[*] Chờ {i} giây để tiếp tục...", end="")
            time.sleep(1)
        print("")

    def main(self):
        import pandas as pd
        df=pd.read_excel("account.xlsx",sheet_name="okxrace",dtype={"proxy":str,"check_ip":int,"query_id":str,"ref_id":str})
        df['proxy']=df['proxy'].fillna("")
        df['ref_id']=df['ref_id'].fillna("")
        
        records_data=df[["proxy","check_ip","query_id","ref_id"]].to_dict("records")
        import datetime
        for item in records_data:
            item['next_round']=datetime.datetime.utcnow()

        while True:
            picked_users=[item for item in records_data if item.get("next_round")<datetime.datetime.utcnow()]
            if len(picked_users)==0:
                time.sleep(1)
            else:
                picked_user= sorted(picked_users, key=lambda d: d['next_round'])[0]
                ext_user_id, ext_user_name = parse_user(picked_user.get("query_id"))
                if ext_user_name is None:
                    ext_user_name=""
                if  ext_user_id is None:
                    print(picked_user.get("query_id"))
                    raise Exception(f'UserId không thể parse')      
                try:
                    print(f"{Fore.BLUE}========== Tài khoản {ext_user_name} =========={Style.RESET_ALL}")
                    if picked_user.get("check_ip")==1:
                        response=self.get_ip(picked_user.get('proxy'))
                        if response is None:
                            picked_user['next_round']=datetime.datetime.utcnow()+datetime.timedelta(seconds=60)
                            self.log(f"Lấy IP thất bại ")
                            self.log(f"Lần chạy tiếp theo {picked_user['next_round']}...")
                            continue
                        self.log(f"Lấy IP thành công {response}")
                    self.check_daily_rewards(picked_user.get("ref_id"),picked_user.get("query_id"),ext_user_id,picked_user.get('proxy'))
                    # for _ in range(50):

                    
                    response = self.post_to_okx_api(picked_user.get("ref_id"),picked_user.get("query_id"), ext_user_id, ext_user_name,picked_user.get('proxy'))
                    balance_points = response.get("data", {}).get("balancePoints", 0)
                    
                    self.log(f"{Fore.GREEN}Balance Points:{Style.RESET_ALL} {balance_points}")
                    if response.get("data", {}).get("numChances",0)==0:
                        picked_user['next_round']=datetime.datetime.utcnow()+datetime.timedelta(seconds=60)
                        self.log(f"Lần chạy tiếp theo {picked_user['next_round']}...")
                    else:
                        for chance in range(response.get("data", {}).get("numChances",0)):
                            self.log(f'{chance+1}/{response.get("data", {}).get("numChances",0)}')
                            assess_response = self.assess_prediction(picked_user.get("ref_id"),picked_user.get("query_id"),ext_user_id, 1,picked_user.get('proxy'))
                            assess_data = assess_response.get("data", {})
                            result = Fore.GREEN + "Win" if assess_data.get("won") else Fore.RED + "Thua"
                            calculated_value = assess_data.get("basePoint", 0) * assess_data.get("multiplier", 0)
                            self.log(f"Kết quả: {result} x {assess_data.get('multiplier', 0)}! Balance: {assess_data.get('balancePoints', 0)}, Nhận được: {calculated_value}, Giá cũ: {assess_data.get('prevPrice', 0)}, Giá hiện tại: {assess_data.get('currentPrice', 0)}")
                            self.log(f'Chờ 6 giây')
                            time.sleep(6)
                        picked_user['next_round']=datetime.datetime.utcnow()+datetime.timedelta(seconds=600)
                        self.log(f"Lần chạy tiếp theo {picked_user['next_round']}..")
                    response_boost=self.get_boost(picked_user.get("ref_id"),picked_user.get("query_id"),ext_user_id,picked_user.get('proxy'))
                    if response_boost is not None and response_boost['curStage']<response_boost['totalStage']:                  
                        response_boost=self.use_boost(picked_user.get("ref_id"),picked_user.get("query_id"),picked_user.get('proxy'))
                        if response_boost:
                            picked_user['next_round']=datetime.datetime.utcnow()+datetime.timedelta(seconds=60)
                            self.log(f"Lần chạy tiếp theo {picked_user['next_round']}...")
                    # if response.get("data", {}).get("numChances",0)<=2:
                    self.log(f'Chờ {assess_data["secondToRefresh"] + 5} giây')    

                    
                except Exception as error:
                    import traceback
                    self.log(traceback.format_exc())
                    self.log(f"{Fore.RED}Lỗi rồi:{Style.RESET_ALL} {str(error)}")
                    picked_user['next_round']=datetime.datetime.utcnow()+datetime.timedelta(seconds=60)
                    self.log(f"Lần chạy tiếp theo {picked_user['next_round']}....")

if __name__ == "__main__":
    okx = OKX()
    okx.main()
