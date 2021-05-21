from collections import OrderedDict 
from erddapClient.formatting import erddap_dimensions_str, erddap_dimension_str
from erddapClient.parse_utils import iso8601STRtoNum, numtodate, dttonum
import datetime as dt


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

  def subset(self, *pdims, **kwdims):
    """
    This method receives slices for the dimensions, parses and returns the numeric
    index values, in slice objects.

    Usage example:
    ```
    iidx = dimensions.subset(slice("2014-06-15","2014-07-15"), 0.0, slice(18.1,31.96), slice(-98, -76.41)) 
    # or 
    iidx = dimensions.subset(time=slice("2014-06-15","2014-07-15"), depth=0.0, latitude=slice(18.1,31.96), longitude=slice(-98, -76.41)) 
    ```
    """

    def parseSlice(sobj, dref):
      estart, estop, estep = None, None, None
      if isinstance(sobj, slice):
        if sobj.start is None:
          estart = None
        else:
          estart = dref.closestIdx(sobj.start)
          if estart is None:
            raise Exception("{} its outside the dimensions values of {}".format(sobj.start, dref.name))
        
        if sobj.stop is None:
          estop = None
        else:
          estop = dref.closestIdx(sobj.stop)
          if estop is None:
            raise Exception("{} its outside the dimensions values of {}".format(sobj.stop, dref.name))

        estep = sobj.step if not sobj.step is None else None
        print("Slice stop parameter : ", estop, dref.name, sobj.stop)
      else:
        estop = dref.closestIdx(sobj)

      if estart is None:
        return slice(estop, estop + 1)
      else:
        return slice(estart, estop + 1, estep)

    #   
    rsubset = OrderedDict( { k : None for k in self.keys() } )
    
    for idx, pdim in enumerate(pdims):
      rsubset[self[idx].name] = parseSlice(pdim,self[idx])

    for kdim, vdim in kwdims.items():
      rsubset[kdim] = parseSlice(vdim, self[kdim])
    
    return rsubset

  @property
  def timeDimension(self):
    if 'time' in self.keys():
      return self['time']
    else:
      None
    
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

  def __getitem__(self, val):
    return self.values.index[val]

  def __str__(self):
    return erddap_dimension_str(self)

  def closestIdx(self, value, method='nearest'):
    """
    Returns the integer index that matches the closest 'value' in 
    dimensions values.

    Arguments:

    `value` : The value to search in the dimension values.  If the object
    contains a time dimension, this parameter can be a valid ISO 86091 string
    or datetime.

    `method` : The argument passed to pandas index.get_loc method
    that returns the closest value index.
    """

    if self.isTime and isinstance(value,str):
      value = iso8601STRtoNum(value)
    elif isinstance(value, dt.datetime):
      value = dttonum(value)

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
  def timeData(self):
    if self.isTime:
      return numtodate(self.data)

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



