import pytest 
from erddapClient import ERDDAP_Server
import datetime as dt

def test_simple_search():
    url = 'https://coastwatch.pfeg.noaa.gov/erddap'
    remote = ERDDAP_Server(url)
    searchURL = remote.getSearchURL(filetype='csv', searchFor='Gulf of Mexico')
    assert searchURL == 'https://coastwatch.pfeg.noaa.gov/erddap/search/index.csv?page=1&itemsPerPage=1000&searchFor=Gulf+of+Mexico'

def test_advanced_search():
    url = 'https://coastwatch.pfeg.noaa.gov/erddap'
    searchForString = 'Gulf of Mexico'
    protocol = 'griddap'
    remote = ERDDAP_Server(url)
    searchURL = remote.getAdvancedSearchURL(filetype='csv', searchFor='Gulf of Mexico', protocol='griddap', minTime='now-1month')
    assert searchURL == 'https://coastwatch.pfeg.noaa.gov/erddap/search/advanced.csv?page=1&itemsPerPage=1000&searchFor=Gulf+of+Mexico&protocol=griddap&cdm_data_type=%28ANY%29&institution=%28ANY%29&ioos_category=%28ANY%29&keywords=%28ANY%29&long_name=%28ANY%29&standard_name=%28ANY%29&variableName=%28ANY%29&maxLat=&minLon=&maxLon=&minLat=&minTime=now-1month&maxTime='    

def test_advanced_search_dt():
    url = 'https://coastwatch.pfeg.noaa.gov/erddap'
    searchForString = 'Gulf of Mexico'
    protocol = 'griddap'
    remote = ERDDAP_Server(url)
    searchURL = remote.getAdvancedSearchURL(filetype='csv', searchFor='Gulf of Mexico', protocol='griddap', minTime=dt.datetime(2010,12,24))
    print (searchURL)
    assert searchURL == 'https://coastwatch.pfeg.noaa.gov/erddap/search/advanced.csv?page=1&itemsPerPage=1000&searchFor=Gulf+of+Mexico&protocol=griddap&cdm_data_type=%28ANY%29&institution=%28ANY%29&ioos_category=%28ANY%29&keywords=%28ANY%29&long_name=%28ANY%29&standard_name=%28ANY%29&variableName=%28ANY%29&maxLat=&minLon=&maxLon=&minLat=&minTime=2010-12-24T00%3A00%3A00Z&maxTime='        

@pytest.mark.vcr()
def test_parsestatus():
    remotev211 = ERDDAP_Server('https://coastwatch.pfeg.noaa.gov/erddap') 
    assert remotev211.statusValues != None
    remotev202 = ERDDAP_Server('http://erddap-goldcopy.dataexplorer.oceanobservatories.org/erddap') 
    assert remotev202.statusValues != None
    
