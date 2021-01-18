from erddapClient.erddap_dataset import ERDDAP_Dataset
import xarray as xr 
import requests

class ERDDAP_Griddap(ERDDAP_Dataset):

  DEFAULT_FILETYPE = 'nc'

  def __init__(self, url, datasetid, auth=None, lazyload=True):
    super().__init__(url, datasetid, 'griddap', auth, lazyload=lazyload)


  @property
  def xarray(self):
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
