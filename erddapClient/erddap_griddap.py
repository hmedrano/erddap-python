from erddapClient.erddap_dataset import ERDDAP_Dataset
from erddapClient.formatting import griddap_str
from erddapClient.parse_utils import castTimeRangeAttribute
from netCDF4 import Dataset
import xarray as xr 
import requests

class ERDDAP_Griddap(ERDDAP_Dataset):

  DEFAULT_FILETYPE = 'nc'

  def __init__(self, url, datasetid, auth=None, lazyload=True):
    super().__init__(url, datasetid, 'griddap', auth, lazyload=lazyload)

  def __str__(self):
    dst_repr_ = super().__str__()
    return dst_repr_ + griddap_str(self)

  def loadMetadata(self):
    if super().loadMetadata():
      self._castTimeDimension()

  def _castTimeDimension(self):
    for dimName, dimAtts in self.dimensions.items():
      if '_CoordinateAxisType' in dimAtts.keys() and dimAtts['_CoordinateAxisType'] == 'Time':
        dimAtts['actual_range'] = castTimeRangeAttribute(dimAtts['actual_range'], dimAtts['units'])

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
        # Add user, password in URL
        self.__netcdf4Dataset = Dataset(self.getBaseURL('opendap'))
      else:
        self.__netcdf4Dataset = Dataset(self.getBaseURL('opendap'))
    return self.__netcdf4Dataset    