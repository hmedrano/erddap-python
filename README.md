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

```
from erddapClient import ERDDAP_Tabledap

url = 'https://coastwatch.pfeg.noaa.gov/erddap'
datasetid = 'cwwcNDBCMet'
remote = ERDDAP_Tabledap(url, datasetid)

response = (
    remote.setResultVariables(['station','time','atmp'])
          .addConstraint('time>=2020-12-29T00:00:00Z')
          .addConstraint('time<=2020-12-31T00:00:00Z')
          .orderByClosest(['station','time/1day'])
          .getRequestData('csvp')
)

print(response)


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

