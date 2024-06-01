import traceback
import pandas as pd
import driver_helper
import time
import constraint
import helper
from helper.utils import print_message, sleep


DEFAULT_WINDOW_SIZE=(300,450)
PROFILE_NAME="OCEANV1"

def exec(): 
    helper.helper_driver.delete_profile(driver_name='GPM_LOGIN',profile_name=PROFILE_NAME)
    driver_login,driver=helper.helper_driver.start_profile(driver_name='GPM_LOGIN',profile_name=PROFILE_NAME,window_size=DEFAULT_WINDOW_SIZE)  
    driver.execute_script("document.body.style.zoom='80%'") 
    while True:
            df=pd.read_excel("account.xlsx",dtype={"wave_wallet":str},sheet_name='ocean')
            df=df[(~df['wave_wallet'].isna()) & (df['wave_wallet']!='')]
            df.reset_index(inplace=True)
            df_reversed = df[::-1]
            df_reversed.reset_index(inplace=True)     
            for idx,row in df_reversed.iterrows():
                url=helper.utils.read_config(section='OCEAN',key='url')
                wallet_key=row['wave_wallet']
                print_message(f'{idx+1}/{len(df)}.Processing profile {row['profile']}')
                try:
                    driver.get(url)
                    element=driver_helper.wait_element_appear(driver,value="//button[text()='Login']",timeout=10)
                    if element is not None:
                        element.click()
                        sleep(2)
                        element=driver_helper.wait_element_appear(driver,value='//*[@id="section-login"]/div/div[1]/label/textarea',timeout=10)
                        element.send_keys(wallet_key)
                        sleep(2)
                        driver_helper.click_element(driver,value="//button[text()='Continue']")
                        sleep(2)

                    element=driver_helper.wait_element_appear(driver,value="//button[@class='w-full flex gap-2 justify-end text-white btn_claim']",timeout=10)
                    sleep(2)
                    if element is  not None:
                        element.click()
                        sleep(2)
                        element=driver_helper.wait_element_appear(driver,value="//div[@class='claim cursor-pointer']",timeout=10)
                        if element is not None:
                            sleep(3)
                            element.click()
                            sleep(15)
                except Exception as e:
                    print_message(e)
                finally:
                    driver_helper.delete_cache(driver, is_close=False)
                 
if __name__=='__main__':
    exec()