# ERDDAP python library 

## About

erddap-python is a python API implementation for the ERDDAP server.

ERDDAP is a data server that gives you a simple, consistent way to download subsets of gridded and tabular scientific datasets in common file formats and make graphs and maps. 


## Installation

Using pip:

```
$ pip install erddap-python
```

## Usage

## Explore a ERDDAP Server


### Tabledap datasets 

```
>>> from erddapClient import ERDDAP_Tabledap
>>> 
>>> url = 'https://coastwatch.pfeg.noaa.gov/erddap'
>>> datasetid = 'cwwcNDBCMet'
>>> remote = ERDDAP_Tabledap(url, datasetid)
>>> 
>>> response = (
>>>     remote.setResultVariables(['station','time','atmp'])
>>>           .addConstraint('time>=2020-12-29T00:00:00Z')
>>>           .addConstraint('time<=2020-12-31T00:00:00Z')
>>>           .orderByClosest(['station','time/1day'])
>>>           .getData('csvp')
>>> )
>>> 
>>> print(response)


station,time (UTC),atmp (degree_C)
41001,2020-12-29T00:00:00Z,17.3
41001,2020-12-30T00:00:00Z,13.7
41001,2020-12-31T00:00:00Z,15.9
41004,2020-12-29T00:10:00Z,18.1
41004,2020-12-30T00:00:00Z,17.1
41004,2020-12-31T00:00:00Z,21.2
41008,2020-12-29T00:50:00Z,14.8
...
.
```

### Griddap datasets

```
>>> from erddapClient import ERDDAP_Griddap
>>> 
>>> url = 'https://coastwatch.pfeg.noaa.gov/erddap'
>>> datasetid = 'ucsdHfrE1'
>>> remote = ERDDAP_Griddap(url, datasetid)
>>> 
>>> print(remote)

<erddapClient.ERDDAP_Griddap>
Title:       Currents, HF Radar, US East Coast and Gulf of Mexico, RTV, Near-Real Time, 2012-present, Hourly, 1km
Server URL:  https://coastwatch.pfeg.noaa.gov/erddap
Dataset ID:  ucsdHfrE1
Dimensions: 
  time (double) range=(cftime.DatetimeGregorian(2012, 1, 1, 0, 0, 0, 0), cftime.DatetimeGregorian(2021, 2, 2, 7, 0, 0, 0)) 
    Standard name: time 
    Units:         seconds since 1970-01-01T00:00:00Z 
  latitude (float) range=(21.7, 46.49442) 
    Standard name: latitude 
    Units:         degrees_north 
  longitude (float) range=(-97.88385, -57.19249) 
    Standard name: longitude 
    Units:         degrees_east 
Variables: 
  water_u (float) 
    Standard name: surface_eastward_sea_water_velocity 
    Units:         m s-1 
  water_v (float) 
    Standard name: surface_northward_sea_water_velocity 
    Units:         m s-1 
  DOPx (float) 
  DOPy (float) 
  hdop (float) 
  number_of_sites (byte) 
    Units:         count 
  number_of_radials (short) 
    Units:         count 

```
