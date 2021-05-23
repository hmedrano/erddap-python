from erddapClient.erddap_dataset import ERDDAP_Dataset
from erddapClient.erddap_griddap_dimensions import ERDDAP_Griddap_dimensions, ERDDAP_Griddap_dimension
from erddapClient import url_operations
from erddapClient.formatting import griddap_str
from erddapClient.parse_utils import parseTimeRangeAttributes, parse_griddap_resultvariables_slices, is_slice_element_opendap_extended, get_value_from_opendap_extended_slice_element, validate_iso8601, validate_float, validate_int, validate_last_keyword, iso8601STRtoNum, extractVariableName
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
    self.__positional_indexes = None
    """
    This property stores the last dimensions slices that builds the subset query. Its used to build opendap
    compatible queryes, and to get the dimensions values of the subset.
    """

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


  def clearQuery(self):
    super().clearQuery()
    self.__positional_indexes = None


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


  def getxArray(self, **kwargs_od):
    """
    Returns an xarray object subset of the ERDDAP dataset current selection query

    Arguments:

    This method will pass all kwargs to the xarray.open_dataset method.
    """
    open_dataset_kwparams = { 'mask_and_scale' : True } # Accept _FillValue, scale_value and add_offset attribute functionality
    open_dataset_kwparams.update(kwargs_od)
    subsetURL = self.getDataRequestURL(filetype='opendap', useSafeURL=False)
    if self.erddapauth:
      session = requests.Session()
      session.auth = self.erddapauth
      store = xr.backends.PydapDataStore.open(subsetURL,
                                              session=session)
      _xarray = xr.open_dataset(store, **open_dataset_kwparams)
    else:
      _xarray = xr.open_dataset(subsetURL, **open_dataset_kwparams)
    
    # Add extra information to the xarray object, the dimension information.
    # Add the subset of the dimensions values to the xarray object
    _subset_coords = { dimName : dObj.data[self.__positional_indexes[dimName]] for dimName, dObj in self.dimensions.items() }
    if self.dimensions.timeDimension:
      _subset_coords[self.dimensions.timeDimension.name] = self.dimensions.timeDimension.timeData[ self.__positional_indexes[self.dimensions.timeDimension.name] ]
    _xarray = _xarray.assign_coords(_subset_coords)
    # Add attributes to the coordinates
    for dimName, dObj in self.dimensions.items():
      _xarray.coords[dimName].attrs = dObj.metadata

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
      if self.__positional_indexes:
        resultVariables = self._resultVariablesWithValidDapIndexing()
      else:
        # resultVariables = self._convertERDDAPSubset2OpendapRegular(resultVariables)
        #
        resultVariables = self._parseResultVariablesExtendedDapQueryToValidDap(resultVariables)
    else:
      if self.__positional_indexes:
        resultVariables = self._resultVariablesWithValidDapIndexing()

    if len(self.resultVariables) > 0:
      query += url_operations.parseQueryItems(resultVariables, useSafeURL, safe='', item_separator=',')

    requestURL = url_operations.joinURLElements(requestURL, query)

    self.lastRequestURL = requestURL
    return self.lastRequestURL


  def setSubset(self, *pdims, **kwdims):
    """
    Sets a query subset for griddap request, by using dimension names

    Usage example:

    ```
    dsub = ( remote.setResultVariables(['temperature','salinity'])
                   .setSubset( time=slice(dt.datetime(2014,6,15), dt.datetime(2014,7,15)),
                               depth=0,
                               latitude=slice(18.10, 31.96), 
                               longitude=slice(-98, -76.41))
                   .getxArray() )
    ```
    """
    self.__positional_indexes = self.dimensions.subset(*pdims, **kwdims)
    return self


  def setSubsetI(self, *pdims, **kwdims):
    """
    Sets a query subset for griddap request, by using its positional
    integer index.

    Usage example:

    ```
    dsub = ( remote.setResultVariables(['temperature','salinity'])
                   .setSubsetI( time=slice(-10,-1),
                                depth=0,
                                latitude=slice(10, 150), 
                                longitude=slice(20, 100) )
                   .getxArray() )
    ```
    """

    self.__positional_indexes = self.dimensions.subsetI(*pdims, **kwdims)
    return self

  def _parseResultVariablesExtendedDapQueryToValidDap(self, resultVariables):

    """
    This method will receive a string from the resultVariables part of the
    ERDDAP griddap request like: 
     ssh[(2001-06-01T09:00:00Z):(2002-06-01T09:00:00Z)][0:(last-20.3)][last-20:1:last]

    And will return the each result varibel with valid opendap integer indexing query,
     ssh[10:20][0:70.7][300:359]
    
    This operation is done by parsing the subset, obtaining the elements of the
    slice that are erddap opendap extended format, the ones between ( ), and converting
    the nearest integer index.

    By parsing the subset, this function returns also error messages on a bad formed
    query.
    
    """
    queryComponents = parse_griddap_resultvariables_slices(resultVariables)

    parsedResultVariables = []
    _parsed_positional_indexes = OrderedDict({ dimname : None for dimname, dobj in self.dimensions.items() })
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
            # In griddap querys, the slice start and stop, can be between ( ), this notation is a extended
            # opendap format that uses the dimensions values or special keywords to slice the dimensions.
            # More on this: https://coastwatch.pfeg.noaa.gov/erddap/griddap/documentation.html#query

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
            # In the slice is not between ( ) , then this means the slice component its using the numeric indexes
            # to create the slice.  The only special keyword allowed here, its 'last', which means the last numeric
            # index in the current dimension.
            # More on this: https://coastwatch.pfeg.noaa.gov/erddap/griddap/documentation.html#last
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

        # Build the valid slice object with equivalent numeric indexes in self.__positional_indexes
        _sobj = None # slice object, to include to self.__positional_indexes
        if 'stride' in sliceComponent:
          _sobj = slice( indexSlice['start'], indexSlice['stop'] + 1, int(sliceComponent['stride']) )
        elif 'stop' in sliceComponent:
          _sobj = slice(indexSlice['start'], indexSlice['stop'] + 1)
        elif 'start' in sliceComponent:
          _sobj = slice(indexSlice['start'], indexSlice['start'] + 1)

        _parsed_positional_indexes[dimensionName] = _sobj
        
      #endfor dimension
      self.__positional_indexes = _parsed_positional_indexes
      _validDapIndexing = self._convertPositionalIndexes2DapQuery()

      # Join the variable name with the openDap indexing
      parsedResultVariables.append(queryComponent['variableName'] + _validDapIndexing)
    
    #end for queryComponent
      
    return parsedResultVariables


  def _convertPositionalIndexes2DapQuery(self):
    """
    This function will convert the positional_indexes dictionary of slices, to a string
    query type, compatible with the opendap protocol.

    The property __positional_indexes will contain the slices for each dimension in a dict.

    OrderedDict([('time', slice(200, 201, None)),
             ('altitude', slice(0, 1, None)),
             ('latitude', slice(337, 465, None)),
             ('longitude', slice(1018, 1146, None))])

    This method converts and returns the above to the opendap compatible query string.

    [200:200][0:0][337:464][1018:1145]

    Returns:
      - Compatible opendap query string

    """

    def parseNegativeIndex(nidx, dref):
      return nidx if nidx >= 0 else dref.size + nidx

    if self.__positional_indexes is None or all(dimSlice is None for dimName, dimSlice in self.__positional_indexes.items()):
      return ""
    
    validDapIndexing = ""
    for dimName, dimSlice in self.__positional_indexes.items():
      if dimSlice is None:
        raise Exception("Not a valid slice available for dimension: {} ".format(dimName))
      if not dimSlice.step is None:
        _start = parseNegativeIndex(dimSlice.start, self.dimensions[dimName])
        _stop = parseNegativeIndex(dimSlice.stop, self.dimensions[dimName])
        _sc = "[{}:{}:{}]".format(_start, dimSlice.step, _stop-1)
      elif not dimSlice.start is None:
        _start = parseNegativeIndex(dimSlice.start, self.dimensions[dimName])
        _stop = parseNegativeIndex(dimSlice.stop, self.dimensions[dimName])
        _sc = "[{}:{}]".format(_start, _stop-1)
      elif not dimSlice.stop is None:
        _stop = parseNegativeIndex(dimSlice.stop, self.dimensions[dimName])
        _sc = "[{}]".format(_stop)
      else:
        raise Exception("No valid slice available for dimension: {} ".format(dimName))
      validDapIndexing+=_sc
    
    return validDapIndexing


  def _resultVariablesWithValidDapIndexing(self):
    """
    Returns the opendap query of the variables listed in the resultVariables 
    property, with valid opendap indexing. 
    The indexing its built from the current positional_indexes.
    """

    _validDapIndexing = self._convertPositionalIndexes2DapQuery()
    validDapQuery = []
    if self.resultVariables is None:
      for varName in self.variables.keys():
        validDapQuery.append(varName + _validDapIndexing)
    else:
      for varName in self.resultVariables:
        _justvarname = extractVariableName(varName)
        validDapQuery.append(_justvarname + _validDapIndexing)

    return validDapQuery


  @property 
  def positional_indexes(self):
    return self.__positional_indexes

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


