import os
from io import StringIO
import pandas as pd
from urllib.parse import quote
from pyerddap.remote_requests import urlread











# TODO

class ERDDAP:
  '''
  '''
  def __init__(self, erddapurl, datasetid, protocol='tabledap', auth=None):
    
    self.erddapurl = erddapurl
    self.datasetid = datasetid
    self.protocol = protocol
    self.metadataRequest = None
    self.erddapauth = auth
    self.requestURL = None 

  def __repr__(self):
    return "ERDDAP Server : %s\nSelected dataset id: %s (%s)\n" % (self.erddapurl, self.datasetid, self.protocol)

  def generateDataURL(self, format='csvp'):
    self._dataRequestURL = os.path.join(self.erddapurl, self.protocol, self.datasetid + "." + format )
    return self 


  def getMetadataURL(self, request_format='json'):
    return os.path.join(self.erddapurl, "info", self.datasetid , "index." + request_format )

  def requesturl(self, request_format='csvp', quote_url=False, **kwargs):
    '''
      Params:
       : dataformat - The output format of the request, default is csvp
       : **kwargs
         varlist - A string or list containing the requested variables
         options - A dict with the erddap options / constraints

    '''
    varlist=None
    if "varlist" in kwargs:
      varlist = kwargs.get("varlist")
    options=None
    if "options" in kwargs:
      options = kwargs.get("options")
    functions=None
    if "functions" in kwargs:
      functions = kwargs.get("functions")

    response = os.path.join(self.erddapurl, self.protocol, self.datasetid + "." + request_format )
    if varlist:
      if type(varlist) is list:
        vparams = ','.join(varlist)
      else:
        vparams = varlist
      if quote_url:
        response += '?' + quote(vparams,safe='')
      else:
        response += '?' + vparams

    if options:
      if type(options) is list:
        oparams = '&'.join(options)
      elif type(options) is dict:
        # Parse string contraints
        options = { k: f'"{v}"' if isinstance(v, str) else v for k, v in options.items() }
        oparams = '&'.join( [f"{k}{v}" for k, v in options.items() ] )
      else:
        oparams = options
      if quote_url:
        response += '&' + quote(oparams,safe='=!()&')
      else:
        response += '&' + oparams
      # Dont quote option parameters
      # response += '&' + oparams

    if functions:
      if type(functions) is list:
        fparams = '&'.join(functions)
      else:
        fparams = varlist
      if quote_url:
        response += '&' + quote(fparams,safe='()&')
      else:
        response += '&' + fparams


    self._requesturl = response
    return response


  def getAttribute(self, attribute, variableName='NC_GLOBAL'):
      '''
      Request a specific attribute in erddap metadata json file
      '''
      if self.metadataRequest == None:
          if (self.erddapauth):
            self.metadataRequest = requests.get(self.metadataurl(), auth=self.erddapauth)
          else:
            self.metadataRequest = requests.get(self.metadataurl())

      if self.metadataRequest.status_code == 200:
          metadata = self.metadataRequest.json()
          dmetadata=[]
          # Playing around and making a dictionary from the lists columnNames and array of rows
          for row in metadata['table']['rows']:
              drow = dict(zip(metadata['table']['columnNames'],row))
              dmetadata.append(drow)

          # make the search more organic, by column names
          for rowAttribute in dmetadata:
              if rowAttribute['Variable Name'] == variableName and rowAttribute['Attribute Name'] == attribute:
                  return rowAttribute['Value']

      return ''

  def requestData(self, out='pandas', **kwargs):
    '''
      After creating a request url, with requesturl function, load the
      data with this function, the output can be a pandas dataframe or a string

      Params:
        out : A string with the output type, can be "pandas" to ouput pandas dataframe
              or "raw" to get the raw string from the url request

      Returns:
        pandas dataframe by default, else the rawstring from request
    '''
    if (self._requesturl):
      if (self.erddapauth):
        response = requests.get(self._requesturl, auth=self.erddapauth)
      else:
        response = requests.get(self._requesturl)

      if response.status_code == 200:
        rawdata = response.text
        if out=='pandas':
          return pd.read_csv(StringIO(rawdata), **kwargs)
        else:
          return rawdata
      else:
        response.raise_for_status()
    else:
      return None


  def getVarList(self, varlist=None):
    '''

    '''
    if (self.erddapauth):
      metadataRequest = requests.get(self.metadataurl(), auth=self.erddapauth)
    else:
      metadataRequest = requests.get(self.metadataurl())

    if metadataRequest.status_code == 200:
        metadata = metadataRequest.json()
        dmetadata=[]
        # Playing around and making a dictionary from the lists columnNames and array of rows
        for row in metadata['table']['rows']:
            drow = dict(zip(metadata['table']['columnNames'],row))
            dmetadata.append(drow)

        vars=[]
        for rowAttribute in dmetadata:
            if rowAttribute['Row Type'] == 'variable':
                vars.append(rowAttribute['Variable Name'])
        response={}

        for var in vars:
            if type(varlist) is list:
              addvar = True if var in varlist else False
            else:
              addvar=True
            if addvar:
              response[var]={'attributes':[]}
              for rowAttribute in dmetadata:
                  if rowAttribute['Variable Name'] == var and rowAttribute['Row Type'] == 'attribute':
                      response[var]['attributes'].append({'name':rowAttribute['Attribute Name'],
                                                          'type':rowAttribute['Data Type'],
                                                          'value':rowAttribute['Value'] })

        return response
    return ''
