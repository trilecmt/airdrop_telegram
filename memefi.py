import sys
import traceback
import asyncio
import json
import os
from colorama import Fore
import httpx
import pandas as pd
import pytz
import random
import string
import time
from datetime import datetime, timedelta
from urllib.parse import unquote
from helper.utils import print_message, sleep, format_number
from helper import utils
import http.client
import brotli
import base64

headers_set =  {
  'Accept': '*/*',
  'Accept-Encoding': 'gzip, deflate, br, zstd',
  'Accept-Language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
  'Content-Type': 'application/json',
  'Origin': 'https://tg-app.memefi.club',
  'Priority': 'u=1, i',
  'Referer': 'https://tg-app.memefi.club/',
  'Sec-Ch-Ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
  'Sec-Ch-Ua-Mobile': '?0',
  'Sec-Ch-Ua-Platform': '"Windows"',
  'Sec-Fetch-Dest': 'empty',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Site': 'same-site',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36:',
  'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7Il9pZCI6IjY2MjRjZWI0OWRhNzY3MTIxYjc0YzIwMSIsInVzZXJuYW1lIjoidHJpbGVjbXQifSwic2Vzc2lvbklkIjoiNjY4N2Y4N2FkODZlYzFhYmFjZWViMWUyIiwic3ViIjoiNjYyNGNlYjQ5ZGE3NjcxMjFiNzRjMjAxIiwiaWF0IjoxNzIwMTg3MDAyLCJleHAiOjE3Mjc5NjMwMDJ9.C_0k99jzft-auAv1XeoTFJpQ4Yd3oDuX0td2eikhKos'
}

QUERY_GAME_CONFIG = """
query QUERY_GAME_CONFIG {
  telegramGameGetConfig {
    ...FragmentBossFightConfig
    __typename
  }
}

fragment FragmentBossFightConfig on TelegramGameConfigOutput {
  _id
  coinsAmount
  currentEnergy
  maxEnergy
  weaponLevel
  zonesCount
  tapsReward
  energyLimitLevel
  energyRechargeLevel
  tapBotLevel
  currentBoss {
    _id
    level
    currentHealth
    maxHealth
    __typename
  }
  freeBoosts {
    _id
    currentTurboAmount
    maxTurboAmount
    turboLastActivatedAt
    turboAmountLastRechargeDate
    currentRefillEnergyAmount
    maxRefillEnergyAmount
    refillEnergyLastActivatedAt
    refillEnergyAmountLastRechargeDate
    __typename
  }
  bonusLeaderDamageEndAt
  bonusLeaderDamageStartAt
  bonusLeaderDamageMultiplier
  nonce
  spinEnergyNextRechargeAt
  spinEnergyNonRefillable
  spinEnergyRefillable
  spinEnergyTotal
  spinEnergyStaticLimit
  __typename
}
"""

# Tambahkan query-query lainnya dengan format yang sama

MUTATION_GAME_PROCESS_TAPS_BATCH = """
    mutation MutationGameProcessTapsBatch($payload: TelegramGameTapsBatchInput!) {
  telegramGameProcessTapsBatch(payload: $payload) {
    ...FragmentBossFightConfig
    __typename
  }
}

fragment FragmentBossFightConfig on TelegramGameConfigOutput {
  _id
  coinsAmount
  currentEnergy
  maxEnergy
  weaponLevel
  zonesCount
  tapsReward
  energyLimitLevel
  energyRechargeLevel
  tapBotLevel
  currentBoss {
    _id
    level
    currentHealth
    maxHealth
    __typename
  }
  freeBoosts {
    _id
    currentTurboAmount
    maxTurboAmount
    turboLastActivatedAt
    turboAmountLastRechargeDate
    currentRefillEnergyAmount
    maxRefillEnergyAmount
    refillEnergyLastActivatedAt
    refillEnergyAmountLastRechargeDate
    __typename
  }
  bonusLeaderDamageEndAt
  bonusLeaderDamageStartAt
  bonusLeaderDamageMultiplier
  nonce
  spinEnergyNextRechargeAt
  spinEnergyNonRefillable
  spinEnergyRefillable
  spinEnergyTotal
  spinEnergyStaticLimit
  __typename
}
    """
UPGRADE_QUERY = """
        mutation telegramGamePurchaseUpgrade($upgradeType: UpgradeType!) {
          telegramGamePurchaseUpgrade(type: $upgradeType) {
            ...FragmentBossFightConfig
            __typename
          }
        }
        fragment FragmentBossFightConfig on TelegramGameConfigOutput {
          _id
          coinsAmount
          currentEnergy
          maxEnergy
          weaponLevel
          energyLimitLevel
          energyRechargeLevel
          tapBotLevel
          currentBoss {
            _id
            level
            currentHealth
            maxHealth
            __typename
          }
          freeBoosts {
            _id
            currentTurboAmount
            maxTurboAmount
            turboLastActivatedAt
            turboAmountLastRechargeDate
            currentRefillEnergyAmount
            maxRefillEnergyAmount
            refillEnergyLastActivatedAt
            refillEnergyAmountLastRechargeDate
            __typename
          }
          bonusLeaderDamageEndAt
          bonusLeaderDamageStartAt
          bonusLeaderDamageMultiplier
          nonce
          __typename
        }
        """
QUERY_SPIN="""
mutation spinSlotMachine {
  slotMachineSpin {
    id
    combination
    rewardAmount
    rewardType
    __typename
  }
}
"""
QUERY_BOOSTER = """
            mutation telegramGameActivateBooster($boosterType: BoosterType!) {
              telegramGameActivateBooster(boosterType: $boosterType) {
                ...FragmentBossFightConfig
                __typename
              }
            }
            fragment FragmentBossFightConfig on TelegramGameConfigOutput {
              _id
              coinsAmount
              currentEnergy
              maxEnergy
              weaponLevel
              energyLimitLevel
              energyRechargeLevel
              tapBotLevel
              currentBoss {
                _id
                level
                currentHealth
                maxHealth
                __typename
              }
              freeBoosts {
                _id
                currentTurboAmount
                maxTurboAmount
                turboLastActivatedAt
                turboAmountLastRechargeDate
                currentRefillEnergyAmount
                maxRefillEnergyAmount
                refillEnergyLastActivatedAt
                refillEnergyAmountLastRechargeDate
                __typename
              }
              bonusLeaderDamageEndAt
              bonusLeaderDamageStartAt
              bonusLeaderDamageMultiplier
              nonce
              __typename
            }
            """

QUERY_NEXT_BOSS = """
        mutation telegramGameSetNextBoss {
          telegramGameSetNextBoss {
            ...FragmentBossFightConfig
            __typename
          }
        }
        fragment FragmentBossFightConfig on TelegramGameConfigOutput {
          _id
          coinsAmount
          currentEnergy
          maxEnergy
          weaponLevel
          energyLimitLevel
          energyRechargeLevel
          tapBotLevel
          currentBoss {
            _id
            level
            currentHealth
            maxHealth
            __typename
          }
          freeBoosts {
            _id
            currentTurboAmount
            maxTurboAmount
            turboLastActivatedAt
            turboAmountLastRechargeDate
            currentRefillEnergyAmount
            maxRefillEnergyAmount
            refillEnergyLastActivatedAt
            refillEnergyAmountLastRechargeDate
            __typename
          }
          bonusLeaderDamageEndAt
          bonusLeaderDamageStartAt
          bonusLeaderDamageMultiplier
          nonce
          __typename
        }
        """

QUERY_GET_TASK = """
        fragment FragmentCampaignTask on CampaignTaskOutput {
          id
          name
          description
          status
          type
          position
          buttonText
          coinsRewardAmount
          link
          userTaskId
          isRequired
          iconUrl
          __typename
        }

        query GetTasksList($campaignId: String!) {
          campaignTasks(campaignConfigId: $campaignId) {
            ...FragmentCampaignTask
            __typename
          }
        }
        """

QUERY_TASK_ID = """
                fragment FragmentCampaignTask on CampaignTaskOutput {
                  id
                  name
                  description
                  status
                  type
                  position
                  buttonText
                  coinsRewardAmount
                  link
                  userTaskId
                  isRequired
                  iconUrl
                  __typename
                }

                query GetTaskById($taskId: String!) {
                  campaignTaskGetConfig(taskId: $taskId) {
                    ...FragmentCampaignTask
                    __typename
                  }
                }
                """

QUERY_TASK_VERIF = """
                fragment FragmentCampaignTask on CampaignTaskOutput {
                  id
                  name
                  description
                  status
                  type
                  position
                  buttonText
                  coinsRewardAmount
                  link
                  userTaskId
                  isRequired
                  iconUrl
                  __typename
                }

                mutation CampaignTaskToVerification($userTaskId: String!) {
                  campaignTaskMoveToVerification(userTaskId: $userTaskId) {
                    ...FragmentCampaignTask
                    __typename
                  }
                }
                """

QUERY_TASK_COMPLETED = """
                fragment FragmentCampaignTask on CampaignTaskOutput {
                  id
                  name
                  description
                  status
                  type
                  position
                  buttonText
                  coinsRewardAmount
                  link
                  userTaskId
                  isRequired
                  iconUrl
                  __typename
                }

                mutation CampaignTaskCompleted($userTaskId: String!) {
                  campaignTaskMarkAsCompleted(userTaskId: $userTaskId) {
                    ...FragmentCampaignTask
                    __typename
                  }
                }
                """
QUERY_USER = """
        query QueryTelegramUserMe {
          telegramUserMe {
            firstName
            lastName
            telegramId
            username
            referralCode
            isDailyRewardClaimed
            referral {
              username
              lastName
              firstName
              bossLevel
              coinsAmount
              __typename
            }
            isReferralInitialJoinBonusAvailable
            league
            leagueIsOverTop10k
            leaguePosition
            _id
            __typename
          }
        }
        """

QUERY_LOGIN = """mutation MutationTelegramUserLogin($webAppData: TelegramWebAppDataInput!) {
            telegramUserLogin(webAppData: $webAppData) {
                access_token
                __typename
            }
        }"""

QUERY_BOT_CLAIM = """
fragment FragmentTapBotConfig on TelegramGameTapbotOutput {
  damagePerSec
      endsAt
          id
            isPurchased
            startsAt
            totalAttempts
            usedAttempts
            __typename
          }
          
          mutation TapbotClaim {
            telegramGameTapbotClaimCoins {
              ...FragmentTapBotConfig
              __typename
            }
          }"""

QUERY_BOT_START = """fragment FragmentTapBotConfig on TelegramGameTapbotOutput {
  damagePerSec
  endsAt
  id
  isPurchased
  startsAt
  totalAttempts
  usedAttempts
  __typename
}

mutation TapbotStart {
  telegramGameTapbotStart {
    ...FragmentTapBotConfig
    __typename
  }
}"""

QUERY_UPGRADE="""mutation telegramGamePurchaseUpgrade($upgradeType: UpgradeType!) {
  telegramGamePurchaseUpgrade(type: $upgradeType) {
    ...FragmentBossFightConfig
    __typename
  }
}

fragment FragmentBossFightConfig on TelegramGameConfigOutput {
  _id
  coinsAmount
  currentEnergy
  maxEnergy
  weaponLevel
  zonesCount
  tapsReward
  energyLimitLevel
  energyRechargeLevel
  tapBotLevel
  currentBoss {
    _id
    level
    currentHealth
    maxHealth
    __typename
  }
  freeBoosts {
    _id
    currentTurboAmount
    maxTurboAmount
    turboLastActivatedAt
    turboAmountLastRechargeDate
    currentRefillEnergyAmount
    maxRefillEnergyAmount
    refillEnergyLastActivatedAt
    refillEnergyAmountLastRechargeDate
    __typename
  }
  bonusLeaderDamageEndAt
  bonusLeaderDamageStartAt
  bonusLeaderDamageMultiplier
  nonce
  __typename
}"""

url = "https://api-gw-tg.memefi.club/graphql"


def generate_random_nonce(length=52):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


async def exec(profile): 
    try:
      headers = headers_set.copy()
      proxies=utils.get_proxies(profile["proxy"],type=0)
      profile_id=""
      ip_data=None
      conn=None
      if proxies is not None or 1==1:   
        from urllib.parse import urlparse
        # Chuỗi proxy
        
        # Phân tích chuỗi proxy
        parsed_url = urlparse(proxies)
        # Lấy thông tin username, password, host và port
        username =parsed_url.username
        password = parsed_url.password
        proxy_host =parsed_url.hostname
        proxy_port = parsed_url.port
        # Tạo một chuỗi xác thực base64 từ username và password
        auth_base64=None
        if parsed_url.username is not None:  
          auth = f'{username}:{password}'
          auth_encoded = auth.encode('utf-8')
          auth_base64 = base64.b64encode(auth_encoded).decode('utf-8')
        if proxy_host is not None:
          conn = http.client.HTTPSConnection(proxy_host, proxy_port)
        else:
            conn = http.client.HTTPSConnection()
        def get_ip(auth_base64):
          conn_ip = http.client.HTTPSConnection(proxy_host, proxy_port)
          if auth_base64 is not None:
             conn_ip.set_tunnel('api.myip.com', headers={'Proxy-Authorization': f'Basic {auth_base64}'})
          else:
             conn_ip.set_tunnel('api.myip.com')
          # Gửi yêu cầu HTTPS tới server đích qua proxy
          conn_ip.request('GET', '/')
          response = conn_ip.getresponse()
          if response.status == 200:
              data = response.read()
              conn_ip.close()
              return json.loads(data)['ip']
          else:
            conn_ip.close()
          


      def call_data(conn,payload):
          conn.request("POST", "/graphql", json.dumps(payload), headers) 
          res = conn.getresponse()
          if res.status==200:
              data = res.read()
              str_data=(brotli.decompress(data))
              return json.loads(str_data)

          
        

      def auth(cnn,query):
          tg_web_data = unquote(unquote(query))
          query_id = tg_web_data.split('query_id=', maxsplit=1)[1].split('&user', maxsplit=1)[0]
          user_data = tg_web_data.split('user=', maxsplit=1)[1].split('&auth_date', maxsplit=1)[0]
          auth_date = tg_web_data.split('auth_date=', maxsplit=1)[1].split('&hash', maxsplit=1)[0]
          hash_ = tg_web_data.split('hash=', maxsplit=1)[1].split('&', maxsplit=1)[0]

          user_data_dict = json.loads(unquote(user_data))
          headers = headers_set.copy() 
          data = [{
              "operationName": "MutationTelegramUserLogin",
              "variables": {
                  "webAppData": {
                      "auth_date": int(auth_date),
                      "hash": hash_,
                      "query_id": query_id,
                      "checkDataString": f"auth_date={auth_date}\nquery_id={query_id}\nuser={unquote(user_data)}",
                      "user": {
                          "id": user_data_dict["id"],
                          "allows_write_to_pm": user_data_dict.get("allows_write_to_pm",True),
                          "first_name": user_data_dict["first_name"],
                          "last_name": user_data_dict["last_name"],
                          "username": user_data_dict.get("username", "Username gak diset"),
                          "language_code": user_data_dict["language_code"],
                          "version": "7.2",
                          "platform": "ios"
                      }
                  }
              },
              "query": QUERY_LOGIN
          }]
          try:
            response= call_data(cnn,data)
            if response is not None:
              access_token = response[0]['data']['telegramUserLogin']['access_token']
              return access_token
          except Exception as e:
              return None
          
      
          
      # Cek akses token
      def cek_user(cnn):
          payload =[
            {
              "operationName": "QueryTelegramUserMe",
              "variables": {},
              "query": "query QueryTelegramUserMe {\n  telegramUserMe {\n    firstName\n    lastName\n    telegramId\n    username\n    referralCode\n    isDailyRewardClaimed\n    referral {\n      username\n      lastName\n      firstName\n      bossLevel\n      coinsAmount\n      __typename\n    }\n    isReferralInitialJoinBonusAvailable\n    league\n    leagueIsOverTop10k\n    leaguePosition\n    _id\n    opens {\n      isAvailable\n      openType\n      __typename\n    }\n    features\n    role\n    earlyAdopterBonusAmount\n    earlyAdopterBonusPercentage\n    __typename\n  }\n}"
            }
          ]
          response=call_data(cnn,payload)
          if response is not None:
              user_data = response[0]['data']['telegramUserMe']
              return user_data 
          
      
      def submit_taps(conn,total_tap=None,vector=None,json_payload=None):           
          if vector is None:
              vector=",".join([str(random.randint(1,4)) for i in range(total_tap)])
          if total_tap is None:
              total_tap=len(vector.split(","))
          if json_payload is None:
            json_payload = [{
                "operationName": "MutationGameProcessTapsBatch",
                "variables": {
                    "payload": {
                        "nonce": generate_random_nonce(),
                        "tapsCount": total_tap,
                        "vector":vector
                    }
                },
                "query": MUTATION_GAME_PROCESS_TAPS_BATCH
            }]
          response=call_data(conn,json_payload)
          if response is not None:
              return response[0]['data']  # Mengembalikan hasil response
          else:
              print_message(f"❌ #{profile_id} Lỗi khi tap thất bại")

      def upgrade(conn,upgrade_type):
          json_payload = {
              "operationName": "telegramGamePurchaseUpgrade",
              "query": QUERY_UPGRADE,
              "variables":{
                  "upgradeType":upgrade_type
              }
          }
          response_data= call_data(conn,json_payload)
          if response_data is not None:
              print_message(f"✅ #{profile_id} Đã nâng {upgrade_type} thành công.")
              return response_data
          print_message(f"❌ #{profile_id} Đã nâng {upgrade_type} thất bại")
        
      def cek_stat(cnn):
          json_payload =[{
              "operationName": "QUERY_GAME_CONFIG",
              "variables": {},
              "query": QUERY_GAME_CONFIG
          }]
          
          response=call_data(cnn,json_payload)
          if response is not None:
              user_data = response[0]['data']['telegramGameGetConfig']
              return user_data

      def change_boss(conn):
          try:
            json_payload =[{
                "operationName": "telegramGameSetNextBoss",
                "variables": {},
                "query": QUERY_NEXT_BOSS
            }]
            response= call_data(conn,json_payload)
            if response is not None:
                r= response[0]
                if "errors" in r:
                    print_message(f"❌ #{profile_id} Đã chuyển BOSS thất bại.Lỗi {r.get('errors')[0]['message']}")
                    return False
                else:
                  print_message(f"✅ #{profile_id} Đã chuyển BOSS thành công.")
                  return True
            print_message(f"❌ #{profile_id} Đã chuyển BOSS thất bại.")
            return False
          except:
            print_message(f"❌ #{profile_id} Đã chuyển BOSS thất bại.")
            return False
          

      def start_bot(conn):
          url = "https://api-gw-tg.memefi.club/graphql"
          json_payload = {
              "operationName": "TapbotStart",
              "variables": {},
              "query": QUERY_BOT_START
          }
          response= call_data(conn,json_payload)
          if response is not None:
              print_message(f"✅ #{profile_id} Đã start TAPBOT thành công.")
              return response
          print_message(f"❌ #{profile_id} Đã start TAPBOT thất bại.")

      def claim_bot(conn):
          json_payload = [{
              "operationName": "TapbotClaim",
              "variables": {},
              "query": QUERY_BOT_CLAIM
          }]
          response= call_data(conn,json_payload)
          
          if response is not None:
              print_message(f"✅ #{profile_id} Đã claim TAPBOT thành công.")
              return response
          print_message(f"❌ #{profile_id} Đã claim TAPBOT thất bại.")
      
      def buy_bot(conn):
          json_payload = [{
                  "operationName": "telegramGamePurchaseUpgrade",
                  "variables": {"upgradeType": "TapBot"},
                  "query": """mutation telegramGamePurchaseUpgrade($upgradeType: UpgradeType!) {
telegramGamePurchaseUpgrade(type: $upgradeType) {
  ...FragmentBossFightConfig
  __typename
}
}

fragment FragmentBossFightConfig on TelegramGameConfigOutput {
_id
coinsAmount
currentEnergy
maxEnergy
weaponLevel
zonesCount
tapsReward
energyLimitLevel
energyRechargeLevel
tapBotLevel
currentBoss {
  _id
  level
  currentHealth
  maxHealth
  __typename
}
freeBoosts {
  _id
  currentTurboAmount
  maxTurboAmount
  turboLastActivatedAt
  turboAmountLastRechargeDate
  currentRefillEnergyAmount
  maxRefillEnergyAmount
  refillEnergyLastActivatedAt
  refillEnergyAmountLastRechargeDate
  __typename
}
bonusLeaderDamageEndAt
bonusLeaderDamageStartAt
bonusLeaderDamageMultiplier
nonce
__typename
}"""
                  }]
          response= call_data(conn,json_payload)
          if response is not None:
              print_message(f"✅ #{profile_id} Đã mua TAPBOT thành công.")
              jsons =  response[0]
              return jsons
          print_message(f"❌ #{profile_id} Đã mua TAPBOT thất bại.")
        
              
      def spin_energy(cnn):
          json_payload = [{
              "operationName": "spinSlotMachine",
              "variables": {},
            "query": QUERY_SPIN
          }]
          response= call_data(cnn,json_payload)
          if response is not None:
              print_message(f"✅ #{profile_id} Đã kích hoạt SPIN thành công.Reward :{response[0]['data']['slotMachineSpin']['rewardAmount']} {response[0]['data']['slotMachineSpin']['rewardType']}")
              return  response[0]
          print_message(f"❌ #{profile_id} Đã kích hoạt SPIN thất bại.")

      def apply_boost(conn,boost_type):
          json_payload = [{
              "operationName": "telegramGameActivateBooster",
              "variables": {"boosterType":boost_type},
              "query": QUERY_BOOSTER
          }]
          response= call_data(conn,json_payload)
          if response is not None:
              print_message(f"✅ #{profile_id} Đã kích hoạt {boost_type} thành công.")
              return  response[0]
          print_message(f"❌ #{profile_id} Đã kích hoạt {boost_type} thất bại.")
      
      conn = http.client.HTTPSConnection(proxy_host, proxy_port)
      if auth_base64 is not None:
          conn.set_tunnel("api-gw-tg.memefi.club",443 ,  headers={'Proxy-Authorization': f'Basic {auth_base64}'})
      else:
          conn.set_tunnel("api-gw-tg.memefi.club",443 )
      ip_data= get_ip(auth_base64)
      if ip_data is None:
          return print_message(f"❌ #{profile_id} Lấy IP thất bại.")
      profile_id=f"{profile.get('profile')}[{ip_data}]"          
      access_token =  auth(conn,profile["query"])
      if access_token is None:
          return print_message(f"❌ #{profile_id} Auth thất bại.")
      
      headers['Authorization'] = f'Bearer {access_token}'
      result =  cek_user(conn)
      if result is  None:
          return print_message(f"❌ #{profile_id} Load dữ liệu user thất bại.")
      
      user_data =cek_stat(conn)
      if user_data is None:
          return print_message(f"❌ #{profile_id} Load dữ liệu game thất bại.")

      spin_energy_total=user_data['spinEnergyTotal']

      if spin_energy_total>0:
          for _spin_energy in range(spin_energy_total):
              spin_energy(conn)
              time.sleep(3)
      before_amount= user_data['coinsAmount']
      if profile["vector"] is not None:
        submit_taps(conn,vector=profile["vector"])
        user_data = cek_stat(conn)
        if user_data is None:
            return print_message(f"❌ #{profile_id} Load dữ liệu game thất bại.")
        after_amount=user_data['coinsAmount']
        if after_amount-before_amount>=1_000_000:
            print_message(f"✅ #{profile_id} Giải mật mã {profile['vector']} thành công.Trước {before_amount} Sau {after_amount}")
        else:
            print_message(f"❌ #{profile_id} Giải mật mã {profile['vector']} thất bại..Trước {before_amount} Sau {after_amount}")

      boost_energy_amount = user_data['freeBoosts']['currentRefillEnergyAmount']
      boost_turbo_amount = user_data['freeBoosts']['currentTurboAmount']
      boss_health = user_data['currentBoss']['currentHealth']
      current_level_boss = user_data['currentBoss']['level']
      print_message(f"✅ #{profile_id} Balance : {user_data['coinsAmount']} | Energy : {user_data['currentEnergy']} - {user_data['maxEnergy']}")
      
      def get_tap_bot_config(cnn):
          json_payload = [{
              "operationName": "TapbotConfig",
              "variables": {},
              "query": "fragment FragmentTapBotConfig on TelegramGameTapbotOutput {\n  damagePerSec\n  endsAt\n  id\n  isPurchased\n  startsAt\n  totalAttempts\n  usedAttempts\n  __typename\n}\n\nquery TapbotConfig {\n  telegramGameTapbotGetConfig {\n    ...FragmentTapBotConfig\n    __typename\n  }\n}"
          }]
          response_data= call_data(cnn,json_payload)
          if response_data is not None:
              user_data = response_data[0]['data']['telegramGameTapbotGetConfig']
              return user_data
      

      def process_bot(cnn,current_balance):
          tap_bot_config= get_tap_bot_config(cnn)
          is_purchase = tap_bot_config["isPurchased"]
          if not is_purchase:
              if current_balance >= 200000:
                  r= buy_bot(conn)
                  if r is not None:
                      return print_message(f"✅ #{profile_id} Mua BOT AFK thành công.")
                  else:
                      return print_message(f"❌ #{profile_id} Đã có lỗi xảy ra khi mua BOT AFK.")
              else:
                  return print_message(f"❌ #{profile_id} Không đủ balance mua BOT AFK.")

          def get_date_format(date_str : str):
              date_format = '%Y-%m-%dT%H:%M:%S.%fZ'
              if date_str is None:
                  return ""
              else:
                  return datetime.strptime(date_str, date_format) + timedelta (hours=7)
              
          end_at = get_date_format(tap_bot_config["endsAt"])
          if end_at == "":
              if tap_bot_config["totalAttempts"] - tap_bot_config["usedAttempts"]> 0:
                  r=  start_bot(conn)
                  if r is not None:
                      return print_message(f"✅ #{profile_id} ACTIVATE BOT AFK thành công.")
                  else:
                      return print_message(f"❌ #{profile_id} Đã có lỗi xảy ra khi ACTIVATE BOT AFK.")
              else:
                  return print_message(f"✅ #{profile_id} Đã hết lượt ACTIVATE BOT AFK.")
          else:
              if end_at <= datetime.now():
                    claim_bot(conn)
              else:
                  print_message(f"❌ #{profile_id} Chưa đến thời gian CLAIM BOT AFK. {end_at}")

      process_bot(conn,user_data['coinsAmount'])
      
      # if current_level_boss == 11:
      #     print_message(f"❌ #{profile_id} đã max level boss", flush=True)
      #     return
      
      # print_message(f"✅ #{profile_id} Free Turbo : {user_data['freeBoosts']['currentTurboAmount']} Free Energy : {user_data['freeBoosts']['currentRefillEnergyAmount']}")
      # print_message(f"✅ #{profile_id} Boss level : {user_data['currentBoss']['level']} | Boss health : {user_data['currentBoss']['currentHealth']} - {user_data['currentBoss']['maxHealth']}")
      for i in range(user_data.get("energyRechargeLevel"),3):
          r= upgrade(conn,"EnergyRechargeRate")
      for i in range(user_data.get("weaponLevel"),profile['dame_level']):
          r= upgrade(conn,"Damage")
      for i in range(user_data.get("energyLimitLevel"),profile['energy_level']):
          r= upgrade(conn,"EnergyCap")
      
      if boss_health <= 0:
          change_boss(conn)
        

      def farm(conn):
          for i in range(10):
              total_tap = random.randint(30, 50)
              respon =  submit_taps(conn,total_tap)
              if respon is not None:
                  energy = respon['telegramGameProcessTapsBatch']['currentEnergy']
                  current_boss = respon['telegramGameProcessTapsBatch']['currentBoss']['currentHealth']
                  print_message(f"✅ #{profile_id} {i+1}/10 Tap {total_tap} thành công.Năng lượng còn lại:{energy}.Máu boss còn lại:{current_boss}")
                  if current_boss <= 0:
                        r= change_boss(conn)
                        if r==False:
                            return False

                  if energy < 150:
                      print_message(f"❌ #{profile_id} Năng lượng dưới 150.Tạm nghỉ")
                      break                 
              else:
                  print_message(f"❌ #{profile_id} Tap thất bại")
                  break
              time.sleep(2) 

      r= farm(conn)
      if r==False:
          return print_message(f"❌ #{profile_id} Nâng boss gặp lỗi. Move next")
      for i  in range(boost_energy_amount):
          apply_boost(conn,"Recharge")
          farm(conn)
          time.sleep(3)

      for i  in range(boost_turbo_amount):
          boost_type = "Turbo"
          apply_boost(conn,boost_type)
          turbo_time = time.time()
          total_hit = random.randint(400,600)
          nonce=generate_random_nonce()
          
          while True:
              tap_payload = [{
                "operationName": "MutationGameProcessTapsBatch",
                "variables": {
                    "payload": {
                        "nonce": nonce,
                        "tapsCount": total_hit
                    }
                },
                "query": MUTATION_GAME_PROCESS_TAPS_BATCH
            }]
              respon =  submit_taps(conn,total_hit,json_payload=tap_payload)   
              if respon is not None:
                  energy = respon['telegramGameProcessTapsBatch']['currentEnergy']
                  current_boss = respon['telegramGameProcessTapsBatch']['currentBoss']['currentHealth']
                  print_message(f"✅ #{profile_id} Tap thành công.Năng lượng còn lại:{energy}.Máu boss còn lại:{current_boss}")
              else:
                  print_message(f"❌ #{profile_id} Tap thất bại")
                  break      
              if current_boss <= 0:
                  change_boss(conn)
              if ((time.time() - turbo_time) > 10):
                  turbo_time = 0
                  break
              time.sleep(2) 
    except Exception as e:
          print_message(f"❌ Lỗi khi xử lí profile {profile['profile']}")
          print_message(traceback.format_exc())
    finally:
        print_message(f"✅ #{profile_id} Kết thúc")

async def limited_exec(semaphore, profile):
    async with semaphore:
        await exec(profile)
        
            

async def main(count_process,delay,sheet_name):
    print_message("Next round...")
    code=utils.get_daily_code()
    vector=None
    if code is not None:
        vector=code.get("comboMeme",None)
    df=pd.read_excel("account.xlsx",dtype={"profile":str, "query":str,"dame_level":int,"energy_level":int,"token":str},sheet_name=sheet_name)
    if "proxy" not in df.columns:
            df["proxy"] = ""
    df['proxy']=df['proxy'].fillna('')
    if "energy_level" not in df.columns:
        df["energy_level"]=10
    if "dame_level" not in df.columns:
        df["dame_level"]=6
    df=df[(~df['query'].isna()) & (df['query']!='')]

    profiles=[]
    for idx,row in df.iterrows():
        profile={
            "id":idx+1,
            "profile":row["profile"],
            "query":row["query"],
            "proxy":row["proxy"],
            "energy_level":row["energy_level"],
            "dame_level":row["dame_level"],
            "vector":vector
        }
        profiles.append(profile)
        # await exec(profile)
    semaphore = asyncio.Semaphore(count_process)  # Limit to 5 concurrent tasks
    tasks = [limited_exec(semaphore, profile) for profile in profiles]
    await asyncio.gather(*tasks)
    for __second in range(delay*60, 0, -1):
          sys.stdout.write(f"\r{Fore.CYAN}Chờ thời gian nhận tiếp theo trong {Fore.CYAN}{Fore.WHITE}{__second // 60} phút {Fore.WHITE}{__second % 60} giây")
          sys.stdout.flush()
          time.sleep(1)

if __name__=="__main__":
    count_process=int(input("Nhập số CPU:"))
    sheet_name=input("Nhập tên sheet:")
    delay=int(input("Nhập thời gian nghỉ(phút):"))
    while True:
        try:
          asyncio.run(main(count_process,delay,sheet_name))        
        except Exception as e:
            print_message(traceback.format_exc())


