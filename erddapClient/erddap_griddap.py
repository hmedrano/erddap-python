from erddapClient.erddap_dataset import ERDDAP_Dataset
from erddapClient import url_operations
from erddapClient.formatting import griddap_str
from erddapClient.parse_utils import parseTimeRangeAttributes, parse_griddap_resultvariables_slices, is_slice_element_opendap_extended, get_value_from_opendap_extended_slice_element, validate_iso8601, iso8601todt, validate_float, validate_int, validate_last_keyword
from netCDF4 import Dataset
import numpy as np
import pandas as pd
import xarray as xr 
import requests

class ERDDAP_Griddap(ERDDAP_Dataset):

  DEFAULT_FILETYPE = 'nc'

  def __init__(self, url, datasetid, auth=None, lazyload=True):
    super().__init__(url, datasetid, 'griddap', auth, lazyload=lazyload)
    self.dimensionValues = None

  def __str__(self):
    dst_repr_ = super().__str__()
    return dst_repr_ + griddap_str(self)

  def loadMetadata(self):
    if super().loadMetadata():
      parseTimeRangeAttributes(self.dimensions.items())

  def loadDimensionValues(self, force=False):
    """
    This methods loads from the ERDDAP Server the dimension values
    for the current griddap dataset.  This values will be used to 
    calculate integer indexes for opendap requests.
    """
    if self.dimensionValues is None or force:
      dimensionVariableNames = list(self.dimensions.keys())
      # Search if there is a time dimension
      parseDates = None
      for dimName, dimAtts in self.dimensions.items():
        if 'axis' in dimAtts and dimAtts['axis'] == 'T':
          parseDates = dimName
          break
      
      dimensionsData = ( self.setResultVariables(dimensionVariableNames)
                             .getDataFrame(header=0, 
                                           names=dimensionVariableNames,
                                           parse_dates=[parseDates]) )
      self.dimensionValues = []
      for dimName in self.dimensions.keys():
        droppedNaNs = dimensionsData[dimName].dropna().squeeze() 
        dimensionSeries = pd.Series( data = droppedNaNs.index.values, index = droppedNaNs.values)        
        self.dimensionValues.append(ERDDAP_Griddap_dimension(dimName, dimensionSeries))


  def _convertERDDAPSubset2OpendapRegular(self, resultVariables):
    """
    """
    queryComponents = parse_griddap_resultvariables_slices(resultVariables)
    print(queryComponents)

    parsedResultVariables = []
    for queryComponent in queryComponents:

      if len(queryComponent['sliceComponents']) != 0 and len(self.dimensions) != len(queryComponent['sliceComponents']):
        print("ERROR: subset request must match the same number of dimensions.")
        return 

      indexSlice = {'start' : None, 'stop' : None}
      indexSliceStr = ""

      for dimOrder, (dimensionName, sliceComponent) in enumerate(zip(self.dimensions.keys(), queryComponent['sliceComponents'])):
        print (dimensionName, sliceComponent)
        
        # Check if start of stop components of the slice is opendap extended format, 
        # The way to detect them is if they are between (dimValue) 
        for slicePart in ['start', 'stop']:
          if slicePart in sliceComponent and is_slice_element_opendap_extended(sliceComponent[slicePart]):
            # print(sliceComponent[slicePart], " is opendapExtended")
            sliceComponentValue = get_value_from_opendap_extended_slice_element(sliceComponent[slicePart])
            if validate_iso8601(sliceComponentValue):
              # Convert sliceComponentValue to datetime, but how!
              sliceComponentValue = iso8601todt(sliceComponentValue)
              sliceComponentIdx = self.dimensionValues[dimOrder].closestIdx(sliceComponentValue)
              
            elif validate_float(sliceComponentValue):
              sliceComponentValue = float(sliceComponentValue)
              sliceComponentIdx = self.dimensionValues[dimOrder].closestIdx(sliceComponentValue)

            elif validate_int(sliceComponentValue):
              sliceComponentValue = int(sliceComponentValue)
              sliceComponentIdx = self.dimensionValues[dimOrder].closestIdx(sliceComponentValue)

            elif validate_last_keyword(sliceComponentValue):
              sliceComponentValue2Eval = sliceComponentValue.replace('last',str(self.dimensionValues[dimOrder].values.index[-1]))
              # print("To eval ", eval(sliceComponentValue2Eval))
              sliceComponentIdx = self.dimensionValues[dimOrder].closestIdx(eval(sliceComponentValue2Eval))
            else:
              print ("Dont know how to parse : " , sliceComponentValue )
            
            # print (sliceComponentValue, " = ", sliceComponentIdx)

          else:
            if slicePart in sliceComponent:
              sliceComponentValue = sliceComponent[slicePart]
              if validate_last_keyword(sliceComponentValue):
                sliceComponentValue2Eval = sliceComponentValue.replace('last',str(self.dimensionValues[dimOrder].values.iloc[-1]))
                sliceComponentIdx = int(eval(sliceComponentValue2Eval))
              else:  
                sliceComponentIdx = int(sliceComponentValue)
              #print(sliceComponentValue, " is opendap regular int index")
              #print (" = ", sliceComponentIdx)

          indexSlice[slicePart] = sliceComponentIdx
        
        if 'stride' in sliceComponent:
          _indexSliceStr = "[%d:%d:%d]" % (indexSlice['start'], int(sliceComponent['stride']), indexSlice['stop'])
        elif 'stop' in sliceComponent:
          _indexSliceStr = "[%d:%d]" % (indexSlice['start'], indexSlice['stop'])
        elif 'start' in sliceComponent:
          _indexSliceStr = "[%d]" % indexSlice['start']
        else:
          _indexSliceStr =  ""
        
        indexSliceStr += _indexSliceStr
      
      parsedResultVariables.append(queryComponent['variableName'] + indexSliceStr)
    
    return parsedResultVariables


  def getxArray(self):
    """
    """
    subsetURL = (self.getDataRequestURL(filetype='opendap', useSafeURL=False))
    if self.erddapauth:
      session = requests.Session()
      session.auth = self.erddapauth
      store = xr.backends.PydapDataStore.open(subsetURL,
                                              session=session)
      _xarray = xr.open_dataset(store)
    else:
      _xarray = xr.open_dataset(subsetURL)

    return _xarray


  def getncDataset(self):
    """
    """
    subsetURL = (self.getDataRequestURL(filetype='opendap', useSafeURL=False))
    if self.erddapauth:
      # TODO Add user, password in URL
      _netcdf4Dataset = Dataset(subsetURL)
    else:
      _netcdf4Dataset = Dataset(subsetURL)
    return _netcdf4Dataset 


  def getDataRequestURL(self, filetype=DEFAULT_FILETYPE, useSafeURL=True, resultVariables=None):
    """
    """
    requestURL = self.getBaseURL(filetype)
    query = ""

    if resultVariables is None:
      resultVariables = self.resultVariables

    if filetype == 'opendap':
      resultVariables = self._convertERDDAPSubset2OpendapRegular(resultVariables)

    if len(self.resultVariables) > 0:
      query += url_operations.parseQueryItems(resultVariables, useSafeURL, safe='', item_separator=',')

    requestURL = url_operations.joinURLElements(requestURL, query)

    self.lastRequestURL = requestURL
    return self.lastRequestURL
        
  

    

  @property
  def xarray(self):
    """
    Returns the xarray object representation of the dataset. Ths method creates the
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
    Returns the netCDF4.Dataset object representation of the dataset. Ths method
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


class ERDDAP_Griddap_dimension:
  
  def __init__(self, name, values):
    self.name = name
    self.values = values

  def closestIdx(self, value):
    # idx = (np.abs(self.values - value)).argmin()
    if value > self.values.index.max() or value < self.values.index.min():
      return None
    idx = self.values.index.get_loc(value, method='nearest')
    return idx
  
  #def closestDateIdx(self, datet, method='nearest'):
  #  self.values.get_loc(datet, method=method)


