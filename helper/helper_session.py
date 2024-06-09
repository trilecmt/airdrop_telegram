
import random
import re
import requests
import time
import datetime
import json
from helper.utils import print_message

class MySession(requests.Session):
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        
    def set_proxy(self,proxy_url:str='',is_test_after_change=True):
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
            self.proxies= {'http':proxy_url,'https':proxy_url}
            print_message(f'Changed proxy success==> success')      
        else:
            print("Countinue without proxy.")
            
        if is_test_after_change:
                print_message("Checking new IP...")
                response = self.exec_get(url="https://api.myip.com/",headers={"content-type": "application/json"})
                if response is None:
                    print_message(f"Get new IP Failed")
                else:
                    print_message(f"New IP:{response['ip']}")
                    return response['ip']
                
    def exec_post(self,url, headers, data,retry_count=1):
        for i in range(retry_count):
            try:
                response_info  = self.post(url, headers=headers, data=json.dumps(data))
                if response_info.status_code  in [200,201]:   
                    return json.loads(response_info.text)
                print_message(f"StatusCode: {response_info.status_code}")
                print_message(f"Response text: {response_info.text}")
                print_message("Error: Couldn't fetch user data")
                time.sleep(2)
            except Exception as e:
                print_message(e)
        
    def exec_get(self,url, headers,retry_count=1):
        for i in range(retry_count):
            try:
                response_info  = self.get(url, headers=headers)
                if response_info.status_code in [200,201]:    
                    return json.loads(response_info.text)
                print_message(f"StatusCode: {response_info.status_code}")
                print_message(f"Response text: {response_info.text}")
                print_message("Error: Couldn't fetch user data")
                time.sleep(2)
            except Exception as e:
                print_message(e)


    def exec_exec(self,url, headers,method:str='GET',data=None):
        if method not in ['POST','GET']:
            raise Exception('Method is only support POST/GET')
        if method=='POST':
            return self.exec_post(url,headers,data)
        if method=='GET':
            return self.exec_get(url,headers)