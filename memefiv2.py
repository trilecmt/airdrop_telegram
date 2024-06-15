import sys
import traceback
import aiohttp
import asyncio
import json
import os
from colorama import Fore
import pandas as pd
import pytz
import random
import string
import time
from datetime import datetime, timedelta
from urllib.parse import unquote
from helper.utils import print_message, sleep, format_number
from helper import utils
TODAY_VECTOR="1,4,1,4".replace(" ","")
headers_set = {
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
        'Content-Type': 'application/json',
        'Origin': 'https://tg-app.memefi.club',
        'Referer': 'https://tg-app.memefi.club/',
        'Sec-Ch-Ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
        'Sec-Ch-Ua-mobile': '?1',
        'Sec-Ch-Ua-platform': '"Android"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36',
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
    headers = headers_set.copy()
    proxies=utils.get_proxies(profile["proxy"],type=0)
    profile_id=""
    async with aiohttp.ClientSession() as session:
        async def auth(query):
            tg_web_data = unquote(unquote(query))
            query_id = tg_web_data.split('query_id=', maxsplit=1)[1].split('&user', maxsplit=1)[0]
            user_data = tg_web_data.split('user=', maxsplit=1)[1].split('&auth_date', maxsplit=1)[0]
            auth_date = tg_web_data.split('auth_date=', maxsplit=1)[1].split('&hash', maxsplit=1)[0]
            hash_ = tg_web_data.split('hash=', maxsplit=1)[1].split('&', maxsplit=1)[0]

            user_data_dict = json.loads(unquote(user_data))
            headers = headers_set.copy() 
            data = {
                "operationName": "MutationTelegramUserLogin",
                "variables": {
                    "webAppData": {
                        "auth_date": int(auth_date),
                        "hash": hash_,
                        "query_id": query_id,
                        "checkDataString": f"auth_date={auth_date}\nquery_id={query_id}\nuser={unquote(user_data)}",
                        "user": {
                            "id": user_data_dict["id"],
                            "allows_write_to_pm": user_data_dict["allows_write_to_pm"],
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
            }
            async with session.post(url, headers=headers, json=data,proxy=proxies) as response:
                try:
                    json_response = await response.json()
                    if 'errors' in json_response:
                        return None
                    else:
                        access_token = json_response['data']['telegramUserLogin']['access_token']
                        return access_token
                except aiohttp.ContentTypeError:
                    return None

        # Cek akses token
        async def cek_user():
            json_payload = {
                "operationName": "QueryTelegramUserMe",
                "variables": {},
                "query": QUERY_USER
            }
            async with session.post(url, headers=headers, json=json_payload,proxy=proxies) as response:
                if response.status == 200:
                    response_data = await response.json()
                    if 'errors' in response_data:
                        print(f" Gagal Query ID Salah")
                        return None
                    else:
                        user_data = response_data['data']['telegramUserMe']
                        return user_data  
                else:
                    print(response)
                    print(f" Gagal dengan status {response.status}, mencoba lagi...")
                    return None 
        
        async def submit_taps(total_tap=None,vector=None):           
            if vector is None:
                vector=",".join([str(random.randint(1,4)) for i in range(total_tap)])
            if total_tap is None:
                total_tap=len(vector.split(","))
            json_payload = {
                "operationName": "MutationGameProcessTapsBatch",
                "variables": {
                    "payload": {
                        "nonce": generate_random_nonce(),
                        "tapsCount": total_tap,
                        "vector":vector
                    }
                },
                "query": MUTATION_GAME_PROCESS_TAPS_BATCH
            }
            async with session.post(url, headers=headers, json=json_payload,proxy=proxies) as response:
                if response.status == 200:
                    response_data = await response.json()
                    return response_data['data']  # Mengembalikan hasil response
                else:
                    print_message(f"❌ #{profile_id} Lỗi khi tap thất bại")

        async def upgrade(upgrade_type):
            json_payload = {
                "operationName": "telegramGamePurchaseUpgrade",
                "query": QUERY_UPGRADE,
                "variables":{
                    "upgradeType":upgrade_type
                }
            }
            async with session.post(url, headers=headers, json=json_payload,proxy=proxies) as response:
                if response.status == 200:
                    response_data = await response.json()
                    print_message(f"✅ #{profile_id} Đã nâng {upgrade_type} thành công.")
                    return response_data
            print_message(f"❌ #{profile_id} Đã nâng {upgrade_type} thất bại")
          
        async def cek_stat():
            json_payload = {
                "operationName": "QUERY_GAME_CONFIG",
                "variables": {},
                "query": QUERY_GAME_CONFIG
            }
            
            async with session.post(url, headers=headers, json=json_payload,proxy=proxies) as response:
                if response.status == 200:
                    response_data = await response.json()
                    if 'errors' in response_data:
                        return None
                    else:
                        user_data = response_data['data']['telegramGameGetConfig']
                        return user_data
                    
                elif response.start == 500:
                    return response
                
                else:
                    print(response)
                    print(f" Gagal dengan status {response.status}, mencoba lagi...")
                    return None, None  

        async def change_boss():
            json_payload = {
                "operationName": "telegramGameSetNextBoss",
                "variables": {},
                "query": QUERY_NEXT_BOSS
            }
            async with session.post(url, json=json_payload, headers=headers,proxy=proxies) as response:
                if response.status == 200:
                    print_message(f"✅ #{profile_id} Đã chuyển BOSS thành công.")
                    return await response.json()
            
            print_message(f"❌ #{profile_id} Đã chuyển BOSS thất bại.")
            

        async def start_bot():
            url = "https://api-gw-tg.memefi.club/graphql"
            json_payload = {
                "operationName": "TapbotStart",
                "variables": {},
                "query": QUERY_BOT_START
            }
            async with session.post(url, json=json_payload, headers=headers,proxy=proxies) as response:
                jsons = await response.json()
                if response.status == 200:
                    print_message(f"✅ #{profile_id} Đã start TAPBOT thành công.")
                    return response
            print_message(f"❌ #{profile_id} Đã start TAPBOT thất bại.")

        async def claim_bot():
            json_payload = {
                "operationName": "TapbotClaim",
                "variables": {},
                "query": QUERY_BOT_CLAIM
            }
            async with session.post(url, json=json_payload, headers=headers,proxy=proxies) as response:
                jsons = await response.json()
                if response.status == 200:
                    print_message(f"✅ #{profile_id} Đã claim TAPBOT thành công.")
                    return response
            print_message(f"❌ #{profile_id} Đã claim TAPBOT thất bại.")
        
        async def buy_bot():
            json_payload = {
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
                    }
            async with session.post(url, json=json_payload, headers=headers,proxy=proxies) as response:
                jsons = await response.json()
                if response.status == 200:
                    print_message(f"✅ #{profile_id} Đã mua TAPBOT thành công.")
                    return jsons
            print_message(f"❌ #{profile_id} Đã mua TAPBOT thất bại.")
          
                
        async def apply_boost(boost_type):
            json_payload = {
                "operationName": "telegramGameActivateBooster",
                "variables": {"boosterType" : boost_type},
                "query": QUERY_BOOSTER
            }
            async with session.post(url, json=json_payload, headers=headers,proxy=proxies) as response:
                if response.status == 200:
                    print_message(f"✅ #{profile_id} Đã kích hoạt {boost_type} thành công.")
                    return await response.json()
            print_message(f"❌ #{profile_id} Đã kích hoạt {boost_type} thất bại.")

        async def get_ip():
          async with session.get("https://httpbin.org/ip", headers={"content-type": "application/json"}, proxy=proxies) as response:
              if response.status in [200,201]:
                  response_json= await response.json()
                  return response_json           
              else:
                  return print_message(f"❌ #{profile_id} Get new IP Failed")
              
        ip_data=await get_ip()
        if ip_data is None:
            return print_message(f"❌ #{profile_id} Lấy IP thất bại.")
        profile_id=f"{profile.get('profile')}[{ip_data['origin']}]"          
        access_token = await auth(profile["query"])
        if access_token is None:
            return print_message(f"❌ #{profile_id} Auth thất bại.")
        
        headers['Authorization'] = f'Bearer {access_token}'
        result = await cek_user()
        if result is  None:
            return print_message(f"❌ #{profile_id} Load dữ liệu user thất bại.")
        
        user_data = await cek_stat()
        if user_data is None:
            return print_message(f"❌ #{profile_id} Load dữ liệu game thất bại.")

        before_amount= user_data['coinsAmount']
        await submit_taps(vector=TODAY_VECTOR)
        user_data = await cek_stat()
        if user_data is None:
            return print_message(f"❌ #{profile_id} Load dữ liệu game thất bại.")
        after_amount=user_data['coinsAmount']
        if after_amount-before_amount>=1_000_000:
            print_message(f"✅ #{profile_id} Giải mật mã thành công.Trước {before_amount} Sau {after_amount}")
        else:
            print_message(f"❌ #{profile_id} Giải mật mã thất bại..Trước {before_amount} Sau {after_amount}")

        boost_energy_amount = user_data['freeBoosts']['currentRefillEnergyAmount']
        boost_turbo_amount = user_data['freeBoosts']['currentTurboAmount']
        boss_health = user_data['currentBoss']['currentHealth']
        current_level_boss = user_data['currentBoss']['level']
        print_message(f"✅ #{profile_id} Balance : {user_data['coinsAmount']} | Energy : {user_data['currentEnergy']} - {user_data['maxEnergy']}")
        async def get_tap_bot_config():
            json_payload = {
                "operationName": "TapbotConfig",
                "variables": {},
                "query": "fragment FragmentTapBotConfig on TelegramGameTapbotOutput {\n  damagePerSec\n  endsAt\n  id\n  isPurchased\n  startsAt\n  totalAttempts\n  usedAttempts\n  __typename\n}\n\nquery TapbotConfig {\n  telegramGameTapbotGetConfig {\n    ...FragmentTapBotConfig\n    __typename\n  }\n}"
            }
            async with session.post(url, json=json_payload, headers=headers,proxy=proxies) as response:
                if response.status == 200:
                    response_data = await response.json()
                    user_data = response_data['data']['telegramGameTapbotGetConfig']
                    return user_data
        

        async def process_bot(current_balance):
            tap_bot_config=await get_tap_bot_config()
            is_purchase = tap_bot_config["isPurchased"]
            if not is_purchase:
                if current_balance >= 200000:
                    r=await buy_bot()
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
                    r= await start_bot()
                    if r is not None:
                        return print_message(f"✅ #{profile_id} ACTIVATE BOT AFK thành công.")
                    else:
                        return print_message(f"❌ #{profile_id} Đã có lỗi xảy ra khi ACTIVATE BOT AFK.")
                else:
                    return print_message(f"✅ #{profile_id} Đã hết lượt ACTIVATE BOT AFK.")
            else:
                if end_at <= datetime.now():
                    await claim_bot()
                else:
                    print_message(f"❌ #{profile_id} Chưa đến thời gian CLAIM BOT AFK. {end_at}")

        await process_bot(user_data['coinsAmount'])
        
        if current_level_boss == 11:
            print_message("❌ #{profile_id} đã max level boss", flush=True)
            return
        
        # print_message(f"✅ #{profile_id} Free Turbo : {user_data['freeBoosts']['currentTurboAmount']} Free Energy : {user_data['freeBoosts']['currentRefillEnergyAmount']}")
        # print_message(f"✅ #{profile_id} Boss level : {user_data['currentBoss']['level']} | Boss health : {user_data['currentBoss']['currentHealth']} - {user_data['currentBoss']['maxHealth']}")
        for i in range(user_data.get("energyRechargeLevel"),3):
            r=await upgrade("EnergyRechargeRate")
        for i in range(user_data.get("weaponLevel"),profile['dame_level']):
            r=await upgrade("Damage")
        for i in range(user_data.get("energyLimitLevel"),profile['energy_level']):
            r=await upgrade("EnergyCap")
        
        if boss_health <= 0:
            r=await change_boss()
            if r is not None:
                print_message(f"✅ #{profile_id} Đã chuyển boss thành công.")
            else:
                print_message(f"❌ #{profile_id} Đã chuyển boss thất bại")

        async def farm():
            while True:
                total_tap = random.randint(10, 50)
                respon = await submit_taps(total_tap)
                if respon is not None:
                    energy = respon['telegramGameProcessTapsBatch']['currentEnergy']
                    current_boss = respon['telegramGameProcessTapsBatch']['currentBoss']['currentHealth']
                    print_message(f"✅ #{profile_id} Tap thành công.Năng lượng còn lại:{energy}.Máu boss còn lại:{current_boss}")
                    if current_boss <= 0:
                        await change_boss()

                    if energy < 150:
                        print_message(f"❌ #{profile_id} Năng lượng dưới 150.Tạm nghỉ")
                        break                 
                else:
                    print_message(f"❌ #{profile_id} Tap thất bại")
                    break
                time.sleep(4) 
        await farm()

        #giải mật mã


        for i  in range(boost_energy_amount):
            await apply_boost("Recharge")
            await farm()
            time.sleep(3)

        for i  in range(boost_turbo_amount):
            boost_type = "Turbo"
            await apply_boost(boost_type)
            turbo_time = time.time()
            total_tap = random.randint(100, 200)
            while True:
                respon = await submit_taps(total_tap)   
                if respon is not None:
                    energy = respon['telegramGameProcessTapsBatch']['currentEnergy']
                    current_boss = respon['telegramGameProcessTapsBatch']['currentBoss']['currentHealth']
                    print_message(f"✅ #{profile_id} Tap thành công.Năng lượng còn lại:{energy}.Máu boss còn lại:{current_boss}")
                else:
                    print_message(f"❌ #{profile_id} Tap thất bại")
                    break      
                if current_boss <= 0:
                    await change_boss()
                if ((time.time() - turbo_time) > 10):
                    turbo_time = 0
                    break
                time.sleep(2) 

async def limited_exec(semaphore, profile):
    async with semaphore:
        await exec(profile)

async def main(count_process):
    df=pd.read_excel("account.xlsx",dtype={"profile":str, "query":str,"dame_level":int,"energy_level":int},sheet_name='memefi')
    df=df[(~df['query'].isna()) & (df['query']!='')]
    if "proxy" not in df.columns:
            df["proxy"] = ""
    df['proxy']=df['proxy'].fillna('')
    if "energy_level" not in df.columns:
        df["energy_level"]=10
    if "dame_level" not in df.columns:
        df["dame_level"]=6
    
    profiles=[]
    for idx,row in df.iterrows():
        profile={
            "id":idx+1,
            "profile":row["profile"],
            "query":row["query"],
            "proxy":row["proxy"],
            "energy_level":row["energy_level"],
            "dame_level":row["dame_level"]
        }
        profiles.append(profile)
        # await exec(profile)
    semaphore = asyncio.Semaphore(count_process)  # Limit to 5 concurrent tasks
    tasks = [limited_exec(semaphore, profile) for profile in profiles]
    await asyncio.gather(*tasks)

if __name__=="__main__":
    count_process=int(input("Nhập số CPU:"))
    delay=int(input("Nhập thời gian nghỉ(phút):"))
    while True:
        try:
          asyncio.run(main(count_process))
          for __second in range(delay*60, 0, -1):
              sys.stdout.write(f"\r{Fore.CYAN}Chờ thời gian nhận tiếp theo trong {Fore.CYAN}{Fore.WHITE}{__second // 60} phút {Fore.WHITE}{__second % 60} giây")
              sys.stdout.flush()
              time.sleep(1)
        except Exception as e:
            print_message(traceback.format_exc())


