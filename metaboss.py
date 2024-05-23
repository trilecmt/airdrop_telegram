from selenium import webdriver
import time
import pandas as pd
import driver_helper
import helper
import constraint
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

DEFAULT_WINDOW_SIZE=(400,800)
PROFILE_NAME=constraint.METABOSS_PROFILE

def exec():
    driver_login=helper.get_driver_login("GEN_LOGIN")
    df=pd.read_excel("account.xlsx",dtype={"url":str},sheet_name='metaboss')
    df=df[(~df['url'].isna()) & (df['url']!='')]
    df.reset_index(inplace=True)
    for idx,row in df.iterrows():
        url=row['url']
        if url is None:
            continue
        # if idx!=2:
        #     continue
        print(f'{idx+1}/{len(df)}.Processing profile {PROFILE_NAME}')
        response=driver_login.start_profile(PROFILE_NAME)

        if response.get("success")==False:
            try:
                print(f"close profile {PROFILE_NAME}")
                driver_login.close_profile(PROFILE_NAME)
            except Exception as e:
                pass
            continue
        
        driver=driver_login.get_driver(debugger_address=response['data']['debugger_address'],window_size=DEFAULT_WINDOW_SIZE)
       
        
        try:
            driver.get(url)
            # action = webdriver.common.action_chains.ActionChains(driver)
            # action.w3c_actions.pointer_action._duration = helper.get_random(1,3)
            # action.move_to_element_with_offset(driver.find_element(by=By.ID.ID,value="unity-canvas"), 0,0)
            # action.move_by_offset(248, 254).click().perform()
            from selenium.webdriver import ActionChains
            from selenium.webdriver.common.actions.action_builder import ActionBuilder

            while True:
                action = ActionBuilder(driver)
                action.pointer_action.move_to_location(64, 60)
                action.pointer_action.click()
                action.perform()

            # from a_selenium_click_on_coords import click_on_coordinates
            # click_on_coordinates(driver,x=248,y=254, script_timeout=10)
            # click_on_coordinates(driver,x=254,y=252484, script_timeout=10)
            # element=driver_helper.wait_element_appear(driver,value="//p[text()='Start Playing']",timeout=5)
            # if element is not None:
            #     element.click()
            #     time.sleep(2)
            # click_hero(time_click=3)
            # while booster():
            #     click_hero(time_click=3)

        except Exception as e:
            print(e)
        finally:
            try:       
                driver_helper.delete_cache(driver)
            except Exception as e:
                pass
            time.sleep(3)
            print('Done...')
            
if __name__=='__main__':
    while True:
        try:
            exec()
        except Exception as e:
            print(e)