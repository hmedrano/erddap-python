from erddapClient.erddap_dataset import ERDDAP_Dataset
from erddapClient.formatting import tabledap_str
from erddapClient.parse_utils import castTimeRangeAttribute, ifListToCommaSeparatedString


class ERDDAP_Tabledap(ERDDAP_Dataset):
  """
  Class with the representation and methods for a ERDDAP Tabledap Dataset

  """

  DEFAULT_FILETYPE = 'csvp'

  def __init__(self, url, datasetid, auth=None, lazyload=True):
    """
    Constructs the ERDDAP_Tabledap, and if specified, automaticaly loads
    the metadata information of the dataset.

    Arguments:

    `url` : The url of the ERDDAP Server that contains the tabledap dataset.

    `datasetid` : The identifier of the dataset.

    `auth` : Tupple with username and password for a protected ERDDAP Server.

    `lazyload` : If false calls the loadMetadata method.

    """
    super().__init__(url, datasetid, 'tabledap', auth, lazyload=lazyload)

  def __str__(self):
    dst_repr_ = super().__str__()
    return dst_repr_ + tabledap_str(self)

  def loadMetadata(self):
    if super().loadMetadata():
      self._castTimeVariable()

  def _castTimeVariable(self):
    for varName, varAtts in self.variables.items():
      if '_CoordinateAxisType' in varAtts.keys() and varAtts['_CoordinateAxisType'] == 'Time':
        varAtts['actual_range'] = castTimeRangeAttribute(varAtts['actual_range'], varAtts['units'])


  # 
  # Tabledap server side functions wrappers
  # 
  def addVariablesWhere(self, attributeName, attributeValue):
    '''
    Adds "addVariablesWhere" server side function to the data request query
    [https://coastwatch.pfeg.noaa.gov/erddap/tabledap/documentation.html#addVariablesWhere](https://coastwatch.pfeg.noaa.gov/erddap/tabledap/documentation.html#addVariablesWhere)
    '''
    self.serverSideFunctions.append( 
      'addVariablesWhere("{}","{}")'.format(attributeName, attributeValue) 
    )
    return self

  def distinct(self):
    '''
    Adds "distinct" server side function to the data request query
    [https://coastwatch.pfeg.noaa.gov/erddap/tabledap/documentation.html#distinct](https://coastwatch.pfeg.noaa.gov/erddap/tabledap/documentation.html#distinct)
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
        functionName, ifListToCommaSeparatedString(arguments)
      )
    )


     

  