import os
from erddapClient import url_operations
from erddapClient.remote_requests import urlread
from erddapClient.parse_utils import parseDictMetadata, parseConstraintValue
from erddapClient.formatting import dataset_str, simple_dataset_repr
import datetime as dt
import pandas as pd
from io import StringIO


class ERDDAP_Dataset:
  """
  Class to represent the shared attributes and methods of a ERDDAP Dataset
  either a griddap or tabledap.
  
  """

  DEFAULT_FILETYPE = 'csvp'
  BINARY_FILETYPES = [ 'dods', 'mat', 'nc', 'ncCF', 'ncCFMA', 'wav', 
                       'smallPdf', 'pdf', 'largePdf', 
                       'smallPng', 'png', 'largePng', 'transparentPng']

  def __init__(self, erddapurl, datasetid, protocol='tabledap', auth=None, lazyload=True):
    self.erddapurl = erddapurl
    self.datasetid = datasetid
    self.protocol = protocol    
    self.erddapauth = auth

    self.__metadata = None

    self.resultVariables = []
    self.constraints = []
    self.serverSideFunctions = []

    if not lazyload:
      self.loadMetadata()


  def __str__(self):
    return dataset_str(self)

  def __simple_repr__(self):
    return simple_dataset_repr(self)
  

  def setResultVariables(self, variables):
    """
    This function sets the optional comma-separated list of variables 
    called "resultsVariables" as part of the query for data request.
    (for example: longitude,latitude,time,station,wmo_platform_code,T_25).
    For each variable in resultsVariables, there will be a column in the 
    results table, in the same order. If you don't specify any results 
    variables, the results table will include columns for all of the 
    variables in the dataset.

    Arguments

    `variables` : The list of variables, this can be a string with the 
                  comma separated variables, or a list.
    
    Returns the current object allowing chaining functions.

    """
    if type(variables) is list:
      self.resultVariables = variables 
    elif type(variables) is str:
      self.resultVariables = variables.split(',')
    else:
      raise Exception("variables argument must be list, or comma separated list of variables")
    
    return self


  def addResultVariable(self, variable):
    """
    Adds a variable to the data request query element "resultsVariables"

    Arguments

    `variable` : A string with the variable name add.
    """
    self.resultVariables.append(variable)
    return self


  def setConstraints(self, constraintListOrDict):
    """
    This functions sets the constraints for the data request query.

    More on ERDDAP constraints: https://coastwatch.pfeg.noaa.gov/erddap/tabledap/documentation.html#query

    """
    self.clearConstraints()
    self.addConstraints(constraintListOrDict)


  def addConstraints(self, constraintListOrDict):
    if isinstance(constraintListOrDict,dict):
      for k,v in constraintListOrDict.items():
        self.addConstraint({k:v})
    elif isinstance(constraintListOrDict,list):
      for constraint in constraintListOrDict:
        self.addConstraint(constraint)
    else:
      raise Exception("Constraints argument must be either dictionary or list")
    return self


  def addConstraint(self, constraint):
    """
    This adds a constraint to the data request query.

    Arguments

    `constraint` : This can be a string with the constraint, or a dictionary
                   element, being the key the first part of the constraint, and 
                   the dict value the constraint value.

    Example:
    ```
    >>> dataset.addConstraint('time>=2020-12-29T00:00:00Z')
    >>> dataset.addConstraint({ 'time>=' : dt.datetime(2020,12,29) })
    ```

    More on ERDDAP constraints: https://coastwatch.pfeg.noaa.gov/erddap/tabledap/documentation.html#query
    """    
    if isinstance(constraint,dict):
      self._addConstraintDict(constraint)
    elif isinstance(constraint,str):
      self._addConstraintStr(constraint)
    else:
      raise Exception("constraint argument must be either string or a dictionary")
    return self


  def _addConstraintStr(self, constraint):
    self.constraints.append(constraint)


  def _addConstraintDict(self, constraintDict):
    constraintKey = next(iter(constraintDict))
    self._addConstraintStr(
      "{key_plus_conditional}{value}".format(
            key_plus_conditional=constraintKey, 
            value=parseConstraintValue(constraintDict[constraintKey])
          )
    )


  def getDataRequestURL(self, filetype=DEFAULT_FILETYPE, useSafeURL=True):
    requestURL = self.getBaseURL(filetype)
    query = ""

    if len(self.resultVariables) > 0:
      query += url_operations.parseQueryItems(self.resultVariables, useSafeURL, safe='', item_separator=',')

    if len(self.constraints) > 0:
      query += '&' + url_operations.parseQueryItems(self.constraints, useSafeURL, safe='=!()&')

    if len(self.serverSideFunctions) > 0:
      query += '&' + url_operations.parseQueryItems(self.serverSideFunctions, useSafeURL, safe='=!()&/')

    requestURL = url_operations.joinURLElements(requestURL, query)

    self.lastRequestURL = requestURL
    return self.lastRequestURL
  
  
  def getURL(self, filetype=DEFAULT_FILETYPE, useSafeURL=True):
    """
    Buils and returns a strint with the data request query, with the available
    resultsVariables, constraints and operations provided.
    """
    return self.getDataRequestURL(filetype, useSafeURL)


  def getBaseURL(self, filetype=DEFAULT_FILETYPE):
    if filetype.lower() == 'opendap':
      return url_operations.url_join(self.erddapurl, self.protocol, self.datasetid )
    else:
      return url_operations.url_join(self.erddapurl, self.protocol, self.datasetid + "." + filetype )
    

  def getAttribute(self, attribute, variableName='NC_GLOBAL'):
    """
    Returns the value for a attribute name in the dataset. If the metadata of the
    dataset is not already in memory, this functions will load it, calling the
    function `erddapClient.ERDDAP_Dataset.loadMetadata`

    """
    self.loadMetadata()
    if variableName == 'NC_GLOBAL':
      if attribute in self.__metadata['global'].keys():
        return self.__metadata['global'][attribute]
    else:
      for vd in [ self.__metadata['dimensions'], self.__metadata['variables'] ]:
        if variableName in vd.keys():
          if attribute in vd[variableName].keys():
            return vd[variableName][attribute]


  def loadMetadata(self):
    """
    Loads in to memory the metadata atributes and values available in the info
    page of the dataset.
    """
    if self.__metadata is None:
      rawRequest = urlread(self.getMetadataURL(), auth=self.erddapauth)
      rawRequestJson = rawRequest.json()
      self.__metadata = parseDictMetadata(rawRequestJson)
      return True
      
  @property
  def variables(self):
    return self.__metadata['variables']

  @property
  def dimensions(self):
    return self.__metadata['dimensions']

  @property
  def info(self):
    return self.__metadata['global']


  def getMetadataURL(self, filetype='json'):
    """
    Returns a string with the url to request the metadata for the dataset.

    Arguments

    `filetype` : The filetype for the metadata request, defaults to 'json'

    """ 
    return url_operations.url_join(self.erddapurl, "info", self.datasetid , "index." + filetype )


  def clearConstraints(self):
    """
    Clears from the constrains stack all the constraints provided by the 
    `erddapClient.ERDDAP_Dataset.setConstraints`, `erddapClient.ERDDAP_Dataset.addConstraint`
    methods. 

    """
    self.constraints = []
  

  def clearServerSideFunctions(self):
    """
    Clears from the server side functions stack all the functions provided by the 
    methods available, like `erddapClient.ERDDAP_Tabledap.orderBy`, 
    `erddapClient.ERDDAP_Tabledap.orderByClosest`, etc.
    
    """    
    self.serverSideFunctions = []
  

  def clearResultVariables(self):
    """
    Clears from the results variables stack all the variabkles provided by the 
    `erddapClient.ERDDAP_Dataset.setResultsVariables` and 
    `erddapClient.ERDDAP_Dataset.addResultVariable` methods
    
    """       
    self.resultVariables = []


  def clearQuery(self):
    """
    Clears all the query elements of the stack, variables, constraints and
    server side variables.

    """
    self.clearConstraints()
    self.clearServerSideFunctions()
    self.clearResultVariables()


  def getData(self, filetype=DEFAULT_FILETYPE, request_kwargs={}):
    """
    Makes a data request to the ERDDAP server, the request url is build
    using the `erddapClient.ERDDAP_Dataset.getURL` function. 

    Aditional request arguments for the urlread function can be provided
    as kwargs in this function.

    Returns either a string or a binary format (`erddapClient.ERDDAP_Dataset.BINARY_FILETYPES`) 
    depending on the filetype specified in the query.

    """
    rawRequest = urlread(self.getDataRequestURL(filetype), auth=self.erddapauth, **request_kwargs)
    if filetype in self.BINARY_FILETYPES:
      return rawRequest.content
    else:
      return rawRequest.text

  def getDataFrame(self, request_kwargs={}, **kwargs):
    """
    This method makes a data request to the ERDDAP server in csv format
    then convert it to a pandas object. 
    
    The pandas object is created using the read_csv method, and 
    additional arguments for this method can be provided as kwargs in this
    method.

    Returns the pandas DataFrame object.
    """
    csvpdata = self.getData('csvp', **request_kwargs)
    return pd.read_csv(StringIO(csvpdata), **kwargs)
