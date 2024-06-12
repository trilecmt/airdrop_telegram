from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import constraint
import login_drivers.gen_login_driver

class ChormeDriverConfig:
    def __init__(self,debugger_address,driver_path) -> None:
        self.debugger_address=debugger_address
        self.driver_path=driver_path
        
def get_driver_login(driver_name:str):
        if driver_name=="GEN_LOGIN":
            driver_login=login_drivers.gen_login_driver.GenLoginDriver(api_url='http://localhost:55550/backend/profiles')
        # if driver_name=="GO_LOGIN":
        #     driver_login=login_drivers.go_login_driver.GoLoginDriver()
        return driver_login

class LoginDriverBase:

    @staticmethod
    
    
    def list_profiles(self)->list:
        pass
    
    def close_profile(self,profile_id:str):
        pass

    def get_profile_id(self,profile_name:str)->str:
        pass
        
    def start_profile(self,profile_name:str):
        pass
            
    def get_driver(self,debugger_address:str,window_size:tuple=None,chrome_driver_path=None):

        if window_size is None:
            window_size=constraint.DEFAULT_WINDOW_SIZE
        if chrome_driver_path is None:
            chrome_driver_path = constraint.CHORME_DRIVER_PATH
        service = Service(executable_path=chrome_driver_path)
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("headless")
            # Set the window size
        chrome_options.add_argument(f"--window-size={window_size[0]},{window_size[1]}")
        chrome_options.add_argument("--no-startup-window")
        chrome_options.set_capability(
            "goog:loggingPrefs", {"performance": "ALL"}
        )
        chrome_options.add_experimental_option("debuggerAddress", debugger_address)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_window_size(width=window_size[0],height=window_size[1])
        self.driver=driver
        return driver