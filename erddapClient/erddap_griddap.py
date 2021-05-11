from erddapClient.erddap_dataset import ERDDAP_Dataset
from erddapClient import url_operations
from erddapClient.formatting import griddap_str, erddap_dimensions_str, erddap_dimension_str
from erddapClient.parse_utils import parseTimeRangeAttributes, parse_griddap_resultvariables_slices, is_slice_element_opendap_extended, get_value_from_opendap_extended_slice_element, validate_iso8601, validate_float, validate_int, validate_last_keyword, iso8601STRtoNum, numtodate, dttonum
from erddapClient.erddap_constants import ERDDAP_TIME_UNITS, ERDDAP_DATETIME_FORMAT
from collections import OrderedDict 
from netCDF4 import Dataset, date2num 
import datetime as dt
import numpy as np
import pandas as pd
import xarray as xr 
import requests

class ERDDAP_Griddap(ERDDAP_Dataset):
  """
  Class with the representation and methods for a ERDDAP Griddap Dataset

  """

  DEFAULT_FILETYPE = 'nc'

  def __init__(self, url, datasetid, auth=None, lazyload=True):
    super().__init__(url, datasetid, 'griddap', auth, lazyload=lazyload)
    self.__dimensions = None

  def __str__(self):
    dst_repr_ = super().__str__()
    return dst_repr_ + griddap_str(self)

  def loadMetadata(self, force=False):
    """
    Loads in to memory the metadata atributes and values available in the info
    page of the dataset.

    Arguments:

    `force` : If true, this method will reload the metadata attributes
    even if the information where already downloaded.   
    """    
    if super().loadMetadata(force):
      parseTimeRangeAttributes(self._ERDDAP_Dataset__metadata['dimensions'].items())

  @property
  def dimensions(self):
    self.loadDimensionValues()
    return self.__dimensions


  def loadDimensionValues(self, force=False):
    """
    This methods loads from the ERDDAP Server the dimension values
    for the current griddap dataset.  This values will be used to 
    calculate integer indexes for opendap requests.

    Arguments:

    `force` : If true, this method will reload the dimensions values
    even if the values where already downloaded.
    """

    if self.__dimensions is None or force:
      self.loadMetadata()
      dimensionVariableNames = list(self._ERDDAP_Dataset__metadata['dimensions'].keys())

      _resultVars = self.resultVariables
      dimensionsData = ( self.setResultVariables(dimensionVariableNames)
                             .getDataFrame(header=0, names=dimensionVariableNames)  )
      self.resultVariables = _resultVars
      
      self.__dimensions = ERDDAP_Griddap_dimensions()
      for dimName in dimensionVariableNames:
        
        dimDatadroppedNaNs = dimensionsData[dimName].dropna()
        if dimName == 'time':
          numericDates = np.array([ date2num(dt.datetime.strptime(_dt, ERDDAP_DATETIME_FORMAT), ERDDAP_TIME_UNITS) if (isinstance(_dt,str)) else _dt for _dt in dimDatadroppedNaNs] )
          dimensionSeries = pd.Series( data = np.arange(numericDates.size), index = numericDates)   
        else:
          dimensionSeries = pd.Series( data = dimDatadroppedNaNs.index.values, index = dimDatadroppedNaNs.values) 

        dimMeta = self._ERDDAP_Dataset__metadata['dimensions'][dimName]
        self.__dimensions[dimName] = ERDDAP_Griddap_dimension(dimName, dimensionSeries, metadata=dimMeta)       



  def _convertERDDAPSubset2OpendapRegular(self, resultVariables):
    """
    This method will receive a string from the resultVariables part of the
    ERDDAP griddap request like: 
     ssh[(2001-06-01T09:00:00Z):(2002-06-01T09:00:00Z)][0:(last-20.3)][last-20:1:last]

    And will return the subset part, to the equivalent in integer indexes, 
     ssh[10:20][0:70.7][300:359]
    
    This operation is done by parsing the subset, obtaining the elements of the
    slice that are erddap opendap extended format, the ones between ( ), and converting
    the nearest integer index.

    By parsing the subset, this function returns also error messages on a bad formed
    query.
    
    """
    queryComponents = parse_griddap_resultvariables_slices(resultVariables)

    parsedResultVariables = []
    for qIdx, queryComponent in enumerate(queryComponents):

      if len(queryComponent['sliceComponents']) != 0 and len(self.dimensions) != len(queryComponent['sliceComponents']):        
        raise Exception('The subset request ({}) must match the number of dimensions ({})'.format(resultVariables[qIdx], self.dimensions.ndims))
        
      indexSlice = {'start' : None, 'stop' : None}
      indexSliceStr = ""

      for dimOrder, (dimensionName, sliceComponent) in enumerate(zip(self.dimensions.keys(), queryComponent['sliceComponents'])):
        
        # Check if start of stop components of the slice is opendap extended format, 
        # The way to detect them is if they are between (dimValue) 
        for slicePart in ['start', 'stop']:
          if slicePart in sliceComponent and is_slice_element_opendap_extended(sliceComponent[slicePart]):
            
            sliceComponentValue = get_value_from_opendap_extended_slice_element(sliceComponent[slicePart])
            if validate_iso8601(sliceComponentValue):
              sliceComponentValueNum = iso8601STRtoNum(sliceComponentValue)
              sliceComponentIdx = self.dimensions[dimensionName].closestIdx(sliceComponentValueNum)
              
            elif validate_float(sliceComponentValue):
              sliceComponentValue = float(sliceComponentValue)
              sliceComponentIdx = self.dimensions[dimensionName].closestIdx(sliceComponentValue)

            elif validate_int(sliceComponentValue):
              sliceComponentValue = int(sliceComponentValue)
              sliceComponentIdx = self.dimensions[dimensionName].closestIdx(sliceComponentValue)

            elif validate_last_keyword(sliceComponentValue):
              sliceComponentValue2Eval = sliceComponentValue.replace('last',str(self.dimensions[dimensionName].values.index[-1]))
              sliceComponentIdx = self.dimensions[dimensionName].closestIdx(eval(sliceComponentValue2Eval))
            else:
              raise Exception('Malformed subset : ({}) , couldn\'t parse: ({})'.format(resultVariables[qIdx], sliceComponentValue))
            
          else:
            if slicePart in sliceComponent:
              sliceComponentValue = sliceComponent[slicePart]
              if validate_last_keyword(sliceComponentValue):
                sliceComponentValue2Eval = sliceComponentValue.replace('last',str(self.dimensions[dimensionName].values.iloc[-1]))
                sliceComponentIdx = int(eval(sliceComponentValue2Eval))
              else:
                sliceComponentIdx = int(sliceComponentValue)

          if sliceComponentIdx is None:
            raise Exception('Malformed subset : ({}) , The constraint ({}) is out of dimension range: [{}]'.format(resultVariables[qIdx], sliceComponentValue, self.dimensions[dimensionName].range))

          indexSlice[slicePart] = sliceComponentIdx
        
        #endfor slicePart
        if 'stride' in sliceComponent:
          _indexSliceStr = "[%d:%d:%d]" % (indexSlice['start'], int(sliceComponent['stride']), indexSlice['stop'])
        elif 'stop' in sliceComponent:
          _indexSliceStr = "[%d:%d]" % (indexSlice['start'], indexSlice['stop'])
        elif 'start' in sliceComponent:
          _indexSliceStr = "[%d]" % indexSlice['start']
        else:
          _indexSliceStr =  ""
        
        indexSliceStr += _indexSliceStr

      #endfor dimension
      parsedResultVariables.append(queryComponent['variableName'] + indexSliceStr)
    
    return parsedResultVariables



  def getxArray(self, **kwargs):
    """
    Returns an xarray object subset of the ERDDAP dataset

    Arguments:

    This method will pass all kwargs to the xarray.open_dataset method.
    """
    subsetURL = (self.getDataRequestURL(filetype='opendap', useSafeURL=False))
    if self.erddapauth:
      session = requests.Session()
      session.auth = self.erddapauth
      store = xr.backends.PydapDataStore.open(subsetURL,
                                              session=session)
      _xarray = xr.open_dataset(store, **kwargs)
    else:
      _xarray = xr.open_dataset(subsetURL, **kwargs)

    return _xarray


  def getncDataset(self, **kwargs):
    """
    Returns an netCDF4.Dataset object subset of the ERDDAP dataset

    Arguments:

    This method will pass all kwargs to the netCDF4.Dataset method.
    """
    subsetURL = (self.getDataRequestURL(filetype='opendap', useSafeURL=False))
    if self.erddapauth:
      # TODO Add user, password in URL
      _netcdf4Dataset = Dataset(subsetURL, **kwargs)
    else:
      _netcdf4Dataset = Dataset(subsetURL, **kwargs)
    return _netcdf4Dataset 


  def getDataRequestURL(self, filetype=DEFAULT_FILETYPE, useSafeURL=True, resultVariables=None):
    """
    Returns the fully built ERDDAP data request url with the available components. 

    Arguments:

    `filetype` : The request download format 

    `useSafeURL` : If True the query part of the url will be encoded

    `resultVariables` : If None, the self.resultVariables will be used.

    """
    requestURL = self.getBaseURL(filetype)
    query = ""

    if resultVariables is None:
      resultVariables = self.resultVariables

    if filetype == 'opendap':
      self.loadDimensionValues()
      resultVariables = self._convertERDDAPSubset2OpendapRegular(resultVariables)

    if len(self.resultVariables) > 0:
      query += url_operations.parseQueryItems(resultVariables, useSafeURL, safe='', item_separator=',')

    requestURL = url_operations.joinURLElements(requestURL, query)

    self.lastRequestURL = requestURL
    return self.lastRequestURL
        
  

  @property
  def xarray(self):
    """
    Returns the xarray object representation of the whoe dataset. Ths method creates the
    xarray object by calling the open_dataset method and connecting to the 
    opendap endpoint that ERDDAP provides.
    """
    if not hasattr(self,'__xarray'):      
      if self.erddapauth:
        session = requests.Session()
        session.auth = self.erddapauth
        store = xr.backends.PydapDataStore.open(self.getBaseURL('opendap'),
                                                session=session)
        self.__xarray = xr.open_dataset(store)
      else:
        self.__xarray = xr.open_dataset(self.getBaseURL('opendap'))
    return self.__xarray

  @property
  def ncDataset(self):
    """
    Returns the netCDF4.Dataset object representation of the whole dataset. Ths method
    creates the Dataset object by calling the Dataset constructor connecting 
    to the opendap endpoint that ERDDAP provides.
    """    
    if not hasattr(self,'__netcdf4Dataset'):      
      if self.erddapauth:
        # TODO Add user, password in URL
        self.__netcdf4Dataset = Dataset(self.getBaseURL('opendap'))
      else:
        self.__netcdf4Dataset = Dataset(self.getBaseURL('opendap'))
    return self.__netcdf4Dataset    




class ERDDAP_Griddap_dimensions(OrderedDict):
  """
  Class with the representation and methods for a ERDDAP Griddap 
  dimensions variables
  """    
  def __str__(self):
    return erddap_dimensions_str(self)

  def __getitem__(self, val):
    if isinstance(val, int):
      return self[list(self.keys())[val]]
    else:
      return super().__getitem__(val)
    
  @property 
  def ndims(self):
    return len(self)


class ERDDAP_Griddap_dimension:
  """
  Class with the representation and methods for each ERDDAP Griddap 
  dimension, for its metadata and values

  """  
  def __init__(self, name, values, metadata):
    self.name = name
    self.values = values
    self.metadata = metadata

  def __str__(self):
    return erddap_dimension_str(self)

  def closestIdx(self, value, method='nearest'):
    """
    Returns the integer index that matches the closest 'value' in 
    dimensions values.

    Arguments:

    `value` : The value to search in the dimension values

    `method` : The argument passed to pandas index.get_loc method
    that returns the closest value index.
    """
    if self.isTime:
      rangemin = dttonum(self.metadata['actual_range'][0])
      rangemax = dttonum(self.metadata['actual_range'][1])
    else:
      rangemin = self.metadata['actual_range'][0]
      rangemax = self.metadata['actual_range'][1]
    if value > rangemax or value < rangemin:
      return None
    idx = self.values.index.get_loc(value, method=method)
    return idx

  @property
  def info(self):
    return self.metadata

  @property
  def data(self):
    """
    Returns the dimension values
    """
    return self.values.index

  @property
  def isTime(self):
    return self.name == 'time'

  @property
  def range(self):
    if 'actual_range' in self.metadata:
      return self.metadata['actual_range']
    elif self.name == 'time':
      return (numtodate(self.values.index.min()), numtodate(self.values.index.max()))
    else:
      return (self.values.index.min(), self.values.index.max())



