import requests

from helper.utils import print_message


def request_api(api_url):
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise HTTPError for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print_message(f"Error: {e}" )
        return None