import pandas as pd
import driver_helper
import time
import constraint
import helper

DEFAULT_WINDOW_SIZE=constraint.DEFAULT_WINDOW_SIZE
PROFILE_NAME="OCEANV2"

def claim_a_wallet(driver,wallet_name):
    helper.print_message(f'Claim {wallet_name}')
    try:
        frame=driver_helper.wait_element_appear(driver,value="//iframe",timeout=10)
        driver.switch_to.frame(frame)
        
        element=driver_helper.wait_element_appear(driver,value="//button[@class='relative p-4']",timeout=10)
        time.sleep(2)
        helper.print_message('click hpm')
        element.click()
        time.sleep(2)
        element=driver_helper.wait_element_appear(driver,value=f"//p[text()='{wallet_name}']",timeout=10)    
        time.sleep(2)
        helper.print_message(f'click wallet {wallet_name}')
        element.click()
        element=driver_helper.wait_element_appear(driver,value="//button[@class='w-full flex gap-2 justify-end text-white btn_claim']",timeout=10)
        if element is  not None:
            time.sleep(3)
            helper.print_message(f'click wallet claim')
            element.click()
            element=driver_helper.wait_element_appear(driver,value="//div[@class='claim cursor-pointer']",timeout=10)
            if element is not None:
                time.sleep(3)
                helper.print_message(f'click claim {wallet_name}')
                element.click()
                time.sleep(15)
            helper.print_message('click back')
            driver.back()
    except Exception as e:
        helper.print_message(e)
        
def exec():
    try:    
        driver_login,driver=helper.start_profile(driver_name='GPM_LOGIN',profile_name=PROFILE_NAME,window_size=DEFAULT_WINDOW_SIZE) 
        try: 
            driver.get("https://web.telegram.org/a/#6430669852")
            helper.sleep(5,15)
            element=driver_helper.wait_element_appear(driver,value="//*[@class='bot-menu-text']",timeout=30)
            if element is not None:
                helper.sleep(10,30)
                element.click()
                helper.sleep(5,10)

            helper.print_message("Check button Comfirm IP Address...")
            element=driver_helper.wait_element_appear(driver,value="//button[text()='Confirm']",timeout=5)
            if element is not None:
                helper.print_message("Click button Comfirm IP Address...")
                
                helper.sleep(1,4)
                element.click()
                helper.sleep(2,4)

            helper.print_message("Check button Launch...")
            element=driver_helper.wait_element_appear(driver,value="//*[text()='Confirm']",timeout=5)
            if element is not None:
                helper.print_message("Click Launch...")
                helper.sleep(1,3)
                element.click()
                helper.sleep(1,3)
            frame=driver_helper.wait_element_appear(driver,value="//iframe",timeout=10)
            helper.write_config(section='OCEAN',key='url',value=frame.get_property("src"))
            df=pd.read_excel("account.xlsx",dtype={"wave_wallet":str},sheet_name='ocean')
            df=df[(~df['wave_wallet'].isna()) & (df['wave_wallet']!='')]
            df.reset_index(inplace=True)
            df_reversed = df[::-1]
            df_reversed.reset_index(inplace=True)
            count=1
            while True:
                for idx,row in df_reversed.iterrows():
                    claim_a_wallet(driver,row['account_name'])
                    time.sleep(3)
                count+=1

        except Exception as e:
            pass

    except Exception as e:
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