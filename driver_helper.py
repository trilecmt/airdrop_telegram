from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import datetime
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
from pathlib import Path
from selenium.webdriver.remote.webelement import WebElement as webelement

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

def perform_actions(driver, keys):
    for i in range(0, len(keys)):
        actions = ActionChains(driver)
        actions.send_keys(keys[i])
        time.sleep(.3) #  adjust this if its going to fast\slow
        actions.perform()
    print("Actions performed!")

def delete_cache(driver):
    driver.execute_script("window.open('')")  # Create a separate tab than the main one
    driver.switch_to.window(driver.window_handles[-1])  # Switch window to the second tab
    driver.get('chrome://settings/clearBrowserData')  # Open your chrome settings.
    perform_actions(driver,Keys.TAB * 3 + Keys.LEFT + Keys.TAB * 6 + Keys.ENTER + Keys.TAB + Keys.ENTER + Keys.TAB + Keys.ENTER + Keys.TAB + Keys.ENTER + Keys.TAB * 2 + Keys.ENTER)  # Tab to the time select and key down to say "All Time" then go to the Confirm button and press Enter
    close(driver)
    

def close(driver):
    driver.close()  # Close that window
    driver.switch_to.window(driver.window_handles[0])  # Switch Selenium controls to the original tab to continue normal functionality.

# Example code to click an element with retry mechanism
def click_element(driver,value:str,index=0,by=By.XPATH):
    try:
        element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((by, value)))
        element.click()
    except Exception as e:
        print(e)
        pass
          

def web_element_is_clickable(web_element):
    return web_element.is_displayed() and web_element.is_enabled()


def wait_element_appear(driver:webdriver.Chrome,value:str,timeout:int,by=By.XPATH):
    start_time=datetime.datetime.now()
    while datetime.datetime.now()<(start_time+datetime.timedelta(seconds=timeout)):
        element=find_element(driver,value=value,by=by)
        if element is not None:
            return element
    return None

def wait_until_element_located(driver:webdriver.Chrome,value:str,timeout:int):
    try:
        element = WebDriverWait(driver,20).until(EC.presence_of_element_located((By.XPATH, "//*[text()='Recharge']/following-sibling::span[@class='MuiTypography-root MuiTypography-bodyLittleBold css-18kcc4d' and contains(text(),'Boosts')]")))
        return element
    except Exception as e:
        print(e)

def wait_until_elements_located(driver:webdriver.Chrome,value:str,timeout:int):
    pass


def wait_elements_appear(driver:webdriver.Chrome,value:str,timeout:int,min_count=1,by=By.XPATH):
    start_time=datetime.datetime.now()
    while datetime.datetime.now()<(start_time+datetime.timedelta(seconds=timeout)):
        elements=find_elements(driver,value=value,by=by)
        if elements is not None and len(elements)>=min_count:
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