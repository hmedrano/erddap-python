# ERDDAP python library 

[![Build Status](https://travis-ci.com/hmedrano/erddap-python.svg?branch=main)](https://travis-ci.com/hmedrano/erddap-python)

## About

erddap-python is a python API implementation for the ERDDAP server.

ERDDAP is a data server that gives you a simple, consistent way to download subsets of gridded and tabular scientific datasets in common file formats and make graphs and maps. 

Full API reference can bue found [here](https://hmedrano.github.io/erddap-python/).

## Requirements

 - python 3
 - python libraries numpy, pandas, xarray, netCDF4

## Installation

Using pip:

```
$ pip install erddap-python
```

## Usage

### Explore a ERDDAP Server

Connect to a ERDDAP Server

```python
>>> from erddapClient import ERDDAP_Server
>>> 
>>> remoteServer = ERDDAP_Server('https://coastwatch.pfeg.noaa.gov/erddap')
>>> remoteServer
<erddapClient.ERDDAP_Server>
Server version:  ERDDAP_version=2.11
```

Search and advancedSerch methods that connects to the ERDDAP Restful services, usage:

```python
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

Using the Tabledap object to build ERDDAP URL's

```python

>>> from erddapClient import ERDDAP_Tabledap
>>> 
>>> url = 'https://coastwatch.pfeg.noaa.gov/erddap'
>>> datasetid = 'cwwcNDBCMet'
>>> remote = ERDDAP_Tabledap(url, datasetid)
>>> 
>>> remote.setResultVariables(['station','time','atmp'])
>>> print (remote.getURL('htmlTable'))

'https://coastwatch.pfeg.noaa.gov/erddap/tabledap/cwwcNDBCMet.htmlTable?station%2Ctime%2Catmp'

```

You can continue adding constraints and operations to the request. 

```python
>>> import datetime as dt 
>>> 
>>> remote.addConstraint('time>=2020-12-29T00:00:00Z') \
          .addConstraint({ 'time<=' : dt.datetime(2020,12,31) })
>>> remote.getURL()

'https://coastwatch.pfeg.noaa.gov/erddap/tabledap/cwwcNDBCMet.csvp?station%2Ctime%2Catmp&time%3E=2020-12-29T00%3A00%3A00Z&time%3C=2020-12-31T00%3A00%3A00Z'

>>>
>>> remote.orderByClosest(['station','time/1day'])
>>> remote.getURL()

'https://coastwatch.pfeg.noaa.gov/erddap/tabledap/cwwcNDBCMet.csvp?station%2Ctime%2Catmp&time%3E=2020-12-29T00%3A00%3A00Z&time%3C=2020-12-31T00%3A00%3A00Z&orderByClosest(%22station%2Ctime/1day%22)'

>>> 
```

> You can continue adding constraints, server side operations or the distinct operation to the url generation. 
> The class has object has methods to clear the result variables, the constraints, and the server side operations in the stack: `clearConstraints()`, `clearResultVariable()`, `clearServerSideFunctions` or `clearQuery()`

To request the data:

```python
>>>
>>> remote.clearQuery()
>>>
>>> responseCSV = (
>>>     remote.setResultVariables(['station','time','atmp'])
>>>           .addConstraint('time>=2020-12-29T00:00:00Z')
>>>           .addConstraint('time<=2020-12-31T00:00:00Z')
>>>           .orderByClosest(['station','time/1day'])
>>>           .getData('csvp')
>>> )
>>> 
>>> print(responseCSV)

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

>>>
>>> remote.clearQuery()
>>>
>>> responsePandas = (
>>>     remote.setResultVariables(['station','time','atmp'])
>>>           .addConstraint('time>=2020-12-29T00:00:00Z')
>>>           .addConstraint('time<=2020-12-31T00:00:00Z')
>>>           .orderByClosest(['station','time/1day'])
>>>           .getDataFrame()
>>> )
>>>
>>> responsePandas

     station            time (UTC)  atmp (degree_C)
0      41001  2020-12-29T00:00:00Z             17.3
1      41001  2020-12-30T00:00:00Z             13.7
2      41001  2020-12-31T00:00:00Z             15.9
3      41004  2020-12-29T00:00:00Z             18.2
4      41004  2020-12-30T00:00:00Z             17.1
...      ...                   ...              ...
2006   YKRV2  2020-12-30T00:00:00Z              NaN
2007   YKRV2  2020-12-31T00:00:00Z              8.1
2008   YKTV2  2020-12-29T00:00:00Z             11.3
2009   YKTV2  2020-12-30T00:00:00Z              NaN
2010   YKTV2  2020-12-31T00:00:00Z              7.1

[2011 rows x 3 columns]


```


### Griddap datasets

All the url building functions, and data request functionality is available in the ERDDAP_Griddap class, plus the
posibility to get the xarray object from the opendap endpoint provided by ERDDAP.


```python
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


