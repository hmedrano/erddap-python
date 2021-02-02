import os
from urllib.parse import quote_plus
from erddapClient import url_operations
from erddapClient.formatting import erddap_search_results_repr, erddap_server_repr
from erddapClient.parse_utils import parseConstraintValue, parseConstraintDateTime, parseSearchResults
from erddapClient.remote_requests import urlread
from erddapClient.erddap_dataset import ERDDAP_Dataset
from erddapClient.erddap_tabledap import ERDDAP_Tabledap
from erddapClient.erddap_griddap import ERDDAP_Griddap
from erddapClient.erddap_constants import ERDDAP_Metadata_Rows, ERDDAP_Search_Results_Rows


class ERDDAP_SearchResult(object):
    datasetid = None
    title     = None
    summary   = None 

    def __init__(self, url, erddapSearchResultRow, auth=None, lazyload=True):
        self.datasetid, self.title, self.summary = \
            erddapSearchResultRow[ERDDAP_Search_Results_Rows.DATASETID], \
            erddapSearchResultRow[ERDDAP_Search_Results_Rows.TITLE], \
            erddapSearchResultRow[ERDDAP_Search_Results_Rows.SUMMARY]
        if erddapSearchResultRow[ERDDAP_Search_Results_Rows.GRIDDAP]:
            self.dataset = ERDDAP_Griddap(url, self.datasetid, auth=auth, lazyload=lazyload)
        elif erddapSearchResultRow[ERDDAP_Search_Results_Rows.TABLEDAP]:
            self.dataset = ERDDAP_Tabledap(url, self.datasetid, auth=auth, lazyload=lazyload)
    
    def __get__(self, instance, owner):
        return self.dataset


class ERDDAP_SearchResults(list):

    def __init__(self, url, erddapSearchRows, auth=None, lazyload=True):
        for erddapSearchRow in erddapSearchRows:
            self.append(ERDDAP_SearchResult(url, erddapSearchRow, auth=auth, lazyload=lazyload))
    
    def __repr__(self):
        return erddap_search_results_repr(self)

    def __getitem__(self, key):
        return super(ERDDAP_SearchResults, self).__getitem__(key).dataset
        
    # def append()
        
    @property
    def results(self):
        return list(self)     


class ERDDAP_Server:

    ALLDATASETS_VARIABLES = [ 'datasetID','accessible','institution','dataStructure',
                              'cdm_data_type','class','title','minLongitude','maxLongitude',
                              'longitudeSpacing','minLatitude','maxLatitude','latitudeSpacing',
                              'minAltitude','maxAltitude','minTime','maxTime','timeSpacing',
                              'griddap','subset','tabledap','MakeAGraph','sos','wcs','wms',
                              'files','fgdc','iso19115','metadata','sourceUrl','infoUrl',
                              'rss','email','testOutOfDate','outOfDate','summary' ]

    def __init__(self, url, auth=None, lazyload=True):
        self.serverURL = url 
        self.auth = auth
        self.tabledapAllDatasets = ERDDAP_Dataset(self.serverURL, 'allDatasets', auth=auth)

    def __repr__(self):
        return erddap_server_repr(self)

    @property
    def version(self):
        if not hasattr(self,'__version'):
            try:
                req = urlread( os.path.join(self.serverURL, 'version'), self.auth)
                __version = req.text
                __version = __version.replace("\n", "")
            except:
                __version = 'ERDDAP_version=<1.22'
            return __version

    @property
    def version_string(self):
        if not hasattr(self,'__version_string'):
            try:
                 req = urlread( os.path.join(self.serverURL, 'version_string'), self.auth)
                 __version_string = req.text
                 __version_string = __version_string.replace("\n", "")
            except:
                __version_string = 'ERDDAP_version_string=<1.80'
            return __version_string

    def advancedSearch(self, **filters):
        """
        """

        searchURL = self.getSearchURL( **filters)
        rawSearchResults = urlread(searchURL, self.auth)
        dictSearchResult = rawSearchResults.json()
        formatedResults = ERDDAP_SearchResults(self.serverURL, dictSearchResult['table']['rows'])

        # _griddap_dsets , _tabledap_dsets = parseSearchResults(dictSearchResult)
        # for dst in _tabledap_dsets:
        #     formatedResults.append(ERDDAP_Tabledap(self.serverURL, dst, auth=self.auth))
        # for dst in _griddap_dsets:
        #     formatedResults.append(ERDDAP_Griddap(self.serverURL, dst, auth=self.auth))

        return formatedResults

        
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


        