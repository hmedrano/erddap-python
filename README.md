# ERDDAP python library 

[![Build Status](https://travis-ci.com/hmedrano/erddap-python.svg?branch=main)](https://travis-ci.com/hmedrano/erddap-python)

## About

[ERDDAP](https://coastwatch.pfeg.noaa.gov/erddap/information.html) is a data server that gives you a simple, consistent way to download subsets of gridded and tabular scientific datasets in common file formats and make graphs and maps. 

erddap-python is a python client for the ERDDAP Restful API, it can obtain server status metrics, provides search methods, gives tabledap and griddap class objects for metadata and data access.

This library was initially built for [CICESE](https://cicese.edu.mx), [CIGOM](https://cigom.org), [OORCO](https://oorco.org), and [CEMIEOceano](https://cemieoceano.mx/) projects for the automation of reports, interactive custom visualizations and data analysis.  Most of the functionality was inspired on the work of [erddapy](https://github.com/ioos/erddapy) library, but designed more for a more flexible backend service construction in mind.


Full API reference can be found [here](https://hmedrano.github.io/erddap-python/).

## Projects using erddap-python

 - [ERDDAP server's status metrics dashboard using Streamlit](https://share.streamlit.io/hmedrano/erddap-status-dashboard/main/dashboard_streamlit_app.py)
 - [Module for Ocean Observatory Data Analysis library](https://github.com/rbardaji/mooda)

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

Connect to a ERDDAP Server, and get some basic search.

```python
>>> from erddapClient import ERDDAP_Server
>>> 
>>> remoteServer = ERDDAP_Server('https://coastwatch.pfeg.noaa.gov/erddap')
>>> remoteServer
<erddapClient.ERDDAP_Server>
Server version:  ERDDAP_version=2.11
```

[search](https://hmedrano.github.io/erddap-python/#ERDDAP_Server.search) and [advancedSerch](https://hmedrano.github.io/erddap-python/#ERDDAP_Server.advancedSearch) methods are available, it builds the search request URL and also can 
make the request to the ERDDAP restful services to obtain results. 

```python
>>> searchRequest = remoteServer.search(searchFor="gliders")
>>> searchRequest
<erddapClient.ERDDAP_SearchResults>
Results:  1
[
  0 - <erddapClient.ERDDAP_Tabledap> scrippsGliders , "Gliders, Scripps Institution of Oceanography, 2014-present"
]
```

The methods returns an object with a list of the ERDDAP Tabledap or Griddap objects that matched the search filters.

### Connect to Tabledap datasets 


Using the [ERDDAP_Tabledap](https://hmedrano.github.io/erddap-python/#ERDDAP_Tabledap) class to build ERDDAP data request URL's

```python

>>> from erddapClient import ERDDAP_Tabledap
>>> 
>>> remote = ERDDAP_Tabledap('https://coastwatch.pfeg.noaa.gov/erddap', 'cwwcNDBCMet')
>>> 
>>> remote.setResultVariables(['station','time','atmp'])
>>> print (remote.getURL('htmlTable'))

'https://coastwatch.pfeg.noaa.gov/erddap/tabledap/cwwcNDBCMet.htmlTable?station%2Ctime%2Catmp'

```

The tabledap object as internally a stack for resultVariables, constrainst and server side operations. You 
can keep adding them and get the different urls.

```python
>>> import datetime as dt 
>>> 
>>> remote.addConstraint('time>=2020-12-29T00:00:00Z') \
..:       .addConstraint({ 'time<=' : dt.datetime(2020,12,31) })
>>> remote.getURL()

'https://coastwatch.pfeg.noaa.gov/erddap/tabledap/cwwcNDBCMet.csvp?station%2Ctime%2Catmp&time%3E=2020-12-29T00%3A00%3A00Z&time%3C=2020-12-31T00%3A00%3A00Z'

>>>
>>> remote.orderByClosest(['station','time/1day'])
>>> remote.getURL()

'https://coastwatch.pfeg.noaa.gov/erddap/tabledap/cwwcNDBCMet.csvp?station%2Ctime%2Catmp&time%3E=2020-12-29T00%3A00%3A00Z&time%3C=2020-12-31T00%3A00%3A00Z&orderByClosest(%22station%2Ctime/1day%22)'

>>> 
```

The class has methods to clear the result variables, the constraints, and the server side operations that are added in the stack: `clearConstraints()`, `clearResultVariable()`, `clearServerSideFunctions` or `clearQuery()`

#### Tabledap data subset request

An user can build the query chaining the result variables, constraints and server side operations, and make the data 
request in all the available formats that ERDDAP provides.

```python
>>>
>>> remote.clearQuery()
>>>
>>> responseCSV = (
..:     remote.setResultVariables(['station','time','atmp'])
..:           .addConstraint('time>=2020-12-29T00:00:00Z')
..:           .addConstraint('time<=2020-12-31T00:00:00Z')
..:           .orderByClosest(['station','time/1day'])
..:           .getData('csvp')
..: )
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
..:     remote.setResultVariables(['station','time','atmp'])
..:           .addConstraint('time>=2020-12-29T00:00:00Z')
..:           .addConstraint('time<=2020-12-31T00:00:00Z')
..:           .orderByClosest(['station','time/1day'])
..:           .getDataFrame()
..: )
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

All the url building functions, and data request functionality is available in the [ERDDAP_Griddap](https://hmedrano.github.io/erddap-python/#ERDDAP_Griddap) class. 

With this class you can download data subsets in all the available ERDDAP data formats, plus the posibility to request a fully described xarray.DataArrays objects.

This class can parse the griddap query, and detect if the query is malformed before requesting data from the 
ERDDAP server.

Usage sample:

```python
>>> from erddapClient import ERDDAP_Griddap
>>> 
>>> remote = ERDDAP_Griddap('https://coastwatch.pfeg.noaa.gov/erddap', 'hycom_gom310D')
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
```

You can query the dimensions information.

```python
>>> print(remote.dimensions)

<erddapClient.ERDDAP_Griddap_dimensions>
Dimensions:
 - time (nValues=1977) 1238630400 .. 1409356800
 - depth (nValues=40) 0.0 .. 5500.0
 - latitude (nValues=385) 18.091648 .. 31.960648
 - longitude (nValues=541) -98.0 .. -76.400024

>>> print(remote.dimensions['time'])

<erddapClient.ERDDAP_Griddap_dimension>
Dimension: time
  _nValues : 1977
  _evenlySpaced : True
  _averageSpacing : 1 day
  _dataType : double
  _CoordinateAxisType : Time
  actual_range : (cftime.DatetimeGregorian(2009, 4, 2, 0, 0, 0, 0), cftime.DatetimeGregorian(2014, 8, 30, 0, 0, 0, 0))
  axis : T
  calendar : standard
  ioos_category : Time
  long_name : Time
  standard_name : time
  time_origin : 01-JAN-1970 00:00:00
  units : seconds since 1970-01-01T00:00:00Z
```

#### Griddap data request in a xarray.DataArray

Request a data subset and store it in a fully described xarray.DataArray object.

```python

>>> xSubset = ( remote.setResultVariables('temperature')
..:                   .setSubset(time="2012-01-13",
..:                              depth=slice(0,2000),
..:                              latitude=slice(18.09165, 31.96065),
..:                              longitude=slice(-98.0,-76.40002))
..:                   .getxArray() )

>>> xSubset

<xarray.Dataset>
Dimensions:      (depth: 33, latitude: 385, longitude: 541, time: 1)
Coordinates:
  * time         (time) object 2012-01-13 00:00:00
  * depth        (depth) float64 0.0 5.0 10.0 15.0 ... 1.5e+03 1.75e+03 2e+03
  * latitude     (latitude) float64 18.09 18.13 18.17 ... 31.89 31.93 31.96
  * longitude    (longitude) float64 -98.0 -97.96 -97.92 ... -76.48 -76.44 -76.4
Data variables:
    temperature  (time, depth, latitude, longitude) float32 ...
Attributes: (12/32)
    cdm_data_type:              Grid
    Conventions:                COARDS, CF-1.0, ACDD-1.3
    creator_email:              hycomdata@coaps.fsu.edu
    creator_name:               Naval Research Laboratory
    creator_type:               institution
    creator_url:                https://www.hycom.org
    ...                         ...
    standard_name_vocabulary:   CF Standard Name Table v70
    summary:                    NRL HYCOM 1/25 deg model output, Gulf of Mexi...
    time_coverage_end:          2014-08-30T00:00:00Z
    time_coverage_start:        2009-04-02T00:00:00Z
    title:                      NRL HYCOM 1/25 deg model output, Gulf of Mexi...
    Westernmost_Easting:        -98.0

```

The above data request can also be done using the ERDDAP opendap extended query format, by example :

```python 
>>> xSubset = ( remote.setResultVariables('temperature[(2012-01-13)][(0):(2000)][(18.09165):(31.96065)][(-98.0):(-76.40002)]')
..:                   .getxArray()            
```

#### Make request for subsets in different formats.

```python
>>> # Request a location subset in a pandas dataframe
>>>
>>> remote.clearQuery()
>>> dfSubset = ( remote.setResultVariables(['temperature','salinity'])
..:                    .setSubset(time=slice("2009-04-02","2014-8-30"),
..:                               depth=0,
..:                               latitude=22.5,
..:                               longitude=-95.5)
..:                    .getDataFrame(header=0,
..:                                  names=['time','depth','latitude','longitude', 'temperature', 'salinity'],
..:                                  parse_dates=['time'],
..:                                  index_col='time') )

>>> dfSubset

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

>>> 

```

----

## Sample notebooks

Check the demostration [notebooks folder](https://github.com/hmedrano/erddap-python/tree/main/notebooks) for more advanced usage of the library classes.
