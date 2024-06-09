
import random
import time
import datetime
import configparser
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 
 
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