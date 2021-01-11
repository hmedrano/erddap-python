import os
from urllib.parse import quote_plus
from pyerddap import url_operations
from pyerddap.formatting import erddap_search_results_repr
from pyerddap.parse_utils import parseConstraintValue, parseConstraintDateTime, parseSearchResults
from pyerddap.remote_requests import urlread
from pyerddap.erddap_dataset import ERDDAP_Dataset
from pyerddap.erddap_tabledap import ERDDAP_Tabledap
from pyerddap.erddap_griddap import ERDDAP_Griddap


class ERDDAP_SearchResults(list):

    def __repr__(self):
        return erddap_search_results_repr(self)
        
    @property
    def results(self):
        return list(self)     

class ERDDAP:

    ALLDATASETS_VARIABLES = ['datasetID','accessible','institution','dataStructure','cdm_data_type','class','title','minLongitude','maxLongitude','longitudeSpacing','minLatitude','maxLatitude','latitudeSpacing','minAltitude','maxAltitude','minTime','maxTime','timeSpacing','griddap','subset','tabledap','MakeAGraph','sos','wcs','wms','files','fgdc','iso19115','metadata','sourceUrl','infoUrl','rss','email','testOutOfDate','outOfDate','summary']

    def __init__(self, url, auth=None, lazyload=True):
        self.serverURL = url 
        self.auth = auth
        self.tabledapAllDatasets = ERDDAP_Dataset(self.serverURL, 'allDatasets', auth=auth)


    def advancedSearch(self, **filters):

        searchURL = self.getSearchURL( **filters)
        rawSearchResults = urlread(searchURL, self.auth)
        dictSearchResult = rawSearchResults.json()
        formatedResults = ERDDAP_SearchResults()

        _griddap_dsets , _tabledap_dsets = parseSearchResults(dictSearchResult)
        for dst in _tabledap_dsets:
            formatedResults.append(ERDDAP_Tabledap(self.serverURL, dst, auth=self.auth))
        for dst in _griddap_dsets:
            formatedResults.append(ERDDAP_Griddap(self.serverURL, dst, auth=self.auth))

        return formatedResults

        


    #def getSearchURL(self, filetype='json', searchFor="", 
    #                                        protocol="",
    #                                        cdm_data_type="",
    #                                        institution="",
    #                                        ioos_category="",
    #                                        keywords="",
    #                                        long_name="",
    #                                        standard_name="",
    #                                        variableName="",
    #                                        minLon="",
    #                                        maxLon="",
    #                                        minLat="",
    #                                        maxLat="",
    #                                        minTime="",
    #                                        maxTime="",
    #                                        itemsPerPage=1000, page=1):
    def getSearchURL(self, filetype='json', **searchFilters): 
        """
         Builds the url call for the advanced Search ERDDAP API Rest service.

          Arguments
           filetype   -  The result format (htmlTable, csv, json, tsv, etc)
                         https://coastwatch.pfeg.noaa.gov/erddap/rest.html#responses 

          Search filters:
           searchFor     - This is a Google-like search of the datasets metadata, set the words you 
                           want to search for  with spaces between the words.  ERDDAP will search 
                           for the words separately, not as a phrase. 
                           To search for a phrase, put double quotes around the phrase (for 
                           example, "wind speed"). 
                           To exclude datasets with a specific word, use -excludedWord. 
                           To exclude datasets with a specific phrase, use -"excluded phrase" 
                           To search for specific attribute values, use attName=attValue
                           To find just grid or table datasets, include protocol=griddap 
                           or protocol=tabledap

           protocolol    - Set either: griddap, tabledap or wms                           
           cdm_data_type -
           institution   - 
           ioos_category - 
           keywords      - 
           long_name     - 
           standard_name - 
           variableName  - 
           minLon        -
           maxLon        -
           minLat        - 
           maxLat        -
           minTime       -
           maxTime       -
           itemsPerPage  -
           page          -

          Returns the string url for the search service.

        """

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
                        
            #queryValue = eval(queryElement) if eval(queryElement) else queryElementDefault
            queryValue = searchFilters.get(queryElement, queryElementDefault)

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


        