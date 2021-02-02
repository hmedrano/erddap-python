from functools import lru_cache
import requests
import os
import re


def getMessageError(response):
    """
     Extracts the error message from an ERDDAP error output.
    """
    emessageSearch = re.search(r'message="(.*)"', response)
    if emessageSearch:
        return emessageSearch.group(1)
    else:
        return ""
    
@lru_cache(maxsize=32)
def urlread(url, auth=None, **kwargs):
    """

    """
    response = requests.get(url, auth=auth, **kwargs)
    if response.status_code == 200:
        return response
    else:
        print ("ERDDAP Error: \"{}\"".format(getMessageError(response.text)))
        response.raise_for_status()

