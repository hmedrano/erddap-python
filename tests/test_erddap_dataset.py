import pytest 
from erddapClient import ERDDAP_Tabledap
import datetime as dt 


@pytest.mark.vcr()
def test_remote_connection():
    url = 'https://coastwatch.pfeg.noaa.gov/erddap'
    datasetid = 'cwwcNDBCMet'
    remote = ERDDAP_Tabledap(url, datasetid)
    datasetTitle = remote.getAttribute('title')
    assert datasetTitle == 'NDBC Standard Meteorological Buoy Data, 1970-present'


def test_request_url_quoted_strings():
    url = 'https://coastwatch.pfeg.noaa.gov/erddap'
    datasetid = 'cwwcNDBCMet'
    remote = ERDDAP_Tabledap(url, datasetid)
    (
    remote.setResultVariables(['station','longitude','latitude','time','atmp'])
          .addConstraint({'station=' : '0Y2W3'})
          .addConstraint({'atmp>=' : 15})
          .addConstraint({'atmp<=' : 23})
          .orderByLimit(20)
    )
    orderbyurl_test = remote.getDataRequestURL()    
    print(orderbyurl_test)
    assert orderbyurl_test == 'https://coastwatch.pfeg.noaa.gov/erddap/tabledap/cwwcNDBCMet.csvp?station%2Clongitude%2Clatitude%2Ctime%2Catmp&station=%220Y2W3%22&atmp%3E=15&atmp%3C=23&orderByLimit(%2220%22)'

def test_request_url():
    url = 'https://coastwatch.pfeg.noaa.gov/erddap'
    datasetid = 'cwwcNDBCMet'
    remote = ERDDAP_Tabledap(url, datasetid)
    (
    remote.setResultVariables(['station','time','atmp'])
          .addConstraint('time>=2020-12-24T00:00:00Z')
          .addConstraint('time<=2020-12-31T01:15:00Z')
          .orderBy(['station'])
    )
    orderbyurl_test = remote.getDataRequestURL()
    remote.clearQuery()

    (
    remote.setResultVariables(['station','time','atmp'])
          .addConstraint('time>=2020-12-24T00:00:00Z')
          .addConstraint('time<=2020-12-31T01:15:00Z')
          .orderByClosest(['station','time/1day'])
    )
    orderbyclosest_test = remote.getDataRequestURL()
    remote.clearQuery()

    print (orderbyurl_test)
    assert orderbyurl_test == 'https://coastwatch.pfeg.noaa.gov/erddap/tabledap/cwwcNDBCMet.csvp?station%2Ctime%2Catmp&time%3E=2020-12-24T00%3A00%3A00Z&time%3C=2020-12-31T01%3A15%3A00Z&orderBy(%22station%22)'
    
    print (orderbyclosest_test)
    assert orderbyclosest_test == 'https://coastwatch.pfeg.noaa.gov/erddap/tabledap/cwwcNDBCMet.csvp?station%2Ctime%2Catmp&time%3E=2020-12-24T00%3A00%3A00Z&time%3C=2020-12-31T01%3A15%3A00Z&orderByClosest(%22station%2Ctime/1day%22)'


def test_request_url_dict_constraints():
    url = 'https://coastwatch.pfeg.noaa.gov/erddap'
    datasetid = 'cwwcNDBCMet'
    dtstart = dt.datetime(2020,12,24,0)
    dtend = dt.datetime(2020,12,31,1,15)

    remote = ERDDAP_Tabledap(url, datasetid)
    (
    remote.setResultVariables(['station','time','atmp'])
          .addConstraint( { 'time>=' : dtstart } )
          .addConstraint( { 'time<=' : dtend } )
          .orderBy(['station'])
    )
    orderbyurl_test = remote.getDataRequestURL()
    remote.clearQuery()

    (
    remote.setResultVariables(['station','time','atmp'])
          .addConstraint( { 'time>=' : dtstart } )
          .addConstraint( { 'time<=' : dtend } )
          .orderByClosest(['station','time/1day'])
    )
    orderbyclosest_test = remote.getDataRequestURL()
    remote.clearQuery()

    print (orderbyurl_test)
    assert orderbyurl_test == 'https://coastwatch.pfeg.noaa.gov/erddap/tabledap/cwwcNDBCMet.csvp?station%2Ctime%2Catmp&time%3E=2020-12-24T00%3A00%3A00Z&time%3C=2020-12-31T01%3A15%3A00Z&orderBy(%22station%22)'
    
    print (orderbyclosest_test)
    assert orderbyclosest_test == 'https://coastwatch.pfeg.noaa.gov/erddap/tabledap/cwwcNDBCMet.csvp?station%2Ctime%2Catmp&time%3E=2020-12-24T00%3A00%3A00Z&time%3C=2020-12-31T01%3A15%3A00Z&orderByClosest(%22station%2Ctime/1day%22)'


def test_request_url_time_constraints():
    url = 'https://coastwatch.pfeg.noaa.gov/erddap'
    datasetid = 'cwwcNDBCMet'
    dtstart = '2020-12-24T00:00:00Z'
    dtend = dt.datetime(2020,12,31,1,15)

    remote = ERDDAP_Tabledap(url, datasetid)
    (
    remote.setResultVariables(['station','time','atmp'])
          .addConstraint( { 'time>=' : dtstart } )
          .addConstraint( { 'time<=' : dtend } )
          .orderBy(['station'])
    )
    orderbyurl_test = remote.getDataRequestURL()  
    print (orderbyurl_test)    
    assert orderbyurl_test == 'https://coastwatch.pfeg.noaa.gov/erddap/tabledap/cwwcNDBCMet.csvp?station%2Ctime%2Catmp&time%3E=2020-12-24T00%3A00%3A00Z&time%3C=2020-12-31T01%3A15%3A00Z&orderBy(%22station%22)'

@pytest.mark.vcr()
def test_getattribute():
    url = 'https://coastwatch.pfeg.noaa.gov/erddap'
    datasetid = 'cwwcNDBCMet'
    remote = ERDDAP_Tabledap(url, datasetid)

    dsttitle = remote.getAttribute('title')
    dstwspd_comment = remote.getAttribute('comment','wspd')

    assert dsttitle == 'NDBC Standard Meteorological Buoy Data, 1970-present'
    assert dstwspd_comment == 'Average wind speed (m/s).'

@pytest.mark.vcr()
def test_tabledap_time_range_attribute():
    url = 'https://coastwatch.pfeg.noaa.gov/erddap'
    datasetid = 'cwwcNDBCMet'
    remote = ERDDAP_Tabledap(url, datasetid) 

    time_actual_range = remote.variables['time']['actual_range']
    print(time_actual_range)
    assert time_actual_range[0] == dt.datetime(1970,2,26,20)
    assert time_actual_range[1] == dt.datetime(2021,4,6,21,35)