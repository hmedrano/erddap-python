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

search and advancedSerch methods are available, builds the search request URL and also can 
make the request to the ERDDAP restful services to obtain results. Usage:

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

Using the Tabledap object to build ERDDAP data request URL's

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

You can continue adding constraints and server side operations to the request. 

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

Usage sample:

```python
>>> from erddapClient import ERDDAP_Griddap
>>> 
>>> url = 'https://coastwatch.pfeg.noaa.gov/erddap'
>>> datasetid = 'hycom_gom310D'
>>> remote = ERDDAP_Griddap(url, datasetid)
>>> 
>>> print(remote)

<erddapClient.ERDDAP_Griddap>
Title:       NRL HYCOM 1/25 deg model output, Gulf of Mexico, 10.04 Expt 31.0, 2009-2014, At Depths
Server URL:  https://coastwatch.pfeg.noaa.gov/erddap
Dataset ID:  hycom_gom310D
Dimensions: 
  time (double) range=(cftime.DatetimeGregorian(2009, 4, 2, 0, 0, 0, 0), cftime.DatetimeGregorian(2014, 8, 30, 0, 0, 0, 0)) 
    Standard name: time 
    Units:         seconds since 1970-01-01T00:00:00Z 
  depth (float) range=(0.0, 5500.0) 
    Standard name: depth 
    Units:         m 
  latitude (float) range=(18.09165, 31.96065) 
    Standard name: latitude 
    Units:         degrees_north 
  longitude (float) range=(-98.0, -76.40002) 
    Standard name: longitude 
    Units:         degrees_east 
Variables: 
  temperature (float) 
    Standard name: sea_water_potential_temperature 
    Units:         degC 
  salinity (float) 
    Standard name: sea_water_practical_salinity 
    Units:         psu 
  u (float) 
    Standard name: eastward_sea_water_velocity 
    Units:         m/s 
  v (float) 
    Standard name: northward_sea_water_velocity 
    Units:         m/s 
  w_velocity (float) 
    Standard name: upward_sea_water_velocity 
    Units:         m/s 

>>> # Get more information about dimensions
>>> from pprint import pprint
>>> pprint(remote.dimensions)

{'depth': {'_CoordinateAxisType': 'Height',
           '_CoordinateZisPositive': 'down',
           '_averageSpacing': 141.02564102564102,
           '_dataType': 'float',
           '_evenlySpaced': False,
           '_nValues': 40,
           'actual_range': (0.0, 5500.0),
           'axis': 'Z',
           'ioos_category': 'Location',
           'long_name': 'Depth',
           'positive': 'down',
           'standard_name': 'depth',
           'units': 'm'},
 'latitude': {'_CoordinateAxisType': 'Lat',
              '_averageSpacing': 0.0361171875,
              '_dataType': 'float',
              '_evenlySpaced': False,
              '_nValues': 385,
              'actual_range': (18.09165, 31.96065),
              'axis': 'Y',
              'ioos_category': 'Location',
              'long_name': 'Latitude',
              'standard_name': 'latitude',
              'units': 'degrees_north'},
 'longitude': {'_CoordinateAxisType': 'Lon',
               '_averageSpacing': 0.039999962962962966,
               '_dataType': 'float',
               '_evenlySpaced': True,
               '_nValues': 541,
               'actual_range': (-98.0, -76.40002),
               'axis': 'X',
               'ioos_category': 'Location',
               'long_name': 'Longitude',
               'standard_name': 'longitude',
               'units': 'degrees_east'},
 'time': {'_CoordinateAxisType': 'Time',
          '_averageSpacing': '1 day',
          '_dataType': 'double',
          '_evenlySpaced': True,
          '_nValues': 1977,
          'actual_range': (cftime.DatetimeGregorian(2009, 4, 2, 0, 0, 0, 0),
                           cftime.DatetimeGregorian(2014, 8, 30, 0, 0, 0, 0)),
          'axis': 'T',
          'calendar': 'standard',
          'ioos_category': 'Time',
          'long_name': 'Time',
          'standard_name': 'time',
          'time_origin': '01-JAN-1970 00:00:00',
          'units': 'seconds since 1970-01-01T00:00:00Z'}}

>>> # Request a subset
>>>
>>> remote.clearQuery()
>>> subset = ( remote.setResultVariables(["temperature[0:last][(0.0)][(22.5)][(-95.5)]",
                                           "salinity[0:last][(0.0)][(22.5)][(-95.5)]"])
                     .getDataFrame(header=0, 
                                   names=["time", "depth", "latitude", "longitude", "temperature", "salinity"], 
                                   parse_dates=["time"],
                                   ndex_col="time")  )
>>>
>>> subset.head()                              

                           depth  latitude  longitude  temperature   salinity
time                                                                         
2009-04-02 00:00:00+00:00    0.0  22.51696  -95.47998    24.801798  36.167076
2009-04-03 00:00:00+00:00    0.0  22.51696  -95.47998    24.605570  36.256450
2009-04-04 00:00:00+00:00    0.0  22.51696  -95.47998    24.477884  36.086346
2009-04-05 00:00:00+00:00    0.0  22.51696  -95.47998    24.552357  36.133224
2009-04-06 00:00:00+00:00    0.0  22.51696  -95.47998    25.761946  36.179676
...                          ...       ...        ...          ...        ...
2014-08-26 00:00:00+00:00    0.0  22.51696  -95.47998    30.277546  36.440037
2014-08-27 00:00:00+00:00    0.0  22.51696  -95.47998    30.258907  36.485844
2014-08-28 00:00:00+00:00    0.0  22.51696  -95.47998    30.298597  36.507530
2014-08-29 00:00:00+00:00    0.0  22.51696  -95.47998    30.246874  36.493400
2014-08-30 00:00:00+00:00    0.0  22.51696  -95.47998    30.387840  36.487934

[1977 rows x 5 columns]

>>> # Get an xarray object
>>> remote.xarray

<xarray.Dataset>
Dimensions:            (latitude: 2759, longitude: 4205, time: 79521)
Coordinates:
  * time               (time) datetime64[ns] 2012-01-01 ... 2021-02-02T07:00:00
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

## Sample notebooks

Check the demostration [notebooks folder](https://github.com/hmedrano/erddap-python/tree/main/notebooks) for more advanced usage of the library classes.
