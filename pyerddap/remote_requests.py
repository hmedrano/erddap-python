import os
import requests

def urlread(url, auth=None, **kwargs):

    response = requests.get(url, auth=auth, **kwargs)
    if response.status_code == 200:
        return response
    else:
        response.raise_for_status()

