import login_drivers.gen_login_driver
import login_drivers.gpm_login_driver
from helper.utils import print_message,sleep

def delete_profile(driver_name,profile_name):
    driver_login=get_driver_login(driver_name)
    driver_login.delete_profile(profile_name)

def start_profile(driver_name,profile_name,window_size):
    driver_login=get_driver_login(driver_name)
    is_success_open_profile=False
    chorme_config=None
    while not is_success_open_profile:
        print_message(f'Start profile {profile_name}')
        response=driver_login.start_profile(profile_name)
        if response.get("success")==False:
            try:
                print_message(f"Close profile {profile_name}")
                driver_login.close_profile(profile_name)
                sleep(5,5)
            except Exception as e:
                print_message(e)
                sleep(5,5)
        else:
            is_success_open_profile=True
            chorme_config=response.get("data")
          
    driver=driver_login.get_driver(
        chrome_driver_path=chorme_config.driver_path,
        debugger_address=chorme_config.debugger_address,
        window_size=window_size
    )
    return driver_login,driver

def get_driver_login(driver_name:str):
    if driver_name=="GEN_LOGIN":
        driver_login=login_drivers.gen_login_driver.GenLoginDriver(api_url='http://localhost:55550/backend/profiles')
    if driver_name=="GPM_LOGIN":   
        driver_login=login_drivers.gpm_login_driver.GPMLoginApiV3(api_url='http://127.0.0.1:19995/api/v3/profiles')
    return driver_login