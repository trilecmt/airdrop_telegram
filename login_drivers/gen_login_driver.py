import requests
import helper
from helper.utils import print_message
from login_drivers.login_driver_base import ChormeDriverConfig, LoginDriverBase

class GenLoginDriver(LoginDriverBase):

    def __init__(self,api_url:str='',api_key='') -> None:
        self.api_url = api_url
        self.api_key=api_key
        self.profiles=self.list_profiles()
    
    def list_profiles(self)->list:
        response=helper.request_api(self.api_url)
        items= response['data']['items']
        return [{'id':item['id'],'name':item['profile_data']['name']} for item in items]
    
    def close_profile(self,profile_name:str):
        url = f'{self.LOCAL_URL}/{id}/stop'
        try:
            response = requests.put(url)
            response.raise_for_status()
            data= response.json()
            print_message(data)
            return data
        
        except requests.exceptions.RequestException as err:
            return err.response.json()
        
    


    def get_profile_id(self,profile_name:str)->str:
        for profile in self.profiles:
            if profile.get('name').upper()!=profile_name.upper():
                continue
            return profile.get('id')
    
    def get_ws_endpoint(self, id):
        url = f'{self.api_url}/{id}/ws-endpoint'
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as err:
            return err.response.json()
        
    def start_profile(self,profile_name:str):
        profile_id=self.get_profile_id(profile_name)
        if profile_id is None:
            print_message(f"profile {profile_name} is not found.")
            return
        url = f'{self.api_url}/{profile_id}/start'

        try:
            resEndpoint = self.get_ws_endpoint(id)
            if  resEndpoint["data"]["wsEndpoint"] != '' : 
                return {'success': True, 'wsEndpoint': resEndpoint["data"]["wsEndpoint"]}
            
            response = requests.put(url)
            response.raise_for_status()
            if response.json().get('success'):
                return {
                    'success': True,
                    'data': ChormeDriverConfig(
                        debugger_address=response.json()['data']["wsEndpoint"].replace("ws://","").split('/')[0],
                        driver_path=None
                    )
                }# 'wsEndpoint': response.json().get('data').get('wsEndpoint')}
            else:
                resEndpoint = self.get_ws_endpoint(id)
                if resEndpoint.get('wsEndpoint') != '':
                    return {'success': True, **resEndpoint}
                else:
                    return {'success': False, 'message': 'Profile is running in another device'}
        except requests.exceptions.RequestException as err:
            return err.response.json()
        
            
