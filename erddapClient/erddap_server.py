import os
import pandas as pd
from urllib.parse import quote_plus
from erddapClient import url_operations
from erddapClient.formatting import erddap_search_results_repr, erddap_server_repr
from erddapClient.parse_utils import parseConstraintDateTime, parseERDDAPStatusPage, parseNumericVersion
from erddapClient.remote_requests import urlread
from erddapClient.erddap_dataset import ERDDAP_Dataset
from erddapClient.erddap_tabledap import ERDDAP_Tabledap
from erddapClient.erddap_griddap import ERDDAP_Griddap
from erddapClient.erddap_constants import ERDDAP_Metadata_Rows, ERDDAP_Search_Results_Row_Names



class ERDDAP_Server:
    """
    Class with the representation and methods to access a ERDDAP server.
    """

    ALLDATASETS_VARIABLES = [ 'datasetID','accessible','institution','dataStructure',
                              'cdm_data_type','class','title','minLongitude','maxLongitude',
                              'longitudeSpacing','minLatitude','maxLatitude','latitudeSpacing',
                              'minAltitude','maxAltitude','minTime','maxTime','timeSpacing',
                              'griddap','subset','tabledap','MakeAGraph','sos','wcs','wms',
                              'files','fgdc','iso19115','metadata','sourceUrl','infoUrl',
                              'rss','email','testOutOfDate','outOfDate','summary' ]


    def __init__(self, url, auth=None, lazyload=True, request_kwargs={}):
        """
        Constructs a ERDDAP Server object 
        ...
        Arguments:

        `url`  : The ERDDAP Server URL 

        `auth` : Tupple with username and password, to access a protected ERDDAP Server

        `lazyload` : If True (default) the server metadata and info of tabledapAllDatasets dataset will be loaded when requested by the available methods

        """
        self.serverURL = url 
        self.auth = auth
        self.request_kwargs = request_kwargs
        if self.auth:
            self.request_kwargs.update({ 'auth' : self.auth })
        self.tabledapAllDatasets = ERDDAP_Dataset(self.serverURL, 'allDatasets', auth=auth, lazyload=lazyload)
        """ An `erddapClient.ERDDAP_Tabledap` object with the reference to the "allDatasets" 
            Dataset, [About allDatasets](https://coastwatch.pfeg.noaa.gov/erddap/download/setupDatasetsXml.html#EDDTableFromAllDatasets) """
        self.__status_values = None

    def __repr__(self):
        return erddap_server_repr(self)

    @property
    def version_numeric(self):
        if not hasattr(self,'__version_numeric'):
            self.__version_numeric = parseNumericVersion(self.version)
        return self.__version_numeric  

    @property
    def version(self):
        if not hasattr(self,'__version'):
            try:
                req = urlread( url_operations.url_join(self.serverURL, 'version'), **self.request_kwargs)
                __version = req.text
                self.__version = __version.replace("\n", "")
            except:
                self.__version = 'ERDDAP_version=<1.22'
        return self.__version

    @property
    def version_string(self):
        if not hasattr(self,'__version_string'):
            try:
                 req = urlread( url_operations.url_join(self.serverURL, 'version_string'), **self.request_kwargs)
                 __version_string = req.text
                 self.__version_string = __version_string.replace("\n", "")
            except:
                self.__version_string = 'ERDDAP_version_string=<1.80'
        return self.__version_string


    def search(self, **filters):
        """
        Makes a search request to the ERDDAP Server

        Search filters kwargs:

        `searchFor` :

        * This is a Google-like search of the datasets metadata:
          Type the words you want to search for, with spaces between 
          the words.  ERDDAP will search for the words separately, 
          not as a phrase. 
        * To search for a phrase, put double quotes around the 
          phrase (for example, "wind speed"). 
          To exclude datasets with a specific word, use 
          -excludedWord To exclude datasets with a specific 
          phrase, use -"excluded phrase". 
        * Don't use AND between search terms. It is implied. The 
          results will include only the datasets that have all of 
          the specified words and phrases (and none of the excluded 
          words and phrases) in the dataset's metadata (data about 
          the dataset). 
        * Searches are not case-sensitive. 
        * To search for specific attribute values, use 
          attName=attValue . 
        * To find just grid or just table datasets, include 
          protocol=griddap or protocol=tabledap in your search. 
        * This ERDDAP is using searchEngine=original. 
        * In this ERDDAP, you can search for any part of a word. 
        * For example, searching for spee will find datasets with 
          speed and datasets with WindSpeed. 
        * In this ERDDAP, the last word in a phrase may be a partial 
          word. For example, to find datasets from a specific website 
          (usually the start of the datasetID), include (for example) 
          "datasetID=erd" in your search.

        Optional filters:

        `itemsPerPage` : Set the maximum number of results. (Default: 1000)

        `page` : If the number of results is bigger than the "`itemsPerPage`" you can
                specify the page of results. (Default: 1)

        Returns a `erddapClient.ERDDAP_SearchResults` object
        """

        searchURL = self.getSearchURL( **filters)
        rawSearchResults = urlread(searchURL, **self.request_kwargs)
        dictSearchResult = rawSearchResults.json()
        formatedResults = ERDDAP_SearchResults(self.serverURL, dictSearchResult, request_kwargs=self.request_kwargs)

        return formatedResults


    def getSearchURL(self, filetype='json', **searchFilters):
        """
        Builds the url call for the basic Search ERDDAP API Rest service.

        Arguments

        `filetype` :  The result format (htmlTable, csv, json, tsv, etc) 
                      [https://coastwatch.pfeg.noaa.gov/erddap/rest.html#responses](https://coastwatch.pfeg.noaa.gov/erddap/rest.html#responses)


        Search filters kwargs:

        `searchFor`        

        * This is a Google-like search of the datasets metadata:
          Type the words you want to search for, with spaces between 
          the words.  ERDDAP will search for the words separately, 
          not as a phrase. 
        * To search for a phrase, put double quotes around the 
          phrase (for example, "wind speed"). 
          To exclude datasets with a specific word, use 
          -excludedWord To exclude datasets with a specific 
          phrase, use -"excluded phrase". 
        * Don't use AND between search terms. It is implied. The 
          results will include only the datasets that have all of 
          the specified words and phrases (and none of the excluded 
          words and phrases) in the dataset's metadata (data about 
          the dataset). 
        * Searches are not case-sensitive. 
        * To search for specific attribute values, use 
          attName=attValue . 
        * To find just grid or just table datasets, include 
          protocol=griddap or protocol=tabledap in your search. 
        * This ERDDAP is using searchEngine=original. 
        * In this ERDDAP, you can search for any part of a word. 
        * For example, searching for spee will find datasets with 
          speed and datasets with WindSpeed. 
        * In this ERDDAP, the last word in a phrase may be a partial 
          word. For example, to find datasets from a specific website 
          (usually the start of the datasetID), include (for example) 
          "datasetID=erd" in your search.

        Optional filters:

        `itemsPerPage` :  Set the maximum number of results. (Default: 1000)

        `page` : If the number of results is bigger than the "itemsPerPage" you can
                 specify the page of results. (Default: 1)           

        Returns a string with the url search request.
        """
        searchAPIEndpoint = "search/index.{}".format(filetype)
        searchAPIURL = url_operations.url_join( self.serverURL, searchAPIEndpoint ) 

        queryElementsDefaults = { 'page'          : 1 ,
                                  'itemsPerPage'  : 1000,
                                  'searchFor'     : None}
        queryURL=[]

        for queryElement, queryElementDefault in queryElementsDefaults.items():                      
            
            queryValue = searchFilters.get(queryElement, queryElementDefault)

            if queryElement == 'searchFor':
                if queryValue:
                    queryValue = quote_plus(queryValue, safe='"\'')
                queryURL.append( queryElement + "=" + ("" if queryValue is None else queryValue) )
                continue
 
            if queryValue is None:
                queryURL.append( queryElement + "=" ) 
            else: 
                queryURL.append( queryElement + "=" + str(queryValue) )
        
        return url_operations.joinURLElements(searchAPIURL, url_operations.parseQueryItems(queryURL, safe='=+-&'))


    def advancedSearch(self, **filters):
        """
        Makes a advancedSearch request to the ERDDAP Server

        Search filters kwargs:

        `searchFor` : This is a Google-like search of the datasets metadata, set the words you 
                      want to search for  with spaces between the words.  ERDDAP will search 
                      for the words separately, not as a phrase. 
                      To search for a phrase, put double quotes around the phrase (for 
                      example, "wind speed"). 
                      To exclude datasets with a specific word, use -excludedWord. 
                      To exclude datasets with a specific phrase, use -"excluded phrase" 
                      To search for specific attribute values, use attName=attValue
                      To find just grid or table datasets, include protocol=griddap 
                      or protocol=tabledap

        Optional filters:

        `protocolol`    : Set either: griddap, tabledap or wms (Default: (ANY))

        `cdm_data_type` : Set either: grid, timeseries, point, timeseriesProfile, trajectory
                          trajectoryProfile, etc.. (Default: (ANY))

        `institution`   : Set either to one of the available instituion values in the ERDDAP
                          (Default: (ANY))

        `ioos_category` : Set either to one of the available ioos_category values in the ERDDAP
                          (Default: (ANY))

        `keywords`      : Set either to one of the available keywords values in the ERDDAP
                          (Default: (ANY))

        `long_name`     : Set either to one of the available long_name values in the ERDDAP
                          (Default: (ANY))

        `standard_name` : Set either to one of the available standard_name values in the ERDDAP
                          (Default: (ANY))

        `variableName`  : Set either to one of the available variable names values in the 
                          ERDDAP (Default: (ANY))
          
        `minLon`, `maxLon` : Some datasets have longitude values within -180 to 180, others 
                             use 0 to 360. If you specify Min and Max Longitude within -180 to 180
                             (or 0 to 360), ERDDAP will only find datasets that match the values 
                             you specify. Consider doing one search: longitude -180 to 360, or 
                             two searches: longitude -180 to 180, and 0 to 360.

        `minLat`, `maxLat` : Set latitude bounds, range -90 to 90 

        `minTime`, `maxTime` : Your can pass a <datetime> object or a string with the following
                               specifications

        > 
        - A time string with the format yyyy-MM-ddTHH:mm:ssZ,    
          for example, 2009-01-21T23:00:00Z.  If you specify something, you must include yyyy-MM-dd.   
          You can omit (backwards from the end) Z, :ss, :mm, :HH, and T.   
          Always use UTC (GMT/Zulu) time.   
        - Or specify the number of seconds since 1970-01-01T00:00:00Z.                                  
        - Or specify "now-nUnits", for example, "now-7days"        

        `itemsPerPage` : Set the maximum number of results. (Default: 1000)

        `page`         : If the number of results is bigger than the "`itemsPerPage`" you can
                         specify the page of results. (Default: 1)

        The search will find datasets that have some data within the specified 
        time bounds.

        Returns a `erddapClient.ERDDAP_SearchResults` object
        """

        searchURL = self.getAdvancedSearchURL( **filters)
        rawSearchResults = urlread(searchURL, **self.request_kwargs)
        dictSearchResult = rawSearchResults.json()
        formatedResults = ERDDAP_SearchResults(self.serverURL, dictSearchResult, request_kwargs=self.request_kwargs)

        return formatedResults


    def getAdvancedSearchURL(self, filetype='json', **searchFilters): 
        """
        Builds the url call for the advanced Search ERDDAP API Rest service.

        Search filters kwargs:

        `searchFor` : This is a Google-like search of the datasets metadata, set the words you 
                      want to search for  with spaces between the words.  ERDDAP will search 
                      for the words separately, not as a phrase. 
                      To search for a phrase, put double quotes around the phrase (for 
                      example, "wind speed"). 
                      To exclude datasets with a specific word, use -excludedWord. 
                      To exclude datasets with a specific phrase, use -"excluded phrase" 
                      To search for specific attribute values, use attName=attValue
                      To find just grid or table datasets, include protocol=griddap 
                      or protocol=tabledap

        Optional filters:

        `protocolol`    : Set either: griddap, tabledap or wms (Default: (ANY))

        `cdm_data_type` : Set either: grid, timeseries, point, timeseriesProfile, trajectory
                          trajectoryProfile, etc.. (Default: (ANY))

        `institution`   : Set either to one of the available instituion values in the ERDDAP
                          (Default: (ANY))

        `ioos_category` : Set either to one of the available ioos_category values in the ERDDAP
                          (Default: (ANY))

        `keywords`      : Set either to one of the available keywords values in the ERDDAP
                          (Default: (ANY))

        `long_name`     : Set either to one of the available long_name values in the ERDDAP
                          (Default: (ANY))

        `standard_name` : Set either to one of the available standard_name values in the ERDDAP
                          (Default: (ANY))

        `variableName`  : Set either to one of the available variable names values in the 
                          ERDDAP (Default: (ANY))
          
        `minLon`, `maxLon` : Some datasets have longitude values within -180 to 180, others 
                             use 0 to 360. If you specify Min and Max Longitude within -180 to 180
                             (or 0 to 360), ERDDAP will only find datasets that match the values 
                             you specify. Consider doing one search: longitude -180 to 360, or 
                             two searches: longitude -180 to 180, and 0 to 360.

        `minLat`, `maxLat` : Set latitude bounds, range -90 to 90 

        `minTime`, `maxTime` : Your can pass a <datetime> object or a string with the following
                               specifications

        > 
        - A time string with the format yyyy-MM-ddTHH:mm:ssZ,    
          for example, 2009-01-21T23:00:00Z.  If you specify something, you must include yyyy-MM-dd.   
          You can omit (backwards from the end) Z, :ss, :mm, :HH, and T.   
          Always use UTC (GMT/Zulu) time.   
        - Or specify the number of seconds since 1970-01-01T00:00:00Z.                                  
        - Or specify "now-nUnits", for example, "now-7days"        

        `itemsPerPage` : Set the maximum number of results. (Default: 1000)

        `page`         : If the number of results is bigger than the "`itemsPerPage`" you can
                         specify the page of results. (Default: 1)

        The search will find datasets that have some data within the specified 
        time bounds.

        Returns the string url for the search service.

        """

        searchAPIEndpoint = "search/advanced.{}".format(filetype)
        searchAPIURL = url_operations.url_join( self.serverURL, searchAPIEndpoint )

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


    def getQueryAllDatasetsURL(self, filetype='json', constraints=[]):
        """
        This method returns a string URL with the allDatasets default 
        Tabledap Dataset from ERDDAP. 

        Arguments:

        `filetype` : The result format for the request

        `constraints` : The request constraints list
        
        Returns a url string
        """

        resultVariables = self.ALLDATASETS_VARIABLES
        response = (
            self.tabledapAllDatasets.setResultVariables(resultVariables)
                                    .setConstraints(constraints)
                                    .getDataRequestURL(filetype=filetype)
        )
        return response


    @property
    def statusPageURL(self):
        """
        Returns the status.html url for the current ERDDAP Server reference.
        """
        if not hasattr(self,'__statusPageURL'):
            self.__statusPageURL = url_operations.url_join(self.serverURL, 'status.html')
        return self.__statusPageURL

    def parseStatusPage(self, force=False):
      """
      This method will load the status.html page of the current ERRDAP server reference 
      this data is parsed into a OrderedDict, with the scalars, and DataFrames with the
      tables provided in status.html page.
      The data will be available in the `erddapClient.ERDDAP_Server.statusValues` 
      property

      Parameters:

      `force` : Data is stored in a class property, if force is True, the data will be 
                reloaded, if False, the last loaded data is returned.

      """
      if self.__status_values is None or force:
        statusPageCode = urlread.__wrapped__( self.statusPageURL, auth=self.auth).text
        self.__status_values = parseERDDAPStatusPage(statusPageCode, numversion=self.version_numeric)

    @property
    def statusValues(self):
        """
        Returns a OrderedDict with the parsed data of the status.html page.
        More information on the data provided in status.html:
        [ERDDAP documentaiton](https://coastwatch.pfeg.noaa.gov/erddap/download/setup.html#monitoring)
        """
        self.parseStatusPage(force=False)
        return self.__status_values





class ERDDAP_SearchResult(object):
    datasetid = None
    title     = None
    summary   = None 

    def __init__(self, url, erddapSearchResultRow, auth=None, lazyload=True, request_kwargs={}):
        self.datasetid, self.title, self.summary = \
            erddapSearchResultRow[ERDDAP_Search_Results_Row_Names.DATASETID], \
            erddapSearchResultRow[ERDDAP_Search_Results_Row_Names.TITLE], \
            erddapSearchResultRow[ERDDAP_Search_Results_Row_Names.SUMMARY]
        if erddapSearchResultRow[ERDDAP_Search_Results_Row_Names.GRIDDAP]:
            self.dataset = ERDDAP_Griddap(url, self.datasetid, auth=auth, lazyload=lazyload, request_kwargs=request_kwargs)
        elif erddapSearchResultRow[ERDDAP_Search_Results_Row_Names.TABLEDAP]:
            self.dataset = ERDDAP_Tabledap(url, self.datasetid, auth=auth, lazyload=lazyload, request_kwargs=request_kwargs)
    
    def __get__(self, instance, owner):
        return self.dataset


class ERDDAP_SearchResults(list):

    def __init__(self, url, erddapSearchRows, auth=None, lazyload=True, request_kwargs={}):
        columnNames = erddapSearchRows['table']['columnNames']
        for erddapSearchRow in erddapSearchRows['table']['rows']:
            self.append(ERDDAP_SearchResult(url, dict(zip(columnNames, erddapSearchRow)), auth=auth, lazyload=lazyload, request_kwargs=request_kwargs))
    
    def __repr__(self):
        return erddap_search_results_repr(self)

    def __getitem__(self, key):
        if isinstance(key, slice):
            return [self[ii] for ii in range(*key.indices(len(self)))]
        return super(ERDDAP_SearchResults, self).__getitem__(key).dataset       
            
    @property
    def results(self):
        return list(self)     

