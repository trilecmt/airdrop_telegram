
import random
import requests
import login_drivers.gen_login_driver
import login_drivers.gpm_login_driver
import time
import datetime
import configparser
import json
 
 
def read_config(section,key,file_path='config.ini'):
    config = configparser.RawConfigParser()
    config.read(file_path)
    return config.get(section, key)

def write_config(section, key, value,file_path='config.ini'):
    config = configparser.RawConfigParser()
    config.read("config.ini")
    config.set(section,key,value)                         
    cfgfile = open(file_path,'w')
    config.write(cfgfile, space_around_delimiters=False)  # use flag in case case you need to avoid white space.
    cfgfile.close()

def print_message(message):
    print(f'{datetime.datetime.utcnow()+datetime.timedelta(hours=7)} {message}')

def delete_profile(driver_name,profile_name):
    driver_login=get_driver_login(driver_name)
    driver_login.delete_profile(profile_name)

def start_profile(driver_name,profile_name,window_size):
    driver_login=get_driver_login(driver_name)
    is_success_open_profile=False
    chorme_config=None
    while not is_success_open_profile:
        print_message(f'Start profile {profile_name}')
        response=driver_login.start_profile(profile_name)
        if response.get("success")==False:
            try:
                print_message(f"Close profile {profile_name}")
                driver_login.close_profile(profile_name)
                sleep(5,5)
            except Exception as e:
                print_message(e)
                sleep(5,5)
        else:
            is_success_open_profile=True
            chorme_config=response.get("data")
          
    driver=driver_login.get_driver(
        chrome_driver_path=chorme_config.driver_path,
        debugger_address=chorme_config.debugger_address,
        window_size=window_size
    )
    return driver_login,driver

def get_driver_login(driver_name:str):
    if driver_name=="GEN_LOGIN":
        driver_login=login_drivers.gen_login_driver.GenLoginDriver(api_url='http://localhost:55550/backend/profiles')
    if driver_name=="GPM_LOGIN":   
        driver_login=login_drivers.gpm_login_driver.GPMLoginApiV3(api_url='http://127.0.0.1:19995/api/v3/profiles')

    # if driver_name=="GO_LOGIN":
    #     driver_login=login_drivers.go_login_driver.GoLoginDriver()
    return driver_login

def request_api(api_url):
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise HTTPError for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print_message(f"Error: {e}" )
        return None

def get_random(min,max):
    return random.randint(min, max)

def sleep(min,max=None):
    if max is None:
        time.sleep(min)
    else:
        time.sleep(get_random(min,max))

def post_api(url_get_info, headers, payload):
    response_info  = requests.post(url_get_info, headers=headers, json= payload)
    if response_info.status_code != 200:
        print(f"StatusCode: {response_info.status_code}")
        print(f"Response text: {response_info.text}")
        raise ValueError("Error: Couldn't fetch user data")
    return json.loads(response_info.text)

def session_post_api(session:requests.Session,url, headers, payload):
    response_info  = session.post(url, headers=headers, json= payload)
    if response_info.status_code != 200:
        print(f"StatusCode: {response_info.status_code}")
        print(f"Response text: {response_info.text}")
        raise ValueError("Error: Couldn't fetch user data")
    return json.loads(response_info.text)