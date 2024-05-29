from selenium import webdriver
import pandas as pd
import driver_helper
import helper

DEFAULT_WINDOW_SIZE=(300,500)
PROFILE_NAME="Test"



def exec():
    driver_login,driver=helper.start_profile(driver_name='GPM_LOGIN',profile_name=PROFILE_NAME,window_size=DEFAULT_WINDOW_SIZE) 
    df=pd.read_excel("account.xlsx",dtype={"url":str},sheet_name='metaboss')
    df=df[(~df['url'].isna()) & (df['url']!='')]
    df.reset_index(inplace=True)
    
    for idx,row in df.iterrows(): 
        url=row['url']
        if url is None:
            continue
        driver.get(url)   
        element=driver_helper.wait_element_appear(driver,"//body",timeout=30)
        helper.sleep(10)
        action = webdriver.common.action_chains.ActionChains(driver)
        # element=driver_helper.find_element(driver,"//body") 
        try:
            for i in range(500):
                if i%100==0:
                    print(f"{i}/500")
                try:
                    driver_helper.click_at(action,element,201,414)
                except Exception as e:
                    print(e)  
            # for i in range(237,400):
            #     if i%3!=0:
            #         continue
            #     for j in range(200,400):
            #         if j%3!=0:
            #             continue
            #         helper.print_message(f'{i} {j}')
            #         driver_helper.click_at(action,element,i,j)
                    # helper.sleep(0.5)
        except Exception as e:
            print(e)
        finally:
            driver_helper.delete_cache(driver,is_close=False)

        helper.print_message("Done")

    helper.print_message(f"Close profile {PROFILE_NAME}")
    driver_login.close_profile(PROFILE_NAME)

if __name__=='__main__':
    while True:
        try:
            exec()
        except Exception as e:
            helper.print_message(e)