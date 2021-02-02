import os
from erddapClient import url_operations
from erddapClient.remote_requests import urlread
from erddapClient.parse_utils import parseDictMetadata, parseConstraintValue
from erddapClient.formatting import dataset_repr, simple_dataset_repr
import datetime as dt


class ERDDAP_Dataset:

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


  def __repr__(self):
    return dataset_repr(self)

  def __simple_repr__(self):
    return simple_dataset_repr(self)
  

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
    if variableName == 'NC_GLOBAL':
      if attribute in self.__metadata['global'].keys():
        return self.__metadata['global'][attribute]
    else:
      for vd in [ self.__metadata['dimensions'], self.__metadata['variables'] ]:
        if variableName in vd.keys():
          if attribute in vd[variableName].keys():
            return vd[variableName][attribute]


  def loadMetadata(self):
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
  def global_metadata(self):
    return self.__metadata['global']


  def getMetadataURL(self, filetype='json'):
    return os.path.join(self.erddapurl, "info", self.datasetid , "index." + filetype )


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


  def getData(self, filetype=DEFAULT_FILETYPE, request_kwargs={}):
    rawRequest = urlread(self.getDataRequestURL(filetype), auth=self.erddapauth, **request_kwargs)
    if filetype in self.BINARY_FILETYPES:
      return rawRequest.content
    else:
      return rawRequest.text


