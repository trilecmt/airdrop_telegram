import traceback
import pandas as pd
import driver_helper
import time
import constraint
import helper

DEFAULT_WINDOW_SIZE=constraint.DEFAULT_WINDOW_SIZE
PROFILE_NAME="OCEANV1"

def exec():
    try:    
        helper.delete_profile(driver_name='GPM_LOGIN',profile_name=PROFILE_NAME)
        driver_login,driver=helper.start_profile(driver_name='GPM_LOGIN',profile_name=PROFILE_NAME,window_size=DEFAULT_WINDOW_SIZE)  
        df=pd.read_excel("account.xlsx",dtype={"wave_wallet":str},sheet_name='ocean')
        df=df[(~df['wave_wallet'].isna()) & (df['wave_wallet']!='')]
        df.reset_index(inplace=True)
        df_reversed = df[::-1]
        df_reversed.reset_index(inplace=True)
        url=helper.read_config(section='OCEAN',key='url')
        for idx,row in df_reversed.iterrows():
            wallet_key=row['wave_wallet']
            helper.print_message(f'{idx+1}/{len(df)}.Processing profile {row['profile']}')
            try:
                driver.get(url)
                element=driver_helper.wait_element_appear(driver,value="//button[text()='Login']",timeout=10)
                if element is not None:
                    element.click()
                    time.sleep(2)
                    element=driver_helper.wait_element_appear(driver,value='//*[@id="section-login"]/div/div[1]/label/textarea',timeout=10)
                    element.send_keys(wallet_key)
                    time.sleep(2)
                    driver_helper.click_element(driver,value="//button[text()='Continue']")
                    time.sleep(2)

                element=driver_helper.wait_element_appear(driver,value="//button[@class='w-full flex gap-2 justify-end text-white btn_claim']",timeout=10)
                time.sleep(2)
                if element is  not None:
                    element.click()
                    time.sleep(2)
                    element=driver_helper.wait_element_appear(driver,value="//div[@class='claim cursor-pointer']",timeout=10)
                    if element is not None:
                        time.sleep(3)
                        element.click()
                        time.sleep(15)
            except Exception as e:
                pass  
            finally:
                driver_helper.delete_cache(driver, is_close=False)

    except Exception as e:
        print(traceback.format_exc())
        helper.print_message(e)
    finally:
        try:     
            driver_login.close_profile(PROFILE_NAME)
            time.sleep(3)
        except Exception as e:
            pass
                 
if __name__=='__main__':
    while True:
        try:
            exec()
        except Exception as e:
            helper.print_message(e)
            pass