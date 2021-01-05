from pyerddap.erddap_dataset import ERDDAP_Dataset
from pyerddap.formatting import dataset_repr
from io import StringIO
import pandas as pd


class ERDDAP_Tabledap(ERDDAP_Dataset):

  DEFAULT_FILETYPE = 'csvp'

  def __init__(self, url, datasetid, auth=None, lazyload=True):
    super().__init__(url, datasetid, 'tabledap', auth, lazyload=lazyload)


  def getDataFrame(self, request_kwargs={}, **kwargs):
    csvpdata = self.getDataRequest('csvp', **request_kwargs)
    return pd.read_csv(StringIO(csvpdata), **kwargs)

  