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

PROFILE_NAME="DOT"#input("Enter profile name:")
IS_REVERSE=0#input("Enter huong 1(nguoc)/0:")

def exec():
    driver_login,driver=helper.start_profile(driver_name='GPM_LOGIN',profile_name=PROFILE_NAME,window_size=DEFAULT_WINDOW_SIZE) 

    driver.get("https://dot.dapplab.xyz/#tgWebAppData=query_id%3DAAEYkl0oAwAAABiSXSgbvdif%26user%3D%257B%2522id%2522%253A7119671832%252C%2522first_name%2522%253A%2522ChuThiCamTiep%2522%252C%2522last_name%2522%253A%2522%2522%252C%2522username%2522%253A%2522camtoo20%2522%252C%2522language_code%2522%253A%2522vi%2522%252C%2522allows_write_to_pm%2522%253Atrue%257D%26auth_date%3D1716906629%26hash%3D610248081a7849333fe94c6491454cea8d902359d1d22bf4fca9d16bcc2a247f&tgWebAppVersion=7.2&tgWebAppPlatform=android&tgWebAppThemeParams=%7B%22bg_color%22%3A%22%23ffffff%22%2C%22button_color%22%3A%22%233390ec%22%2C%22button_text_color%22%3A%22%23ffffff%22%2C%22hint_color%22%3A%22%23707579%22%2C%22link_color%22%3A%22%2300488f%22%2C%22secondary_bg_color%22%3A%22%23f4f4f5%22%2C%22text_color%22%3A%22%23000000%22%2C%22header_bg_color%22%3A%22%23ffffff%22%2C%22accent_text_color%22%3A%22%233390ec%22%2C%22section_bg_color%22%3A%22%23ffffff%22%2C%22section_header_text_color%22%3A%22%233390ec%22%2C%22subtitle_text_color%22%3A%22%23707579%22%2C%22destructive_text_color%22%3A%22%23df3f40%22%7D")
    element=driver_helper.wait_element_appear(driver,value="//*[@class='ClickerCoinDot']",timeout=10)
    if element is not None:
        for i in range(100):
            element.click()
            time.sleep(0.2)
    
    helper.print_message(f"Close profile {PROFILE_NAME}")
    driver_login.close_profile(PROFILE_NAME)

if __name__=='__main__':
    while True:
        try:
            exec()
        except Exception as e:
            helper.print_message(e)