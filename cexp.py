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

DEFAULT_WINDOW_SIZE=constraint.DEFAULT_WINDOW_SIZE
PROFILE_NAME='CEXP'

def exec():
    driver_login,driver=helper.start_profile(driver_name='GPM_LOGIN',profile_name=PROFILE_NAME,window_size=DEFAULT_WINDOW_SIZE) 
    df=pd.read_excel("account.xlsx",dtype={"url":str},sheet_name='cexp')
    df=df[(~df['url'].isna()) & (df['url']!='')]
    df.reset_index(inplace=True)
    for idx,row in df.iterrows():
        url=row['url']
        if url is None:
            continue
        helper.print_message(f'{idx+1}/{len(df)}.Processing')

        def click_hero(time_click):
            helper.print_message(f'[{row['profile']}] Attacking hero')
         
            for i in range(time_click):
                helper.print_message(f'{i}/{time_click}')
                
                element=driver_helper.find_element(driver,value="//*[@class='Text_text__g5dgG Text_primary__9SniH Text_textL__4XTbr Text_semiBold__iPCTR Text_center__cmN+H']")
                if  element is not None and element.text=='0 taps left':
                    helper.print_message('0 taps left')
                    helper.sleep(1,1)
                    continue
                helper.sleep(2,2)        
                element=driver_helper.find_element(driver,value="//*[@class='Tap_tapCoin__IQw2b']")
                action = webdriver.common.action_chains.ActionChains(driver)
                action.w3c_actions.pointer_action._duration = helper.get_random(1,3)
                for j in range(100):
                    try:
                        action.move_to_element_with_offset(element,helper.get_random(-15,0),helper.get_random(-15,0))# helper.get_random(-20,-40), helper.get_random(-20,-40))
                        action.double_click()
                        action.perform()
                    except Exception as e:
                        pass
                time.sleep(helper.get_random(1,2))
                #check level up

        def claim():
            helper.print_message('Claim...')
            element=driver_helper.wait_element_appear(driver,value="//span[text()='Claim']/parent::button",timeout=10)
            if element is not None and driver_helper.web_element_is_clickable(element):
                helper.sleep(1,2)
                element.click()
                helper.print_message('Claim success')
                time.sleep(2)   

        def close_more_if_exist():
            element=driver_helper.wait_element_appear(driver,value="//*[text()='Morrre!']",timeout=10)
            if element is not None and driver_helper.web_element_is_clickable(element):
                helper.sleep(1,2)
                element.click()
                helper.print_message('Close more')
                time.sleep(2)   

        def input_email(email):
            helper.print_message('Check Email input')
            element=driver_helper.wait_element_appear(driver,value="//*[@id='email']",timeout=5)
            if element is None:
                return
            element.send_keys(email)
            helper.sleep(3,3)
            element=driver_helper.wait_element_appear(driver,value="//*[text()='Continue']",timeout=5)
            if element is None:
                return
            helper.sleep(2,3)
            element.click()
            helper.sleep(2,3)
        
        def farm():
            time.sleep(2)
            element=driver_helper.wait_element_appear(driver,value="//*[text()='Farm']",timeout=10)
            if element is not None and driver_helper.web_element_is_clickable(element):
                helper.sleep(1,2)
                element.click()
                helper.print_message("Click Tab Farm")
                time.sleep(2)   
                helper.print_message('Check Start farming era')
                element=driver_helper.wait_element_appear(driver,value="//*[text()='Start farming era']",timeout=10)
                if element is not None and driver_helper.web_element_is_clickable(element):
                    helper.sleep(1,2)
                    element.click()
                    helper.print_message("Click Start farming era")
                    time.sleep(2)   
                else:
                    helper.sleep(1,2)
                    claim()
                    helper.sleep(1,2)
                    close_more_if_exist()
                    helper.print_message('Check Start farming era')
                    element=driver_helper.wait_element_appear(driver,value="//*[text()='Start farming era']",timeout=10)
                    if element is not None and driver_helper.web_element_is_clickable(element):
                        helper.sleep(1,2)
                        element.click()
                        helper.print_message("Click Start farming era")
                        time.sleep(2)   
            else:
                helper.print_message("Không có claim")

        try:
            driver.get(url)
            input_email(row['email'])
            click_hero(time_click=10)
            claim()
            driver.refresh()
            farm()
        except Exception as e:
            helper.print_message(e)
        finally:
            # try:       
            #     driver_helper.delete_cache(driver,is_close=False)
            # except Exception as e:
            #     pass
            helper.print_message('Done...')
    helper.print_message(f"Close profile {PROFILE_NAME}")
    driver_login.close_profile(PROFILE_NAME)

if __name__=='__main__':
    while True:
        try:
            exec()
        except Exception as e:
            helper.print_message(e)