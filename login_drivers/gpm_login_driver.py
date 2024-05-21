import helper

class GPMLoginApiV3():
    def __init__(self,api_url:str) -> None:
        self.api_url=api_url
        self.profiles=self.list_profiles()
    
    def list_profiles(self)->list:
        url=f'{self.api_url}/api/v3/profiles'
        response=helper.request_api(url)
        return [{"id":item["id"],"name":item["name"]} for item in response['data']]

    def close_profile(self,profile_name:str):
        url=f'{self.api_url}/api/v3/profiles/close/{self.get_profile_id(profile_name)}'
        response=helper.request_api(url)
        print(response)
        return {"success":response['success']}


    def get_profile_id(self,profile_name:str)->str:
        for profile in self.profiles:
            if profile.get('name').upper()!=profile_name.upper():
                continue
            return profile.get('id')
        
    def start_profile(self,profile_name:str):
        profile_id=self.get_profile_id(profile_name)
        if profile_id is None:
            return   {
                "success": False,
            }   
        url=f'{self.api_url}/api/v3/profiles/start/{profile_id}'
        data=helper.request_api(url)
        print(data)
        if data['success']:
            return {
                "success": data['success'],
                "data":{
                    "remote_debugging_address":data['data'].get('remote_debugging_address',None),
                    "driver_path":data['data'].get('driver_path',None),
                    "remote_debugging_address":data['data'].get('remote_debugging_address',None)
                }
                
            }   
        return   {
            "success": False,
        }   
