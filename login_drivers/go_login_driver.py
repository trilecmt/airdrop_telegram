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
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

import time
from sys import platform
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from gologin import GoLogin
import constraint
import helper
from helper.utils import print_message


class GoLoginDriver:
    def __init__(self) -> None:
        pass
    
    def list_profiles(self)->list:
        url=f'{self.api_url}/api/v3/profiles'
        response=helper.helper_request.request_api(url)
        return [{"id":item["id"],"name":item["name"]} for item in response['data']]

    def close_profile(self,profile_name:str):
        url=f'{self.api_url}/api/v3/profiles/close/{self.get_profile_id(profile_name)}'
        response=helper.helper_request.request_api(url)
        print_message(response)
        return {"success":response['success']}


    def get_profile_id(self,profile_name:str)->str:
        for profile in self.profiles:
            if profile.get('name').upper()!=profile_name.upper():
                continue
            return profile.get('id')
        
    def start_profile(self,profile_id:str):
        gl = GoLogin({
            "token": constraint.GO_LOGIN_TOKEN,
            "profile_id": profile_id,
        })
        self.gl=gl
        debugger_address = self.gl.start()
        return {
            "success": True,
            "data":{
                "debugger_address":debugger_address
            }
        }   


    
    
    def close(self):
        self.driver.quit()
        print_message('Driver quitted')
        time.sleep(5)
        self.gl.stop()   
        print_message('Stopped Profile')
        time.sleep(5)
