
import random
import time
import datetime
import configparser
import warnings

import requests
warnings.filterwarnings("ignore", category=DeprecationWarning) 

def print_welcome(game):
    print(f"Welcome to {game}")



def get_daily_code():
    return None
    url = 'https://www.myjsons.com/v/hamster_daily_cards'
    f = requests.get(url)
    data = f.json()
    now=(datetime.datetime.utcnow()+datetime.timedelta(hours=7))
    _data=[item for item in data if item['date']==now.strftime("%Y%m%d")]
    if len(_data)==0:
        return None
    return data[0]


def get_proxies(proxy_url,type):
    
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
        if type==0:
            return proxy_url
        if type==1:
            return {'http':proxy_url,'https':proxy_url}

def read_config(section,key,file_path='config.ini'):
    config = configparser.RawConfigParser()
    config.read(file_path)
    return config.get(section, key)

def format_number(number):
    return "{:,.0f}".format(number)
    
def write_config(section, key, value,file_path='config.ini'):
    config = configparser.RawConfigParser()
    config.read("config.ini")
    config.set(section,key,value)                         
    cfgfile = open(file_path,'w')
    config.write(cfgfile, space_around_delimiters=False)  # use flag in case case you need to avoid white space.
    cfgfile.close()

def print_message(*args, **kwargs):
    current_time=datetime.datetime.utcnow()+datetime.timedelta(hours=7)
    print(current_time, *args, **kwargs)

def get_random(min,max):
    return random.randint(min, max)

def sleep(min,max=None):
    if max is None:
        time.sleep(min)
    else:
        time.sleep(get_random(min,max))

def get_query_id (url:str):
    import urllib.parse
    parsed_url = urllib.parse.urlparse(url)
    query_string = parsed_url.fragment
    query_params = urllib.parse.parse_qs(query_string)
    return query_params['tgWebAppData'][0]