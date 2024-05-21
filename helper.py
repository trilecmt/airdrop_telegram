
import random
import requests
import login_drivers.gen_login_driver

def get_driver_login(driver_name:str):
    if driver_name=="GEN_LOGIN":
        driver_login=login_drivers.gen_login_driver.GenLoginDriver(api_url='http://localhost:55550/backend/profiles')
    # if driver_name=="GO_LOGIN":
    #     driver_login=login_drivers.go_login_driver.GoLoginDriver()
    return driver_login

def request_api(api_url):
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise HTTPError for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return None

def get_random(min,max):
    return random.randint(min, max)