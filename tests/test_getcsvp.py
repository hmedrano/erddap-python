from pyerddap import ERDDAP_Tabledap
import pprint

def test_getdata_csvp():
    url = 'https://coastwatch.pfeg.noaa.gov/erddap'
    datasetid = 'cwwcNDBCMet'
    remote = ERDDAP_Tabledap(url, datasetid)

    response = (
        remote.setResultVariables(['station','time','atmp'])
              .addConstraint('time>=2020-12-29T00:00:00Z')
              .addConstraint('time<=2020-12-31T00:00:00Z')
              .orderByClosest(['station','time/1day'])
              .getDataRequest('csvp')
    )
    
    print(response)

def test_getdata_nc():
    url = 'https://coastwatch.pfeg.noaa.gov/erddap'
    datasetid = 'cwwcNDBCMet'
    remote = ERDDAP_Tabledap(url, datasetid)

    response = (
        remote.setResultVariables(['station','time','atmp'])
              .addConstraint('time>=2020-12-29T00:00:00Z')
              .addConstraint('time<=2020-12-31T00:00:00Z')
              .orderByClosest(['station','time/1day'])
              .getDataRequest('nc')
    )
    
    filehandler=open("dataSubset.nc","wb")
    filehandler.write(response)
    filehandler.close()

def test_getdata_pandas_dataframe():
    url = 'https://coastwatch.pfeg.noaa.gov/erddap'
    datasetid = 'cwwcNDBCMet'
    remote = ERDDAP_Tabledap(url, datasetid)

    responseDF = (
        remote.setResultVariables(['station','time','atmp'])
              .addConstraint('time>=2020-12-29T00:00:00Z')
              .addConstraint('time<=2020-12-31T00:00:00Z')
              .orderByClosest(['station','time/1day'])
              .getDataFrame()
    )
    
    print (responseDF)

def test_getdata_pandas_dataframe_params():
    url = 'https://coastwatch.pfeg.noaa.gov/erddap'
    datasetid = 'cwwcNDBCMet'
    remote = ERDDAP_Tabledap(url, datasetid)

    responseDF = (
        remote.setResultVariables(['station','time','atmp'])
              .addConstraint('time>=2020-12-29T00:00:00Z')
              .addConstraint('time<=2020-12-31T00:00:00Z')
              .orderByClosest(['station','time/1day'])
              .getDataFrame(header=0, names=['estacion', 'tiempo', 'temperatura aire'], parse_dates=['tiempo'])
    )
    
    print (responseDF)

def test_variables_metadata():
    url = 'https://coastwatch.pfeg.noaa.gov/erddap'
    datasetid = 'cwwcNDBCMet'
    remote = ERDDAP_Tabledap(url, datasetid, lazyload=False)

    pprint.pprint(remote.variables)

def test_dataset_repr():
    url = 'https://coastwatch.pfeg.noaa.gov/erddap'
    datasetid = 'cwwcNDBCMet'
    remote = ERDDAP_Tabledap(url, datasetid)

    print(remote)

test_dataset_repr()