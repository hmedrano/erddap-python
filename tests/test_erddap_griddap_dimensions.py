import pytest
from erddapClient import ERDDAP_Griddap
import datetime as dt

@pytest.mark.vcr()
def test_griddap_dimensions():
    url = 'https://coastwatch.pfeg.noaa.gov/erddap'
    datasetid = 'hycom_gom310D'
    remote = ERDDAP_Griddap(url, datasetid)
    dstDims = remote.dimensions

    assert 'time' in dstDims and 'depth' in dstDims and\
           'latitude' in dstDims and 'longitude' in dstDims

    assert dstDims['time'].size == 1977

    assert dstDims['time'].isTime

    # Depth values to dataset loaded (in cassetes)
    # Float64Index([   0.0,    5.0,   10.0,   15.0,   20.0,   25.0,   30.0,   40.0,
    #                 50.0,   60.0,   70.0,   80.0,   90.0,  100.0,  125.0,  150.0,
    #                200.0,  250.0,  300.0,  400.0,  500.0,  600.0,  700.0,  800.0,
    #                900.0, 1000.0, 1100.0, 1200.0, 1300.0, 1400.0, 1500.0, 1750.0,
    #               2000.0, 2500.0, 3000.0, 3500.0, 4000.0, 4500.0, 5000.0, 5500.0]
    #              )
    assert dstDims['depth'][dstDims['depth'].closestIdx(0)] == dstDims['depth'][0]
    assert dstDims['depth'][dstDims['depth'].closestIdx(5500)] == dstDims['depth'][39]
    assert dstDims['depth'].closestIdx(5501) == None  # If solicited value its outside of valid range returns None

    # Test dimensions indexing by value
    dimIndexing = dstDims.subset( "2014-06-15", slice(0), slice(18.10,31.96), slice(-98, -76.41) )
    assert dstDims['time'].timeData[dimIndexing['time']] == dt.datetime(2014, 6, 15) 

    # Test dimensions indexing by positional integer index
    dimNumIndexing = dstDims.subsetI(time=slice(1900), depth=0, latitude=slice(0,385), longitude=slice(0,541))
    assert dstDims['time'].timeData[dimNumIndexing['time']] == dt.datetime(2014, 6, 15) 

    # Test dimensions indexing by positional negative integer index
    dimNumIndexing = dstDims.subsetI(time=1900, depth=slice(-2, 40), latitude=slice(0,385), longitude=slice(0,541))
    assert dstDims['depth'][dimNumIndexing['depth']][0] == 5000.0 and \
           dstDims['depth'][dimNumIndexing['depth']][1] == 5500.0

    # Test raise Exception if index its out of bounds
    with pytest.raises(Exception):
        dimNumIndexing = dstDims.subsetI(time=slice(1900), depth=45, latitude=slice(0,385), longitude=slice(0,541))
