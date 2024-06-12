import asyncio
import sys
import time
import pandas as pd
import traceback
from helper.utils import print_message, print_welcome, sleep, format_number
from datetime import datetime, timedelta
from helper.helper_session import MySession
from colorama import init, Fore, Style
init(autoreset=True)
GAME='TIMEFARM'

from helper.helper_schedule import ScheduleDB

schedule=ScheduleDB()

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

def exec(profile):
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
                claim_time=datetime.strptime(response['activeFarmingStartedAt'], "%Y-%m-%dT%H:%M:%S.%fZ")+ timedelta(seconds=response['farmingDurationInSec'])
                schedule.update_profile(
                    game=GAME,
                    profile_name=profile["name"],
                    latest_run_date=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                    next_run_date=claim_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                )
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
            claim_time=datetime.strptime(response['activeFarmingStartedAt'], "%Y-%m-%dT%H:%M:%S.%fZ")+ timedelta(seconds=response['farmingDurationInSec'])
            if claim_time>datetime.utcnow():
                schedule.update_profile(
                    game=GAME,
                    profile_name=profile["name"],
                    latest_run_date=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                    next_run_date=(claim_time).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                )
                return print_message(f"❌ #{profile_id} Next claim at {claim_time+timedelta(hours=7)}.Move next...")   
               
            else:
                claim()
            
    except Exception as e:        
        print_message(f'#{profile_id} ERROR............')
        print(traceback.format_exc())
        pass



def main():
    df=pd.read_excel("account.xlsx",dtype={"query":str,"profile":str},sheet_name='timefarm')
    df=df[(~df['query'].isna()) & (df['query']!='')]
    if "proxy" not in df.columns:
            df["proxy"] = ""
    df['proxy']=df['proxy'].fillna('')
    
    for idx,row in df.iterrows():
        profile={
            "id":idx+1,
            "name":row["profile"],
            "query":row["query"],
            "proxy":row["proxy"]
        }
        db_profile=schedule.get_profile(game=GAME, profile_name=profile['name'])
        if db_profile is None or  db_profile["next_run_date"] < (datetime.utcnow()):
            exec(profile)


if __name__=="__main__":
    print_welcome(game=GAME)
    while True:
        main()       
        for __second in range(60, 0, -1):
            sys.stdout.write(f"\r{Fore.CYAN}Chờ thời gian nhận tiếp theo trong {Fore.CYAN}{Fore.WHITE}{__second // 60} phút {Fore.WHITE}{__second % 60} giây")
            sys.stdout.flush()
            time.sleep(1)