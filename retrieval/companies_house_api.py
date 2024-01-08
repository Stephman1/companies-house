import requests
from requests.auth import HTTPBasicAuth
import os
import json

class ChAPI():
    """
    A class for interacting with the Companies House API. 
    """
    
    def __init__(self) -> None:
        pass
    
    
    @staticmethod
    def getChData(url: str, api_key: str, params: dict = None, headers: dict = {'content-type': 'application/json'}) -> dict:
        """
        Hits the Companies House API and returns data as a dictionary.
        """
        try:
            response = requests.get(url=url, auth=HTTPBasicAuth(api_key, ''), params=params, headers=headers)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            return response.json()
        except requests.RequestException as e:
            print(f"Error during API request: {e}")
            return {}   
        
    
    @staticmethod
    def getApiKey(authentication_fp: str = None) -> str:
        """
        Get CH authentication key.
        
        Returns:
            str: API key for Companies House account
        """
        if authentication_fp is None:
            auth_file = ChAPI.getFileParDir('authentication.txt')
        else:
            auth_file = authentication_fp
        with open(auth_file,'r') as f:
            auth_dict = json.loads(f.read())
        return auth_dict['api_key']

    
    @staticmethod
    def getFileParDir(file_name: str) -> str:
        """
        Get the full path of a file in the parent directory.
        """
        parent_dir = os.path.abspath(os.path.join(os.pardir,os.getcwd()))
        full_fp = os.path.join(parent_dir, file_name)
        return full_fp
    
    
    @staticmethod
    def getDataFolderLocation(file_name: str, folder_name: str = "data") -> str:
        """
        Get the location of the data folder or create it if it doesn't exist.
        """
        parent_dir = os.path.abspath(os.path.join(os.pardir, os.getcwd()))
        data_folder = os.path.join(parent_dir, folder_name)
        
        # Create the 'data' folder if it doesn't exist
        if not os.path.exists(data_folder):
            os.makedirs(data_folder)

        full_fp = os.path.join(data_folder, file_name)
        return full_fp


if __name__ == '__main__':
    pass
