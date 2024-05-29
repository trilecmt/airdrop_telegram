
import random
import time
import datetime
 
def print_message(message):
    print(f'{datetime.datetime.utcnow()+datetime.timedelta(hours=7)} {message}')

def get_random(min,max):
    return random.randint(min, max)

def sleep(min,max=None):
    if max is None:
        time.sleep(min)
    else:
        time.sleep(get_random(min,max))