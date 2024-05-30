import time
import requests

def exec(token):
    try:
        
        url = "https://api.hamsterkombat.io/clicker/tap"
        headers = {
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
            "Connection": "keep-alive",
            "Content-Length": "53",
            "Host": "api.hamsterkombat.io",
            "Origin": "https://hamsterkombat.io",
            "Referer": "https://hamsterkombat.io/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
        }

        payload = {
            "count": 1000,
            "availableTaps": 4000,
            "timestamp": int(time.time())
        }

        response = requests.post(url, headers=headers, json=payload)

        print(response.status_code)
        # print(response.text)  # If the response is JSON

    except Exception as e:
        pass

if __name__=="__main__":
    while True:
        exec(token='1716787825438Vh7Nj3NbZyMtpTdHzzEpEVZhc0lEIIjAOtBlUW8kCk6da2VGyLmPuXU8AUjtHYUK7119671832')
        time.sleep(60)