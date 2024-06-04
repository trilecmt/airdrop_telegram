from multiprocessing import Pool
from selenium import webdriver
import time
import pandas as pd
import driver_helper
import helper
import constraint
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from helper.utils import print_message,sleep,get_random
import datetime

DEFAULT_WINDOW_SIZE=(400,800)
KEY="authToken"

def exec():
    
    df=pd.read_excel("account.xlsx",dtype={"profile":str},sheet_name='token')
    df=df[(~df['profile'].isna()) & (df['profile']!='')]
    df.reset_index(inplace=True)
    df['token']=''
    for idx,row in df.iterrows():
        profile=row['profile']
        driver_login,driver=helper.helper_driver.start_profile(driver_name='GPM_LOGIN',profile_name=profile,window_size=DEFAULT_WINDOW_SIZE)  
        driver.get(row['url'])
        #Đợi trang tải hoàn toàn (nếu cần thiết)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        # Lấy dữ liệu từ LocalStorage
        local_storage_data = driver.execute_script(f"return window.localStorage.getItem('{KEY}');")
        print(f"LocalStorage Data: {local_storage_data}")
        df.loc[df.index==idx,"token"]=local_storage_data
        driver_login.close_profile(profile)
    
    df.to_excel(f"token_{datetime.datetime.utcnow().strftime("%Y%M%d%H%m%S")}.xlsx")

if __name__=='__main__':
    exec()