from pyerddap.erddap_dataset import ERDDAP_Dataset

class ERDDAP_Griddap(ERDDAP_Dataset):

  DEFAULT_FILETYPE = 'csvp'

  def __init__(self, url, datasetid, auth=None, lazyload=True):
    super().__init__(url, datasetid, 'griddap', auth, lazyload=lazyload)