import helper
from gpm_login_api_v3 import GPMLoginApiV3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import datetime
import time
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import random
import asyncio
import multiprocessing
import asyncio
from concurrent.futures.thread import ThreadPoolExecutor


# Example code to click an element with retry mechanism
def click_element(driver,value:str,index=0,by=By.XPATH):
    try:
        element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((by, value)))
        element.click()
    except Exception as e:
        print(e)
        pass
          

def wait_element_appear(driver:webdriver.Chrome,value:str,timeout:int,by=By.XPATH):
    start_time=datetime.datetime.now()
    while datetime.datetime.now()<(start_time+datetime.timedelta(seconds=timeout)):
        element=find_element(driver,value=value,by=by)
        if element is not None:
            return element
    return None

def wait_elements_appear(driver:webdriver.Chrome,value:str,timeout:int,by=By.XPATH):
    start_time=datetime.datetime.now()
    while datetime.datetime.now()<(start_time+datetime.timedelta(seconds=timeout)):
        elements=find_elements(driver,value=value,by=by)
        if elements is not None:
            return elements
    return None

def find_elements(driver:webdriver.Chrome,value:str,by=By.XPATH):
    try:
        elements=driver.find_elements(by,value)
        return elements
    except:
        return None
    
def find_element(driver:webdriver.Chrome,value:str,index=0,by=By.XPATH):
    try:
        elements=find_elements(driver,value=value,by=by)
        return elements[index]
    except:
        return None

def get_random(min,max):
    return random.randint(min,max)

def main():
    gpm_login=GPMLoginApiV3(api_url='http://127.0.0.1:19995')
    df=pd.read_excel("account.xlsx")
    for idx,row in df.iterrows():
        profile_name=row['profile']
        url=row['memefi']
        print(f'{idx+1}/{len(df)}.Processing profile {row['profile']}')
        response=gpm_login.start_profile(profile_name=profile_name)
        if response.get('success')==False:
            print(response)
            continue
        data=response.get('data')
        print(data)

        browser_location=data.get('browser_location')
        remote_address=data.get('remote_debugging_address')
        chrome_driver_path=data.get('driver_path')
        
        # Create a ChromeDriverService
        chrome_driver_service = Service(chrome_driver_path)

        # Configure ChromeOptions
        chrome_options = webdriver.ChromeOptions()
        chrome_options.debugger_address = remote_address

        # Set the window size
        chrome_options.add_argument("--window-size=600,800")

        # Start ChromeDriver with ChromeDriverService and ChromeOptions
        driver = webdriver.Chrome(service=chrome_driver_service, options=chrome_options)

        def go_page(url):
            print(f'[{row['profile']}] Go to {url}')
            driver.get(url)
        
        def click_hero(time_click,sleep_time):
            print(f'[{row['profile']}] Attacking hero')
            xpath_animation="//div[@class='animation ']"
            element=wait_element_appear(driver,timeout=60, value=xpath_animation)
            if element is None:
                print(f'Not found {xpath_animation}')
            else:
                print(f'Found {xpath_animation}')
            
            for i in range(time_click):
                print(f'{i}/{time_click}')
                element=find_element(driver,value="//div[@class='animation ']")
                action = webdriver.common.action_chains.ActionChains(driver)
                action.w3c_actions.pointer_action._duration = get_random(3,10)
                for j in range(100):
                    try:
                        action.move_to_element_with_offset(element, get_random(-20,20), get_random(-20,20))
                        action.double_click()
                        action.perform()
                        time.sleep(random(10,50))
                    except Exception as e:
                        pass
                #check level up

                element_countine=find_element(driver,value="//p[text()='Continue Playing']")
                if element_countine is not None and len(element_countine)>0:
                    print('No element Continue Playing')
                    click_element(driver,value="//p[text()='Continue Playing']")
                    time.sleep(3)
                else:
                    time.sleep(sleep_time)


        # def booster():
        #     xpath_booster="//p[text()='Boosters']"
        #     click_element(driver,value=xpath_booster)
        #     elements=wait_elements_appear(driver,timeout=10,value="//span[@class='MuiTypography-root MuiTypography-bodyLittleBold css-18kcc4d']")
        #     if elements is None:
        #         return
        #     if elements is not None:
        #         if elements[1].text=='0/3 Boosts':
        #             print('No booster.Back home page')              
        #             return False

        #         click_element(driver,index=1, value="//button[@class='MuiButtonBase-root MuiButton-root MuiButton-primary MuiButton-primaryPrimary MuiButton-sizeLarge MuiButton-primarySizeLarge MuiButton-colorPrimary MuiButton-root MuiButton-primary MuiButton-primaryPrimary MuiButton-sizeLarge MuiButton-primarySizeLarge MuiButton-colorPrimary css-1opfuue']")
        #         element=wait_element_appear(driver,timeout=10,value="//button[@class='MuiButtonBase-root MuiButton-root MuiButton-primary MuiButton-primaryPrimary MuiButton-sizeLarge MuiButton-primarySizeLarge MuiButton-colorPrimary MuiButton-root MuiButton-primary MuiButton-primaryPrimary MuiButton-sizeLarge MuiButton-primarySizeLarge MuiButton-colorPrimary css-1ew4p28']")
        #         if element is None:
        #             return False
        #         main_window = driver.current_window_handle

        #         # click whatever button it is to open popup

        #         # after opening popup, change window handle
        #         for handle in driver.window_handles: 
        #             if handle != main_window: 
        #                 popup = handle
        #                 driver.switch_to_window(popup)
        #         click_element(driver,value="//button[@class='MuiButtonBase-root MuiButton-root MuiButton-primary MuiButton-primaryPrimary MuiButton-sizeLarge MuiButton-primarySizeLarge MuiButton-colorPrimary MuiButton-root MuiButton-primary MuiButton-primaryPrimary MuiButton-sizeLarge MuiButton-primarySizeLarge MuiButton-colorPrimary css-1ew4p28']")
        #         return True


        go_page(url)
        click_hero(time_click=5,sleep_time=1)
        # while booster():
        #     click_hero(time_click=100,sleep_time=1)
        try:
            driver.close()
        except:
            pass

async def main():
    urls = ["https://example.com", "https://example.org", "https://example.net"]

    # Đặt giới hạn là 2 yêu cầu đồng thời
    semaphore = asyncio.Semaphore(2)

    tasks = [fetch_data(url, semaphore) for url in urls]
    results = await asyncio.gather(*tasks)

    for result in results:
        print(result)

if __name__=='__main__':
     while True:
         asyncio.run(main())
     df=pd.read_excel("account.xlsx")
     data=df[['profile,memefi']].to_records()
     with multiprocessing.Pool(processes=5) as pool:
        # Run the main coroutine in each process
        main()
        pool.map(asyncio.run, [main(links) for _ in range(5)])

    