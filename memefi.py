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

DEFAULT_WINDOW_SIZE=(400,800)


def exec(profile):
    driver_login,driver=helper.helper_driver.start_profile(driver_name='GPM_LOGIN',profile_name=profile['name'],window_size=DEFAULT_WINDOW_SIZE) 
    df=pd.read_excel("account.xlsx",dtype={"url":str},sheet_name='memefi')
    df=df[(~df['url'].isna()) & (df['url']!='') & (df['profile']==profile['name'])]

    df.reset_index(inplace=True)
    for idx,row in df.iterrows():
        url=row['url']
        url=url.replace("tgWebAppPlatform=weba","tgWebAppPlatform=android").replace("tgWebAppPlatform=web","tgWebAppPlatform=android")
        is_upgrade_dame=str(row['upgrade_dame'])
        if url is None:
            continue

        def click_hero(time_click):
            print_message(f"[{row['profile']}] Attacking hero")
            xpath_animation="//div[@class='animation ']"
            element=driver_helper.wait_element_appear(driver,timeout=60, value=xpath_animation)
            if element is None:
                print_message(f'Not found {xpath_animation}')
            else:
                print_message(f'Found {xpath_animation}')
            
            for i in range(time_click):
                print_message(f'{i}/{time_click}')
                element=driver_helper.find_element(driver,value="//div[@class='animation ']")
                action = webdriver.common.action_chains.ActionChains(driver)
                action.w3c_actions.pointer_action._duration = get_random(1,3)
                for j in range(100):
                    try:
                        if driver.current_url=='https://tg-app.memefi.club/boosters':
                            time.sleep(3)
                            continue
                        try:
                            action.move_to_element_with_offset(element,get_random(-15,0),get_random(-15,0))# helper.get_random(-20,-40), helper.get_random(-20,-40))
                            action.double_click()
                            action.perform()
                        except Exception as e:
                            pass
                            
                        
                    except Exception as e:
                        pass
                sleep(1,2)
                #check level up

                element_countines=driver_helper.find_elements(driver,value="//p[text()='Continue Playing']")
                if element_countines is not None and len(element_countines)>0:
                    helper.print_message('No element Continue Playing')
                    driver_helper.click_element(driver,value="//p[text()='Continue Playing']")
                    sleep(2)

        def booster():
            xpath_booster="//p[text()='Boosters']"
            helper.print_message('click Boosters')
            driver_helper.click_element(driver,value=xpath_booster)
            time.sleep(1)
            driver_helper.wait_until_element_located(driver,timeout=20,value="//*[text()='Recharge']/following-sibling::span[@class='MuiTypography-root MuiTypography-bodyLittleBold css-18kcc4d' and contains(text(),'Boosts')]")
            time.sleep(1)
            element = WebDriverWait(driver,20).until(EC.presence_of_element_located((By.XPATH, "//*[text()='Recharge']/following-sibling::span[@class='MuiTypography-root MuiTypography-bodyLittleBold css-18kcc4d' and contains(text(),'Boosts')]")))
            time.sleep(1)
            if  not element.text.replace(" ","").startswith("0/"):
                helper.print_message(f'Click Recharge {element.text}')
                element.click()
                recharge_elements=driver_helper.wait_elements_appear(driver,timeout=10,min_count=2,value="//p[contains(@class, 'MuiTypography-root') and contains(@class, 'MuiTypography-body1') and contains(@class, 'css-ibzb0o') and text()='claim boost']")
                if recharge_elements is not  None: 
                    try:
                        time.sleep(2)
                        helper.print_message('Click Recharge')
                        recharge_elements[1].click()
                        helper.print_message("Recharge full mana.Continue click...")
                        return True
                    except Exception as e:
                        helper.print_message(e)
            else:
                helper.print_message("No Recharge")
                
            
            def claim_bot_offline():
                '''Tiến hành claim bot offline'''
                # Kiểm tra chữ Available
                time.sleep(3)
                tap_bot_elements=driver_helper.wait_elements_appear(driver,timeout=5,value="//span[contains(text(), 'TAP BOT')] | //span[contains(text(), 'ACTIVATE TAP BOT')]")
                if tap_bot_elements is not None:
                    helper.print_message(f'Click Tab Bot')
                    tap_bot_elements[0].click()
                    helper.sleep(2,2)
                    element=driver_helper.wait_element_appear(driver,timeout=3,value=f"//p[text()='Claim coins']/parent::button")
                    if element  is not None:
                        
                            if driver_helper.web_element_is_clickable(element):
                                try:
                                    helper.print_message(f'Click Claim coins')
                                    element.click()
                                    helper.sleep(2,2) 
                                    helper.print_message(f'Clicked Claim coins...')
                                except Exception as e:
                                    pass
                            # helper.print_message(e)  
                            
                    time.sleep(1.5)
                    element=driver_helper.wait_element_appear(driver,timeout=3,value=f"//p[text()='Activate Bot']/parent::button")
                    if element  is not None:
                        if driver_helper.web_element_is_clickable(element):
                            try:
                                helper.print_message(f'Click Activate Bot')
                                element.click()
                                helper.sleep(2,2) 
                                helper.print_message(f'Clicked Activate Bot...')
                            except Exception as e:
                                # helper.print_message(e)  
                                pass
                            
                    time.sleep(1.5)
                    # for key in ['Claim coins','Activate Bot']:
                    #     element=driver_helper.wait_elements_appear(driver,timeout=3,value=f"//p[text()='Claim coins']/parent::button")
                    #     if element  is not None:
                    #         try:
                    #             helper.print_message(f'Click {key}')
                    #             element.click()
                    #             helper.sleep(2,2) 
                    #             helper.print_message(f'Clicked {key}...')
                    #         except Exception as e:
                    #             helper.print_message(e)  
                                
                    #     time.sleep(1.5)

            
            
            def upgrade_dame():
                if is_upgrade_dame!="1":
                    return
                try:
                    element=driver_helper.wait_element_appear(driver,timeout=3,value=f"//*[text()='DAMAGE']")
                    if element  is not None:
                        if driver_helper.web_element_is_clickable(element):
                            try:
                                helper.print_message(f'Click Upgrade Dame')
                                element.click()
                                helper.sleep(2,2) 
                                helper.print_message(f'Clicked Upgrade Dame...')
                                helper.sleep(2,2) 
                                #click vao nut Dong y     
                                element_upgrade=driver_helper.wait_element_appear(driver,timeout=3,value=f"//*[text()='upgrade']/parent::button")
                                if driver_helper.web_element_is_clickable(element_upgrade):
                                    helper.print_message(f'Click Upgrade Dame Confirm')
                                    helper.sleep(2,2) 
                                    from selenium.webdriver.common.action_chains import ActionChains    
                                    actionChains = ActionChains(driver)
                                    actionChains.double_click(element_upgrade).perform()
                                    # element_upgrade.double_click()
                                    helper.print_message(f'Clicked Upgrade Dame Confirm...')
                                    helper.sleep(2,2) 

                            except Exception as e:
                                # helper.print_message(e)  
                                pass
                except Exception as e:
                    helper.print_message(e)

            upgrade_dame()
            time.sleep(3)
            driver.refresh()
            claim_bot_offline()
            time.sleep(5)
        try:
            driver.get(url)
            time.sleep(3)
            element=driver_helper.wait_element_appear(driver,value="//*[text()='Best experienced on mobile. Play on your phone']",timeout=15)
            if element is not None:
                print("Change url mobile")
                url=url.replace("tgWebAppPlatform=weba","tgWebAppPlatform=android").replace("tgWebAppPlatform=web","tgWebAppPlatform=android")
                print(url)
                driver.refresh()
                time.sleep(3)
            element=driver_helper.wait_element_appear(driver,value="//p[text()='Start Playing']",timeout=5)
            if element is not None:
                element.click()
                time.sleep(2)

            click_hero(time_click=3)
            while booster():
                click_hero(time_click=3)

        except Exception as e:
            print_message(e)
        finally:
            # try:       
            #     driver_helper.delete_cache(driver,is_close=False)
            # except Exception as e:
            #     pass
            sleep(3)
            print_message('Done...')

    print_message(f"Close profile {profile['name']}")
    driver_login.close_profile(profile['name'])

if __name__=='__main__':
    count_processes=int(input("# profile:"))
    while True:
        try:      
            profiles=[]
            df=pd.read_excel("account.xlsx",dtype={"url":str},sheet_name='memefi')
            df=df[(~df['url'].isna()) & (df['url']!='')]
            for profile in list(df['profile'].unique()):
                profiles.append({"name":profile})
            with Pool(count_processes) as p:
                p.map(exec, profiles)
            time.sleep(df['delay'].iat[0])
        except Exception as e:
            print_message(e)