import os
from urllib.parse import quote
from pyerddap.remote_requests import urlread
from pyerddap.parse_utils import parseDictMetadata
from pyerddap.formatting import dataset_repr

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


  def setConstraints(self, constraintList):
    self.constraints = constraintList

  def addConstraints(sef, constraintList):
    for constraint in constraintList:
      self.addConstraint(constraint)
    return self

  def addConstraint(self, constraint):
    self.constraints.append(constraint)
    return self


  def getDataRequestURL(self, filetype=DEFAULT_FILETYPE, isQuoted=True):
    
    requestURL = self.getDownloadURL(filetype)
    query = ""

    if len(self.resultVariables) > 0:
      query += self.parseQueryItems(self.resultVariables, isQuoted, safe='', argument_separator=',')

    if len(self.constraints) > 0:
      query += '&' + self.parseQueryItems(self.constraints, isQuoted, safe='=!()&')

    if len(self.serverSideFunctions) > 0:
      query += '&' + self.parseQueryItems(self.serverSideFunctions, isQuoted, safe='=!()&/')

    if len(query)>0:
      requestURL += '?' + query

    self.lastRequestURL = requestURL
    return self.lastRequestURL


  def parseQueryItems(self, items, isQuoted=True, safe='', argument_separator='&'):
    if isQuoted:
      return quote(argument_separator.join(items), safe=safe)
    else:
      return argument_separator.join(items)


  def getDownloadURL(self, filetype=DEFAULT_FILETYPE):
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
    self.serverSideFunctions.append( 'addVariablesWhere("%s","%s")' % (attributeName, attributeValue) )
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
    self.serverSideFunctions.append( 'units(%s)' % value )

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
    self.serverSideFunctions.append( '%s("%s")' % ( functionName, self.parseListOrStrToCommaSeparatedString(arguments) ) )


  def parseListOrStrToCommaSeparatedString(self, listorstring):
    if type(listorstring) is list:
      return ','.join(listorstring)
    else:
      return listorstring        



