import asyncio
import sys
import time
import pandas as pd
import traceback
from helper.utils import print_message, sleep, format_number
from datetime import datetime, timedelta
from helper.helper_session import MySession
from colorama import init, Fore, Style
init(autoreset=True)

headers={
  'Accept': '*/*',
  'Accept-Encoding': 'gzip, deflate, br, zstd',
  'Accept-Language': 'en-US,en;q=0.9',
  'Connection': 'keep-alive',
  'Content-Length': '317',
  'Content-Type': 'text/plain;charset=UTF-8',
  'Host': 'tg-bot-tap.laborx.io',
  'Origin': 'https://tg-tap-miniapp.laborx.io',
  'Referer': 'https://tg-tap-miniapp.laborx.io/',
  'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'Sec-Fetch-Dest': 'empty',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Site': 'same-site',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
}
                
URL='https://tg-bot-tap.laborx.io/api/v1' 

async def exec(profile):
    profile_id=profile['id']
    try:
        with MySession() as session:
            def start_farm():
                response=session.exec_post(f'{URL}/farming/start', headers=headers, data={})
                print_message(f"✅ #{profile_id} Start farm Sucess") 
                return response
            
            def claim():
                response=session.exec_post(f'{URL}/farming/finish', headers=headers, data={})
                if response is None:
                    return print_message(f"❌ #{profile_id} Claim farm failed.Move next...")  
                response=session.exec_post(f'{URL}/farming/start', headers=headers, data={})
                if response is None:
                    return print_message(f"❌ #{profile_id} Start farm failed.Move next...")  
                print_message(f"✅ #{profile_id} Claim farm and restart success.Move next...")          
            
            response=session.exec_post(f'{URL}/auth/validate-init', headers=headers, data=profile['query'],is_convert_dump_json=False)
            if response is None:
                return print_message(f"❌ #{profile_id} Auth failed.Move next...")    
            headers['Authorization']="Bearer "+response['token']
            if "Content-Length" in headers:
                del headers['Content-Length']
            response=session.exec_get(f'{URL}/farming/info', headers=headers,log=True)
            if response is None:
                return print_message(f"❌ #{profile_id} Load farm info failed.Move next...")  
            if  response.get('activeFarmingStartedAt',None) is None:
                return start_farm()      
            claim_time=datetime.strptime(response['activeFarmingStartedAt'], "%Y-%m-%dT%H:%M:%S.%fZ")+ timedelta(seconds=response['farmingDurationInSec'])+timedelta(hours=7)
            if claim_time>(datetime.utcnow()+timedelta(hours=7)):
                return print_message(f"❌ #{profile_id} Next claim at {claim_time+timedelta(hours=7)}.Move next...")      
            else:
                claim()
            
    except Exception as e:        
        print_message(f'#{profile_id} ERROR............')
        print(traceback.format_exc())
        pass


async def limited_exec(semaphore, profile):
    async with semaphore:
        await exec(profile)

async def main(count_process):
    
    df=pd.read_excel("account.xlsx",dtype={"query":str},sheet_name='timefarm')
    df=df[(~df['query'].isna()) & (df['query']!='')]
    if "proxy" not in df.columns:
            df["proxy"] = ""
    df['proxy']=df['proxy'].fillna('')
    
    profiles=[]
    for idx,row in df.iterrows():
        profile={
            "id":idx+1,
            "query":row["query"],
            "proxy":row["proxy"]
        }
        profiles.append(profile)
        # await exec(profile)
    semaphore = asyncio.Semaphore(count_process)  # Limit to 5 concurrent tasks
    tasks = [limited_exec(semaphore, profile) for profile in profiles]
    await asyncio.gather(*tasks)

if __name__=="__main__":
    delay_time=int(input("Enter delay time(second):"))
    count_process=int(input("Enter count process:"))
    while True:
        asyncio.run(main(count_process))
        print(f"\n{Fore.GREEN+Style.BRIGHT}========={Fore.WHITE+Style.BRIGHT}Tất cả tài khoản đã được xử lý thành công{Fore.GREEN+Style.BRIGHT}=========", end="", flush=True)
        print(f"\r\n\n{Fore.GREEN+Style.BRIGHT}Làm mới token...", end="", flush=True)
        
        for __second in range(delay_time, 0, -1):
            sys.stdout.write(f"\r{Fore.CYAN}Chờ thời gian nhận tiếp theo trong {Fore.CYAN}{Fore.WHITE}{__second // 60} phút {Fore.WHITE}{__second % 60} giây")
            sys.stdout.flush()
            time.sleep(1)
        sys.stdout.write("\rĐã đến thời gian nhận tiếp theo!\n")

# def main(delay_time):
#     try:
#         df=pd.read_excel("account.xlsx",dtype={"url":str},sheet_name='memefi')
#         df=df[(~df['token'].isna()) & (df['token']!='')]
#         df.reset_index(inplace=True)
#         if "list_upgrade" not in df.columns:
#             df["list_upgrade"] = ""
#         if "proxy" not in df.columns:
#             df["proxy"] = ""
#         df['proxy']=df['proxy'].fillna('')
#         for idx,row in df.iterrows():
#             exec("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7Il9pZCI6IjY2NWRkN2JkNDgxMjkwOTJkZjlkNjgwMSIsInVzZXJuYW1lIjoiam9uMTEwOCJ9LCJzZXNzaW9uSWQiOiI2NjYzMDlkYjM3YWEzZjk4OWVkNjlhOWMiLCJzdWIiOiI2NjVkZDdiZDQ4MTI5MDkyZGY5ZDY4MDEiLCJpYXQiOjE3MTc3NjY2MTksImV4cCI6MTcxODM3MTQxOX0.X4Z2_y3Knwq3-TmZXylSlq9hyOviRJgpvDzsB6UfeDc"
#                 #  ,row['token'],
#                  ,proxy_url=""
#                  #row['proxy'])
#             )
#             time.sleep(10)
            
#         time.sleep(delay_time)
#     except Exception as e:
#         print(e)

# if __name__=='__main__':
#     while True:
#         try:
#             main(delay_time=120)                      
#         except Exception as e:
#             print(e)