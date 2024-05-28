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

DEFAULT_WINDOW_SIZE=(400,800)

PROFILE_NAME="hamster"#input("Enter profile name:")
IS_REVERSE=0#input("Enter huong 1(nguoc)/0:")

def exec():
    driver_login,driver=helper.start_profile(driver_name='GPM_LOGIN',profile_name=PROFILE_NAME,window_size=DEFAULT_WINDOW_SIZE) 
    df=pd.read_excel("account.xlsx",dtype={"url":str},sheet_name='hamster')
    df=df[(~df['url'].isna()) & (df['url']!='')]
    if IS_REVERSE=='1':
        df=df.reindex(index=df.index[::-1])
    df.reset_index(inplace=True)
    for idx,row in df.iterrows():
        url=row['url']
        if url is None:
            continue

        try:
            driver.get(url)
            element=driver_helper.wait_element_appear(driver,value="//button[@class='bottom-sheet-button button button-primary button-large']",timeout=5)
            if element is not None:
                element.click()
                time.sleep(2)
            element=driver_helper.wait_element_appear(driver,value="//div[@class='user-tap-button-inner']",timeout=5)
   
            if element is not None:
                for i in range(10000):
                    element.click()
                    time.sleep(2)
           

        except Exception as e:
            helper.print_message(e)
        finally:
            # try:       
            #     driver_helper.delete_cache(driver,is_close=False)
            # except Exception as e:
            #     pass
            time.sleep(3)
            helper.print_message('Done...')

    helper.print_message(f"Close profile {PROFILE_NAME}")
    driver_login.close_profile(PROFILE_NAME)

if __name__=='__main__':
    while True:
        try:
            exec()
            time.sleep(30)
        except Exception as e:
            helper.print_message(e)