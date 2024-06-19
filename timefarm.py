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

# from helper.helper_schedule import ScheduleDB

# schedule=ScheduleDB()

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

def format_money(value):
    return f"{int(value):,d}"

def exec(profile):
    profile_id=profile['id']
    try:
        with MySession() as session:
            def start_farm():
                response=session.exec_post(f'{URL}/farming/start', headers=headers, data={})
                print_message(f"✅ #{profile_id} Start farm success") 
                return response
            
            def claim():
                response=session.exec_post(f'{URL}/farming/finish', headers=headers, data={})
                if response is None:
                    return print_message(f"❌ #{profile_id} Claim farm failed.Move next...")  
                response=session.exec_post(f'{URL}/farming/start', headers=headers, data={})
                if response is None:
                    return print_message(f"❌ #{profile_id} Start farm failed.Move next...")  
                claim_time=datetime.strptime(response['activeFarmingStartedAt'], "%Y-%m-%dT%H:%M:%S.%fZ")+ timedelta(seconds=response['farmingDurationInSec'])
                # schedule.update_profile(
                #     game=GAME,
                #     profile_name=profile["name"],
                #     latest_run_date=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                #     next_run_date=claim_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                # )
                print_message(f"✅ #{profile_id} Claim farm and restart success.Move next...")          
            
            response_auth=session.exec_post(f'{URL}/auth/validate-init', headers=headers, data=profile['query'],is_convert_dump_json=False)
            if response_auth is None:
                return print_message(f"❌ #{profile_id} Auth failed.Move next...")  
            print_message(f"✅ #{profile_id} Login success.Main balance:{format_money(response_auth['balanceInfo']['balance'])}. Ref balance:{format_money(response_auth['balanceInfo']['referral'].get('availableBalance',0))}")   
            headers['Authorization']="Bearer "+response_auth['token']
            if "Content-Length" in headers:
                del headers['Content-Length']
            level_descriptions=response_auth.get("levelDescriptions",None)
            current_factor=response_auth['farmingInfo']['farmingReward']/response_auth['farmingInfo']['farmingDurationInSec']

            if level_descriptions is not None:
                for level_description in level_descriptions:
                    if level_description.get('price',-1)>0 and int(level_description.get("farmMultiplicator"))>current_factor:
                        if level_description.get('price',-1)>response_auth['balanceInfo']['balance']:
                            print_message(f"❌ #{profile_id} Not enough balance {format_money(response_auth['balanceInfo']['balance'])} to upgrade level clock (need {format_money(level_description.get('price',-1))})...")  
                            break
                        else:
                            response=session.exec_post(f'{URL}/me/level/upgrade', headers=headers, data={})
                            if response is not None:
                                print_message(f"✅ #{profile_id} Upgrade clock success x{response['level']}.New balance:{response['balance']}") 
                                response_auth['balanceInfo']['balance']=response['balance']
                            else:
                                print_message(f"❌ #{profile_id} Something went wrong when call upgrade clock...")  
                                break

            if response_auth['balanceInfo']['referral'].get('availableBalance',0)>0:
                response=session.exec_post(f'{URL}/balance/referral/claim', headers=headers,data={})
                if response is not None:
                    print_message(f"✅ #{profile_id} Claim ref {response_auth['balanceInfo']['referral']['availableBalance']} success") 
                else:
                    print_message(f"❌ #{profile_id} Something went wrong when call claim ref...")  

            response=session.exec_get(f'{URL}/farming/info', headers=headers)
            if response is None:
                return print_message(f"❌ #{profile_id} Load farm info failed.Move next...")  
            if  response.get('activeFarmingStartedAt',None) is None:
                return start_farm()      
            claim_time=datetime.strptime(response['activeFarmingStartedAt'], "%Y-%m-%dT%H:%M:%S.%fZ")+ timedelta(seconds=response['farmingDurationInSec'])
            if claim_time>datetime.utcnow():
                # schedule.update_profile(
                #     game=GAME,
                #     profile_name=profile["name"],
                #     latest_run_date=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                #     next_run_date=(claim_time).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                # )
                return print_message(f"❌ #{profile_id} Next claim at {claim_time+timedelta(hours=7)}.Move next...")   
               
            else:
                claim()
            
    except Exception as e:        
        print_message(f'#{profile_id} ERROR............')
        print_message(traceback.format_exc())



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
        exec(profile)


if __name__=="__main__":
    try:
        print_welcome(game=GAME)
        delay=int(input("Nhập số phút nghỉ:"))
        while True:
            main()       
            for __second in range(delay*60, 0, -1):
                sys.stdout.write(f"\r{Fore.CYAN}Chờ thời gian nhận tiếp theo trong {Fore.CYAN}{Fore.WHITE}{__second // 60} phút {Fore.WHITE}{__second % 60} giây")
                sys.stdout.flush()
                time.sleep(1)
            sys.stdout.write("")
    except KeyboardInterrupt:
        exit()
    except:
        print_message(traceback.format_exc())