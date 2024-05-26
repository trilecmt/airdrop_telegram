import requests
import helper
from login_drivers.login_driver_base import ChormeDriverConfig, LoginDriverBase

class GPMLoginApiV3(LoginDriverBase):
    def __init__(self,api_url:str) -> None:
        self.api_url=api_url
        self.profiles=self.list_profiles()
    
    def list_profiles(self)->list:
        url=f'{self.api_url}'
        response=helper.request_api(url)
        return [{"id":item["id"],"name":item["name"]} for item in response['data']]

    def delete_profile(self,profile_name:str):
        url=f'{self.api_url}/delete/{self.get_profile_id(profile_name)}?mode=2'
        response=helper.request_api(url)
        helper.print_message(response)
        return {"success":response['success']}
    
    def close_profile(self,profile_name:str):
        url=f'{self.api_url}/close/{self.get_profile_id(profile_name)}'
        response=helper.request_api(url)
        helper.print_message(response)
        return {"success":response['success']}

    def create_profile(self,profile_name:str):
        import json
        url=f'{self.api_url}/create'
        try:
            response = requests.post(url,data=json.dumps(
                {
                    "profile_name" : profile_name,
                    "group_name": "All",
                    "browser_core": "chromium",
                    "browser_name": "Chrome",
                    "browser_version": "124.0.6367.29",
                    "is_random_browser_version": False,
                    "raw_proxy" : "",
                    "startup_urls": "",
                    "is_masked_font": True,
                    "is_noise_canvas": False,
                    "is_noise_webgl": False,
                    "is_noise_client_rect": False,
                    "is_noise_audio_context": True,
                    "is_random_screen": False,
                    "is_masked_webgl_data": True,
                    "is_masked_media_device": True,
                    "is_masked_font": True,
                    "is_random_os": False,
                    "os": "Windows 11",
                    "webrtc_mode": 2,
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                })
            )
            response.raise_for_status()  # Raise HTTPError for bad status codes
            helper.print_message(response.json())
            self.profiles=self.list_profiles()
            return response.json()
        except requests.exceptions.RequestException as e:
            helper.print_message("Error:", e)
        
    
        response=helper.request_api(url)
        helper.print_message(response)
        return {"success":response['success']}

    def get_profile_id(self,profile_name:str)->str:
        for profile in self.profiles:
            if profile.get('name').upper()!=profile_name.upper():
                continue
            return profile.get('id')
        
    def start_profile(self,profile_name:str):
        profile_id=self.get_profile_id(profile_name)
        if profile_id is None:
            self.create_profile(profile_name)
            self.profiles=self.list_profiles()
            return self.start_profile(profile_name) 
        url=f'{self.api_url}/start/{profile_id}'
        data=helper.request_api(url)
        helper.print_message(data)
        if data['success']:
            return {
                "success": data['success'],
                "data":ChormeDriverConfig(
                    debugger_address=data['data'].get('remote_debugging_address',None),
                    driver_path=data['data'].get('driver_path',None)
                ) 
            }   
        return   {
            "success": False,
        }   
