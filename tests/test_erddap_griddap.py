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
    
    assert url == "https://coastwatch.pfeg.noaa.gov/erddap/griddap/erdTAgeomday?u_current[200:200][0:0][337:464][1018:1145],v_current[200:200][0:0][337:464][1018:1145]"
    assert urlquoted == "https://coastwatch.pfeg.noaa.gov/erddap/griddap/erdTAgeomday?u_current%5B200%3A200%5D%5B0%3A0%5D%5B337%3A464%5D%5B1018%3A1145%5D%2Cv_current%5B200%3A200%5D%5B0%3A0%5D%5B337%3A464%5D%5B1018%3A1145%5D"


@pytest.mark.vcr()
def test_griddap_subset_parsing2():
    url = 'https://coastwatch.pfeg.noaa.gov/erddap'
    datasetid = 'erdTAgeomday'
    remote = ERDDAP_Griddap(url, datasetid)
    remote.setResultVariables('u_current[(1999-04-16T00:00:00Z):1(2009-06-16T00:00:00Z)][(0.0)][(9.375):last-10][(254.625):(last-73.5)]')
    urlunquoted = remote.getDataRequestURL(filetype='opendap', useSafeURL=False)

    assert urlunquoted == "https://coastwatch.pfeg.noaa.gov/erddap/griddap/erdTAgeomday?u_current[78:1:200][0:0][337:589][1018:1145]"


@pytest.mark.vcr()
def test_griddap_subset_parsing3():
    url = 'https://coastwatch.pfeg.noaa.gov/erddap'
    datasetid = 'erdTAgeomday'
    remote = ERDDAP_Griddap(url, datasetid)
    remote.setResultVariables('u_current[1:10:200][0][337:589][1018:1145]')
    urlunquoted = remote.getDataRequestURL(filetype='opendap', useSafeURL=False)
    urlquoted = remote.getDataRequestURL(filetype='opendap', useSafeURL=True)
    print(urlquoted)
    assert urlunquoted == "https://coastwatch.pfeg.noaa.gov/erddap/griddap/erdTAgeomday?u_current[1:10:200][0:0][337:589][1018:1145]"
    assert urlquoted == "https://coastwatch.pfeg.noaa.gov/erddap/griddap/erdTAgeomday?u_current%5B1%3A10%3A200%5D%5B0%3A0%5D%5B337%3A589%5D%5B1018%3A1145%5D"


@pytest.mark.vcr()
def test_griddap_subset_outrange():
    url = 'https://coastwatch.pfeg.noaa.gov/erddap'
    datasetid = 'erdTAgeomday'
    remote = ERDDAP_Griddap(url, datasetid)
    remote.setResultVariables(['u_current[(1890-01-01T00:00:00Z)][(0.0)][(9.375):(41.125)][(254.625):(286.375)]',
                               'v_current[(2009-06-16T00:00:00Z)][(0.0)][(9.375):(41.125)][(254.625):(286.375)]'])

    with pytest.raises(Exception):
        url = remote.getDataRequestURL(filetype='opendap')


@pytest.mark.vcr()
def test_griddap_subset_doesntmatchnumberdimensions():
    url = 'https://coastwatch.pfeg.noaa.gov/erddap'
    datasetid = 'erdTAgeomday'
    remote = ERDDAP_Griddap(url, datasetid)
    remote.setResultVariables('v_current[(2009-06-16T00:00:00Z)][(0.0)][(9.375):(41.125)]')

    with pytest.raises(Exception):
        url = remote.getDataRequestURL(filetype='opendap')