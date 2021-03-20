# ERDDAP python library 

[![Build Status](https://travis-ci.com/hmedrano/erddap-python.svg?branch=main)](https://travis-ci.com/hmedrano/erddap-python)

## About

erddap-python is a python API implementation for the ERDDAP server.

ERDDAP is a data server that gives you a simple, consistent way to download subsets of gridded and tabular scientific datasets in common file formats and make graphs and maps. 

## Requirements

 - python 3
 - python libraries numpy, pandas, xarray

## Installation

Using pip:

```
$ pip install erddap-python
```

## Usage

### Explore a ERDDAP Server

Connect to a ERDDAP Server

```
>>> from erddapClient import ERDDAP_Server
>>> 
>>> remoteServer = ERDDAP_Server('https://coastwatch.pfeg.noaa.gov/erddap')
>>> remoteServer
<erddapClient.ERDDAP_Server>
Server version:  ERDDAP_version=2.11
```

Search and advancedSerch methods that connects to the ERDDAP Restful services, usage:

```
>>> searchRequest = remoteServer.advancedSearch(searchFor="gliders")
>>> searchRequest
<erddapClient.ERDDAP_SearchResults>
Results:  1
[
  0 - <erddapClient.ERDDAP_Tabledap> scrippsGliders , "Gliders, Scripps Institution of Oceanography, 2014-present"
]
```

The methods returns an object with a list of the ERDDAP Tabledap or Griddap objects that matched the search filters.

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

>>> # Get an xarray object
>>> remote.xarray

<xarray.Dataset>
Dimensions:            (latitude: 2759, longitude: 4205, time: 79521)
Coordinates:
  * time               (time) datetime64[ns] 2012-01-01 ... 2021-03-20T04:00:00
  * latitude           (latitude) float32 21.7 21.71 21.72 ... 46.48 46.49 46.49
  * longitude          (longitude) float32 -97.88 -97.87 -97.86 ... -57.2 -57.19
Data variables:
    water_u            (time, latitude, longitude) float32 ...
    water_v            (time, latitude, longitude) float32 ...
    DOPx               (time, latitude, longitude) float32 ...
    DOPy               (time, latitude, longitude) float32 ...
    hdop               (time, latitude, longitude) float32 ...
    number_of_sites    (time, latitude, longitude) float32 ...
    number_of_radials  (time, latitude, longitude) float32 ...
Attributes:
    _CoordSysBuilder:           ucar.nc2.dataset.conv.CF1Convention
    cdm_data_type:              Grid
    Conventions:                COARDS, CF-1.6, ACDD-1.3
    ..
    .

```
