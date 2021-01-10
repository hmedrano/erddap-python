import os
from pyerddap import url_operations
from pyerddap.remote_requests import urlread
from pyerddap.parse_utils import parseDictMetadata, parseConstraintValue
from pyerddap.formatting import dataset_repr
import datetime as dt

class ERDDAP_Dataset:

  DEFAULT_FILETYPE = 'csvp'
  BINARY_FILETYPES = [ 'dods', 'mat', 'nc', 'ncCF', 'ncCFMA', 'wav' ]

  def __init__(self, erddapurl, datasetid, protocol='tabledap', auth=None, lazyload=True):
    self.erddapurl = erddapurl
    self.datasetid = datasetid
    self.protocol = protocol
    self.metadata = None
    self.erddapauth = auth
    self.requestURL = None 
    self.resultVariables = []
    self.constraints = []
    self.serverSideFunctions = []
    self.variables = {} 
    if not lazyload:
      self.loadMetadata()

  def __repr__(self):
    return dataset_repr(self)
  

  def setResultVariables(self, variables):
    if type(variables) is list:
      self.resultVariables = variables 
    elif type(variables) is str:
      self.resultVariables = variables.split(',')
    else:
      raise Exception("variables argument must be list, or comma separated list of variables")
    
    return self

  def addResultVariable(self, variable):
    self.resultVariables.append(variable)
    return self

  def setConstraints(self, constraintListOrDict):
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


  def getBaseURL(self, filetype=DEFAULT_FILETYPE):
    if filetype.lower() == 'opendap':
      return os.path.join(self.erddapurl, self.protocol, self.datasetid )
    else:
      return os.path.join(self.erddapurl, self.protocol, self.datasetid + "." + filetype )
    

  def getAttribute(self, attribute, variableName='NC_GLOBAL'):
    self.loadMetadata()
    for rowAttribute in self.metadata:
      if rowAttribute['Variable Name'] == variableName and rowAttribute['Attribute Name'] == attribute:
          return rowAttribute['Value']


  def loadMetadata(self):
    if self.metadata is None:
      rawRequest = urlread(self.getMetadataURL(), auth=self.erddapauth)
      rawRequestJson = rawRequest.json()
      self.metadata, self.variables =  parseDictMetadata(rawRequestJson)


  def getMetadataURL(self, request_format='json'):
    return os.path.join(self.erddapurl, "info", self.datasetid , "index." + request_format )


  def clearConstraints(self):
    self.constraints = []
  
  def clearServerSideFunctions(self):
    self.serverSideFunctions = []
  
  def clearResultVariables(self):
    self.resultVariables = []

  def clearQuery(self):
    self.clearConstraints()
    self.clearServerSideFunctions()
    self.clearResultVariables()


  def getDataRequest(self, filetype=DEFAULT_FILETYPE, request_kwargs={}):
    rawRequest = urlread(self.getDataRequestURL(filetype), auth=self.erddapauth, **request_kwargs)
    if filetype in self.BINARY_FILETYPES:
      return rawRequest.content
    else:
      return rawRequest.text

  # Server side functions wrappers

  def addVariablesWhere(self, attributeName, attributeValue):
    '''
     https://coastwatch.pfeg.noaa.gov/erddap/tabledap/documentation.html#addVariablesWhere
    '''
    self.serverSideFunctions.append( 
      'addVariablesWhere("{}","{}")'.format(attributeName, attributeValue) 
    )
    return self

  def distinct(self):
    '''
     https://coastwatch.pfeg.noaa.gov/erddap/tabledap/documentation.html#distinct
    '''
    self.serverSideFunctions.append( 'distinct()' )
    return self
  
  def units(self, value):
    '''
     https://coastwatch.pfeg.noaa.gov/erddap/tabledap/documentation.html#units
    '''
    self.serverSideFunctions.append( 'units({})'.format(value) )

  def orderBy(self, variables):
    '''
     https://coastwatch.pfeg.noaa.gov/erddap/tabledap/documentation.html#orderBy
    '''
    self.addServerSideFunction('orderBy', variables)
    return self
  
  def orderByClosest(self, variables):
    '''
     https://coastwatch.pfeg.noaa.gov/erddap/tabledap/documentation.html#orderByClosest
    '''
    self.addServerSideFunction('orderByClosest', variables)
    return self

  def orderByCount(self, variables):
    '''
     https://coastwatch.pfeg.noaa.gov/erddap/tabledap/documentation.html#orderByCount
    '''
    self.addServerSideFunction('orderByCount', variables)
    return self    

  def orderByLimit(self, variables):
    '''
     https://coastwatch.pfeg.noaa.gov/erddap/tabledap/documentation.html#orderByLimit
    '''
    self.addServerSideFunction('orderByLimit', variables)
    return self

  def orderByMax(self, variables):
    '''
     https://coastwatch.pfeg.noaa.gov/erddap/tabledap/documentation.html#orderByMax
    '''    
    self.addServerSideFunction('orderByMax', variables)
    return self    

  def orderByMin(self, variables):
    '''
     https://coastwatch.pfeg.noaa.gov/erddap/tabledap/documentation.html#orderByMin
    ''' 
    self.addServerSideFunction('orderByMin', variables)
    return self    

  def orderByMinMax(self, variables):
    '''
     https://coastwatch.pfeg.noaa.gov/erddap/tabledap/documentation.html#orderByMinMax
    '''    
    self.addServerSideFunction('orderByMinMax', variables)
    return self  

  def orderByMean(self, variables):
    '''
     https://coastwatch.pfeg.noaa.gov/erddap/tabledap/documentation.html#orderByMean
    '''    
    self.addServerSideFunction('orderByMean', variables)
    return self     

  def addServerSideFunction(self, functionName, arguments):
    self.serverSideFunctions.append(
      "{}(\"{}\")".format(
        functionName, self.parseListOrStrToCommaSeparatedString(arguments)
      )
    )


  def parseListOrStrToCommaSeparatedString(self, listorstring):
    if type(listorstring) is list:
      return ','.join(listorstring)
    else:
      return listorstring        



