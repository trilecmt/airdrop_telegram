import requests
import random
import time

ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjQzMTkwNSwidGltZXN0YW1wIjoxNzE2NjE5NzI4ODIyLCJ0eXBlIjoxLCJpYXQiOjE3MTY2MTk3MjgsImV4cCI6MTcxNzIyNDUyOH0.xBS8dH51VdbYII6xK6sQGhiia9JuYea6yYEZ09NASxU"  # Put your access token here
listColect = []
listDuck = []

URL='https://api.quackquack.games'

def getTotalEgg():
    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9,vi;q=0.8",
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "if-none-match": 'W/"1a9-I7Onn3jBU9AHo0MlzSY8mMECNvQ"',
        "priority": "u=1, i",
        "sec-ch-ua": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "Referer": "https://dd42189ft3pck.cloudfront.net/",
        "Referrer-Policy": "strict-origin-when-cross-origin",
    }

    response = requests.get(f"{URL}/balance/get", headers=headers)
    data = response.json()

    for item in data["data"]["data"]:
        if item["symbol"] == "EGG":
            helper.print_message(f"Đã thu thập {int(item['balance'])} trứng")


def getListReload():
    global listColect, listDuck

    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9,vi;q=0.8",
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "if-none-match": 'W/"1218-LZvWPzXbQkzjfWJ5mauEo0z3f9c"',
        "priority": "u=1, i",
        "sec-ch-ua": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "Referer": "https://dd42189ft3pck.cloudfront.net/",
        "Referrer-Policy": "strict-origin-when-cross-origin",
    }

    response = requests.get(f"{URL}/nest/list-reload", headers=headers)
    data = response.json()

    if not listDuck:
        listDuck = [item["id"] for item in data["data"]["duck"]]

    for item in data["data"]["nest"]:
        if item["type_egg"]:
            listColect.append(item["id"])

    helper.print_message("Số trứng có thể thu thập:", len(listColect))
    helper.print_message(listColect)


def collect():
    global listColect

    if not listColect:
        time.sleep(3)
        collect()
        return

    egg = listColect[0]

    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9,vi;q=0.8",
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "content-type": "application/x-www-form-urlencoded",
        "priority": "u=1, i",
        "sec-ch-ua": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "Referer": "https://dd42189ft3pck.cloudfront.net/",
        "Referrer-Policy": "strict-origin-when-cross-origin",
    }

    data = {"nest_id": egg}

    response = requests.post(f"{URL}/nest/collect", headers=headers, data=data)
    response_json = response.json()

    helper.print_message(f"Thu thập trứng thành công: {egg}")
    layEgg(egg)


def layEgg(egg):
    global listColect

    duck = random.choice(listDuck)

    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9,vi;q=0.8",
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "content-type": "application/x-www-form-urlencoded",
        "priority": "u=1, i",
        "sec-ch-ua": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "Referer": "https://dd42189ft3pck.cloudfront.net/",
        "Referrer-Policy": "strict-origin-when-cross-origin",
    }

    data = {"nest_id": egg, "duck_id": duck}

    response = requests.post(f"{URL}/nest/lay-egg", headers=headers, data=data)
    response_json = response.json()

    getTotalEgg()
    listColect.pop(0)
    time.sleep(3)
    collect()


getTotalEgg()
getListReload()

while True:
    try:
        time.sleep(10)
        getListReload()
        collect()
    except Exception as e:
        helper.print_message(e)
