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
PROFILE_NAME=constraint.MEMEFI_PROFILE

def exec():
    driver_login=helper.get_driver_login("GEN_LOGIN")
    df=pd.read_excel("account.xlsx",dtype={"url":str},sheet_name='memefi')
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
       
        def click_hero(time_click):
            print(f'[{row['profile']}] Attacking hero')
            xpath_animation="//div[@class='animation ']"
            element=driver_helper.wait_element_appear(driver,timeout=60, value=xpath_animation)
            if element is None:
                print(f'Not found {xpath_animation}')
            else:
                print(f'Found {xpath_animation}')
            
            for i in range(time_click):
                print(f'{i}/{time_click}')
                element=driver_helper.find_element(driver,value="//div[@class='animation ']")
                action = webdriver.common.action_chains.ActionChains(driver)
                action.w3c_actions.pointer_action._duration = helper.get_random(1,3)
                for j in range(100):
                    try:
                        if driver.current_url!='https://tg-app.memefi.club/game':
                            time.sleep(3)
                            continue
                        try:
                            action.move_to_element_with_offset(element,helper.get_random(-15,0),helper.get_random(-15,0))# helper.get_random(-20,-40), helper.get_random(-20,-40))
                            action.double_click()
                            action.perform()
                        except Exception as e:
                            pass
                            
                        
                    except Exception as e:
                        pass
                time.sleep(helper.get_random(1,2))
                #check level up

                element_countines=driver_helper.find_elements(driver,value="//p[text()='Continue Playing']")
                if element_countines is not None and len(element_countines)>0:
                    print('No element Continue Playing')
                    driver_helper.click_element(driver,value="//p[text()='Continue Playing']")
                    time.sleep(2)

        def booster():
            xpath_booster="//p[text()='Boosters']"
            print('click Boosters')
            driver_helper.click_element(driver,value=xpath_booster)
            time.sleep(1)
            driver_helper.wait_until_element_located(driver,timeout=20,value="//*[text()='Recharge']/following-sibling::span[@class='MuiTypography-root MuiTypography-bodyLittleBold css-18kcc4d' and contains(text(),'Boosts')]")
            time.sleep(1)
            element = WebDriverWait(driver,20).until(EC.presence_of_element_located((By.XPATH, "//*[text()='Recharge']/following-sibling::span[@class='MuiTypography-root MuiTypography-bodyLittleBold css-18kcc4d' and contains(text(),'Boosts')]")))
            time.sleep(1)
            if  not element.text.replace(" ","").startswith("0/"):
                print(f'Click Recharge {element.text}')
                element.click()
                recharge_elements=driver_helper.wait_elements_appear(driver,timeout=10,min_count=2,value="//p[contains(@class, 'MuiTypography-root') and contains(@class, 'MuiTypography-body1') and contains(@class, 'css-ibzb0o') and text()='claim boost']")
                if recharge_elements is not  None: 
                    try:
                        time.sleep(2)
                        print('Click Recharge')
                        recharge_elements[1].click()
                        print("Recharge full mana.Continue click...")
                        return True
                    except Exception as e:
                        print(e)
            else:
                print("No Recharge")
                
            
            def claim_bot_offline():
                '''Tiến hành claim bot offline'''
                # Kiểm tra chữ Available
                time.sleep(3)
                tap_bot_elements=driver_helper.wait_elements_appear(driver,timeout=5,value="//span[contains(text(), 'TAP BOT')] | //span[contains(text(), 'ACTIVATE TAP BOT')]")
                if tap_bot_elements is not None:
                    print(f'Click Tab Bot')
                    tap_bot_elements[0].click()
                    helper.sleep(2,2)
                    element=driver_helper.wait_element_appear(driver,timeout=3,value=f"//p[text()='Claim coins']/parent::button")
                    if element  is not None:
                        
                            if driver_helper.web_element_is_clickable(element):
                                try:
                                    print(f'Click Claim coins')
                                    element.click()
                                    helper.sleep(2,2) 
                                    print(f'Clicked Claim coins...')
                                except Exception as e:
                                    pass
                            # print(e)  
                            
                    time.sleep(1.5)
                    element=driver_helper.wait_element_appear(driver,timeout=3,value=f"//p[text()='Activate Bot']/parent::button")
                    if element  is not None:
                        if driver_helper.web_element_is_clickable(element):
                            try:
                                print(f'Click Activate Bot')
                                element.click()
                                helper.sleep(2,2) 
                                print(f'Clicked Activate Bot...')
                            except Exception as e:
                                # print(e)  
                                pass
                            
                    time.sleep(1.5)
                    # for key in ['Claim coins','Activate Bot']:
                    #     element=driver_helper.wait_elements_appear(driver,timeout=3,value=f"//p[text()='Claim coins']/parent::button")
                    #     if element  is not None:
                    #         try:
                    #             print(f'Click {key}')
                    #             element.click()
                    #             helper.sleep(2,2) 
                    #             print(f'Clicked {key}...')
                    #         except Exception as e:
                    #             print(e)  
                                
                    #     time.sleep(1.5)

            claim_bot_offline()

        try:
            driver.get(url)
            element=driver_helper.wait_element_appear(driver,value="//p[text()='Start Playing']",timeout=5)
            if element is not None:
                element.click()
                time.sleep(2)
            click_hero(time_click=3)
            while booster():
                click_hero(time_click=3)

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