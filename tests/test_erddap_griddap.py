import pytest 
from erddapClient import ERDDAP_Griddap
import datetime as dt 

@pytest.mark.vcr()
def test_griddap_subset_parsing():
    url = 'https://coastwatch.pfeg.noaa.gov/erddap'
    datasetid = 'erdTAgeomday'
    remote = ERDDAP_Griddap(url, datasetid)
    remote.setResultVariables(['u_current[(2009-06-16T00:00:00Z)][(0.0)][(9.375):(41.125)][(254.625):(286.375)]',
                               'v_current[(2009-06-16T00:00:00Z)][(0.0)][(9.375):(41.125)][(254.625):(286.375)]'])
    url = remote.getDataRequestURL(filetype='opendap', useSafeURL=False)
    urlquoted = remote.getDataRequestURL(filetype='opendap', useSafeURL=True)
    print (url)
    print (urlquoted)
    
    assert url == "https://coastwatch.pfeg.noaa.gov/erddap/griddap/erdTAgeomday?u_current[200][0][337:464][1018:1145],v_current[200][0][337:464][1018:1145]"
    assert urlquoted == "https://coastwatch.pfeg.noaa.gov/erddap/griddap/erdTAgeomday?u_current%5B200%5D%5B0%5D%5B337%3A464%5D%5B1018%3A1145%5D%2Cv_current%5B200%5D%5B0%5D%5B337%3A464%5D%5B1018%3A1145%5D"