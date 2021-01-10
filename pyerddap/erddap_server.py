import os
from urllib.parse import quote_plus
from pyerddap import url_operations
from pyerddap.parse_utils import parseConstraintValue, parseConstraintDateTime
from pyerddap.remote_requests import urlread
from pyerddap.erddap_dataset import ERDDAP_Dataset

class ERDDAP:

    ALLDATASETS_VARIABLES = ['datasetID','accessible','institution','dataStructure','cdm_data_type','class','title','minLongitude','maxLongitude','longitudeSpacing','minLatitude','maxLatitude','latitudeSpacing','minAltitude','maxAltitude','minTime','maxTime','timeSpacing','griddap','subset','tabledap','MakeAGraph','sos','wcs','wms','files','fgdc','iso19115','metadata','sourceUrl','infoUrl','rss','email','testOutOfDate','outOfDate','summary']

    def __init__(self, url, auth=None, lazyload=True):
        self.serverURL = url 
        self.tabledapAllDatasets = ERDDAP_Dataset(self.serverURL, 'allDatasets', auth=auth)


    def getSearchURL(self, filetype='json', searchFor="", 
                                            protocol="",
                                            cdm_data_type="",
                                            institution="",
                                            ioos_category="",
                                            keywords="",
                                            long_name="",
                                            standard_name="",
                                            variableName="",
                                            minLon="",
                                            maxLon="",
                                            minLat="",
                                            maxLat=None,
                                            minTime="",
                                            maxTime="",
                                            itemsPerPage=1000, page=1):

        searchAPIEndpoint = "search/advanced.{}".format(filetype)
        searchAPIURL = os.path.join( self.serverURL, searchAPIEndpoint )

        queryElementsDefaults = { 'page'          : 1 ,
                                  'itemsPerPage'  : 1000,
                                  'searchFor'     : None,
                                  'protocol'      : "(ANY)",
                                  'cdm_data_type' : "(ANY)",
                                  'institution'   : "(ANY)",
                                  'ioos_category' : "(ANY)",
                                  'keywords'      : "(ANY)",
                                  'long_name'     : "(ANY)",
                                  'standard_name' : "(ANY)",
                                  'variableName'  : "(ANY)",
                                  'maxLat'        : None,
                                  'minLon'        : None,
                                  'maxLon'        : None,
                                  'minLat'        : None,
                                  'minTime'       : None,
                                  'maxTime'       : None}
        queryURL=[]

        for queryElement, queryElementDefault in queryElementsDefaults.items():
                        
            queryValue = eval(queryElement) if eval(queryElement) else queryElementDefault

            if queryElement == 'searchFor':
                if queryValue:
                    queryValue = quote_plus(queryValue)
                queryURL.append( queryElement + "=" + ("" if queryValue is None else queryValue) )
                continue
 
            if queryValue is None:
                queryURL.append( queryElement + "=" )      
            elif queryElement in ['minTime', 'maxTime']:
                queryURL.append( queryElement + "=" + parseConstraintDateTime(queryValue) )
            else: 
                queryURL.append( queryElement + "=" + str(queryValue) )
        
        return url_operations.joinURLElements(searchAPIURL, url_operations.parseQueryItems(queryURL, safe='=+-&'))
        #return searchAPIURL + "?" + "&".join(queryURL)


    def getQueryAllDatasetsURL(self, filetype='json', constraints=[]):

        resultVariables = self.ALLDATASETS_VARIABLES
        response = (
            self.tabledapAllDatasets.setResultVariables(resultVariables)
                                    .setConstraints(constraints)
                                    .getDataRequestURL(filetype=filetype)
        )
        return response


        