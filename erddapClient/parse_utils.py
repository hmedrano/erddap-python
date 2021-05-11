import re
import datetime as dt
from dateutil.parser import parse 
from netCDF4 import date2num, num2date
from erddapClient.erddap_constants import ERDDAP_Metadata_Rows, ERDDAP_Search_Results_Rows, ERDDAP_TIME_UNITS, ERDDAP_DATETIME_FORMAT
from collections import OrderedDict
import pandas as pd

def parseDictMetadata(dmetadata):
    """
     This function parses the metadata json response from a erddap dataset
     This function receives a python dictionary created with the metadata response from a erddap dataset,
     It parses this dictionary and creates a new dictionary with the dimension variables, the data variables
     and the global metadata.
    """
    _dimensions=OrderedDict()
    _variables=OrderedDict()
    _global=OrderedDict()

    inforows = dmetadata['table']['rows']
    for row in inforows:
        drow = dict(zip(dmetadata['table']['columnNames'],row))
        if row[ERDDAP_Metadata_Rows.VARIABLE_NAME] == 'NC_GLOBAL':
            _global[row[ERDDAP_Metadata_Rows.ATTRIBUTE_NAME]] = \
                castMetadataAttribute(row[ERDDAP_Metadata_Rows.DATA_TYPE], row[ERDDAP_Metadata_Rows.VALUE])
        else:
            if row[ERDDAP_Metadata_Rows.ROW_TYPE] == 'dimension':
                _dimensions[row[ERDDAP_Metadata_Rows.VARIABLE_NAME]] = parseDimensionValue(row[ERDDAP_Metadata_Rows.VALUE])
                _dimensions[row[ERDDAP_Metadata_Rows.VARIABLE_NAME]]['_dataType'] = row[ERDDAP_Metadata_Rows.DATA_TYPE]
            elif row[ERDDAP_Metadata_Rows.ROW_TYPE] == 'variable':
                _variables[row[ERDDAP_Metadata_Rows.VARIABLE_NAME]] = {}
                _variables[row[ERDDAP_Metadata_Rows.VARIABLE_NAME]]['_dataType'] = row[ERDDAP_Metadata_Rows.DATA_TYPE]
            else: # Attributes
                if row[ERDDAP_Metadata_Rows.VARIABLE_NAME] in _dimensions:
                    # Dimension atts
                    _dimensions[row[ERDDAP_Metadata_Rows.VARIABLE_NAME]][row[ERDDAP_Metadata_Rows.ATTRIBUTE_NAME]] = \
                        castMetadataAttribute(row[ERDDAP_Metadata_Rows.DATA_TYPE], row[ERDDAP_Metadata_Rows.VALUE])
                else: 
                    # Variable atts
                    _variables[row[ERDDAP_Metadata_Rows.VARIABLE_NAME]][row[ERDDAP_Metadata_Rows.ATTRIBUTE_NAME]] = \
                        castMetadataAttribute(row[ERDDAP_Metadata_Rows.DATA_TYPE], row[ERDDAP_Metadata_Rows.VALUE])
    # .
    
    return { 'global' : _global, 'dimensions' : _dimensions, 'variables' : _variables }


def parseDimensionValue(value):
    """
    This method will parse the ERDDAP dimension name attribute value, that comes
    from the info page.
    Sample: nValues=16, evenlySpaced=false, averageSpacing=91 days 6h 24m 0s
    Returns a dictionary with each of this elements.
    """
    dimensionAttributes = {}
    elements = value.split(',')
    for e in elements:
        k,v = e.split('=')
        dimensionAttributes['_' + k.strip()] = guessCastMetadataAttribute(v.strip())
    return dimensionAttributes


def castMetadataAttribute(data_type, valuestr):
    """
    This method will try to cast valuestr to the data_type specified.
    valuestr can be a tuple of values separated with a comma.
    """
    if data_type != 'String' and ',' in valuestr:
        _lvaluestr = valuestr.split(',')
    elif data_type == 'String':
        return valuestr
    else:
        _lvaluestr = [valuestr]

    if data_type in ['float', 'double']:
        _castedvalue =  [ float(v) for v in _lvaluestr ]
    elif data_type in ['short', 'int', 'byte', 'char', 'short', 'long']:
        _castedvalue =  [ int(v) for v in _lvaluestr ]
    else:
        _castedvalue =  [ v for v in _lvaluestr ]

    if len(_castedvalue) == 1:
        return _castedvalue[0]
    else:
        return tuple(_castedvalue)

def parseTimeRangeAttributes(attItems):
    for dimName, dimAtts in attItems:
        if '_CoordinateAxisType' in dimAtts.keys() and dimAtts['_CoordinateAxisType'] == 'Time':
            dimAtts['actual_range'] = castTimeRangeAttribute(dimAtts['actual_range'], dimAtts['units'])

def castTimeRangeAttribute(rangenumeric, units):
    return ( num2date(rangenumeric[0], units), num2date(rangenumeric[1], units) )

def boolify(s):
    if s == 'true':
        return True
    if s == 'false':
        return False
    raise ValueError()

def guessCastMetadataAttribute(valuestr):
    for fn in (boolify, int, float):
        try:
            return fn(valuestr)
        except ValueError:
            pass
    return valuestr

def parseSearchResults(dresults):
    _griddap_dsets = []
    _tabledap_dsets = []
    
    for row in dresults['table']['rows']:
        if row[ERDDAP_Search_Results_Rows.GRIDDAP]:
            _griddap_dsets.append(row[ERDDAP_Search_Results_Rows.DATASETID])
        elif row[ERDDAP_Search_Results_Rows.TABLEDAP]:
            _tabledap_dsets.append(row[ERDDAP_Search_Results_Rows.DATASETID])

    return _griddap_dsets, _tabledap_dsets


def parseConstraintValue(value):
    """
     This functions detect the constraint value type and decide if is a 
     regular string and if so, put quotes "" around it. 
     Detect if the constraint value is either: 
      String value         : Return the string inside quotes "<value>"
      <python.datetime>    : Convert to string date with format ISO 8601
      Valid ISO 8601 Date  : Return the string date
      Valid time operation : Return the string operation
      Valid variable 
      operation            : Return the string operation
    """
    if isinstance(value, str):    
        if validate_iso8601(value):
            return value 
        if validate_constraint_time_operations(value):
            return value
        if validate_constraint_var_operations(value):
            return value
        else:
            return '"{}"'.format(value)
    elif isinstance(value,dt.datetime):
        return parseConstraintPyDatetime(value)
    else:
        return str(value)

def parseConstraintDateTime(dtvalue):
    if isinstance(dtvalue,dt.datetime):
        return parseConstraintPyDatetime(dtvalue)
    elif isinstance(dtvalue, str):
        return dtvalue

def parseConstraintPyDatetime(dtvalue):
    return dtvalue.strftime(ERDDAP_DATETIME_FORMAT)

def parse_griddap_resultvariables_slices(resultVariables):
    """
    This method will parse each variable subset in the 
    resultVariables variable. The parsing is done by the
    parse_griddap_resultvariable_slice method.
    It will return a list with the subset components separated
    by dimension subset, with start,stride,stop elements.
    """
    resultVariableStructure=[]
    for resultVariable in resultVariables:
        resultVariableStructure.append( parse_griddap_resultvariable_slice(resultVariable) )

    return resultVariableStructure

def parse_griddap_resultvariable_slice(resultVariable):
    """
    This method will parse the ERDDAP griddap variable subset,
    It'll try to detect if the query is using the opendap extended 
    format of subsetting. 
    When using iso8601 dates, latitude, longitude values or keyword
    last, last-n , all of them between ( )
    This method returns a list with the subset components for each 
    dimensions. Each of this elements will have a dict with: 
    'start', 'stride', 'stop' slice components.
    """
    variableName, variableSlices = "", ""
    variableNameSearch = re.search(GROUP_GRIDDAP_VARIABLE, resultVariable)
    if variableNameSearch:
        variableName = variableNameSearch.group(0)
    variableSlicesSearch = re.findall(GROUP_GRIDDAP_SLICE, resultVariable)
    if variableSlicesSearch:
        variableSlices = variableSlicesSearch

    # print ("variableName: ", variableName)
    # print ("variableSlices: ", variableSlices)
    sliceStructure = { 'variableName' : variableName, 'sliceComponents' : []  }
    for slice in variableSlices:
        sliceStructure['sliceComponents'].append( parse_griddap_slice_element(slice) )

    return sliceStructure

def parse_griddap_slice_element(slice):
    """
    This will parse slice string, that might come as the form
    [(2002-06-01T09:00:00Z)] , [(-89.99):1000:(89.99)] ,  [0:10:100] , [0]
    it will return the start, stride and stop elements of the slice
    """    
    slicetrim = slice.replace('[','').replace(']','')
    sliceElementsSearch = re.findall(GROUP_GRIDDAP_SLICE_ELEMENT, slicetrim)
    
    if sliceElementsSearch:
        #sliceelements = sliceElementsSearch
        if len(sliceElementsSearch) == 1:
            sliceelements = { 'start' :  sliceElementsSearch[0] }
        elif len(sliceElementsSearch) == 2:
            sliceelements = { 'start' :  sliceElementsSearch[0], 'stop' :  sliceElementsSearch[1] }
        elif len(sliceElementsSearch) == 3:
            sliceelements = { 'start' :  sliceElementsSearch[0], 'stride' :  sliceElementsSearch[1], 'stop' :  sliceElementsSearch[2] }
        else:
            raise Exception('Slice is malformed, could not parse : {}'.format(slice))

        # print ("slice Elements: ", sliceelements)
        return sliceelements

def is_slice_element_opendap_extended(sliceElement):
    match_opendapextended = re.compile(SLICE_EXTENDED_DAP_FORMAT).match
    return validateRegex(sliceElement, match_opendapextended)

def get_value_from_opendap_extended_slice_element(sliceElement):
    return sliceElement.replace('(','').replace(')','')

def iso8601STRtoDT(iso8601string):
    # return dt.datetime.strptime(iso8601string, ERDDAP_DATETIME_FORMAT)
    # Using dateutil parse method
    return parse(iso8601string)

def iso8601STRtoNum(iso8601string):
    return date2num(iso8601STRtoDT(iso8601string),ERDDAP_TIME_UNITS)

def numtodate(numdate):
    return num2date(numdate, ERDDAP_TIME_UNITS)

def dttonum(pdt):
    return date2num(pdt, ERDDAP_TIME_UNITS)

# ERDDAP Server URL
ERDDAP_SERVERURL=r'^http.*erddap\/(\w*\.html)$'
# Regular expression validators
ERDDAP_NUMVERSION=r'ERDDAP_version=<?(.*)'
# Match valid ISO8601 Date
DATE_ISO8601_REGEX = r'^\d{4}(-\d\d(-\d\d(T\d\d(:\d\d)?(:\d\d)?(\.\d+)?(([+-]\d\d:\d\d)|Z)?)?)?)?$'
# Match valid time constraint in ERDDAP url querys
CONSTRAINT_TIME_OPERATIONS_REGEX = r'^(max|min)\(\w(\w|\d)*\)((-|\+)\d+(millis|seconds|minutes|hours|days|months|years))?$'
# Match valid int or float constraint in ERDDAP url querys
CONSTRAINT_VAR_OPERATIONS_REGEX = r'^(max|min)\(\w(\w|\d)*\)((-|\+)\d+(.\d+)?)?$' 
VALID_DESTINATION_NAME_VARIABLE = r'^[a-zA-Z](?:\w|_)*$'

# Match the variable name of the query.
# Regex not compatible with destinationNames in ERDDAP before version 1.10
GROUP_GRIDDAP_VARIABLE = r'^[a-zA-Z](\w|_)*'

# To match groups of slices [start:stride:stop][start:stride_stop]...[start:stride:stop] 
#GROUP_GRIDDAP_SLICE = r'(\[(\w|\(|\)|-|:|\.)+\])'
GROUP_GRIDDAP_SLICE = r'\[[^\]]*\]'
# Match individual slice elemnents, start, stride and stop
#GROUP_GRIDDAP_SLICE_ELEMENT = r'(\([^\)]*\))|:(\d+):|:(\d+)|(\d+)'
#GROUP_GRIDDAP_SLICE_ELEMENT = r'(?<=:)?((?:\([^\)]*\))|(?:\d+)|(?:\d+)|(?:\d+))(?=:?)'
GROUP_GRIDDAP_SLICE_ELEMENT = r'(?<=:)?((?:\([^\)]*\))|(?:\d+)|(?:last[+-]?\d*))(?=:?)'

# Slice types extended opendap format
SLICE_EXTENDED_DAP_FORMAT = r'\([^\)]*\)'
GROUP_SLICE_ANY_EXTENDED_DAP_FORMAT = r'\([^\)]*\)'
GROUP_SLICE_LATLON_VALUES = r'\([\d|\.|-]*\)'
GROUP_SLICE_TIME_VALUES = r'\([\d|\-|\:|T|Z]*\)'
GROUP_SLICE_LAST_KEYWORD = r'\(last([\d|\+|\-])*\)'
GROUP_SLICE_STRIDE = r'\:(\d*)\:'

# Floating number match
FLOAT_NUMBER_REGEX = r'^[+-]?(?:[0-9]*)?\.[0-9]+$'
# Intenger
INT_NUMBER_REGEX = r'^[+-]?[0-9]+$'
LAST_KEYWORD_REGEX = r'^last(?:[+-](?:[0-9]+)(\.[0-9]+)?)?$'


match_timeoper = re.compile(CONSTRAINT_TIME_OPERATIONS_REGEX).match   
match_iso8601 = re.compile(DATE_ISO8601_REGEX).match
match_varoper = re.compile(CONSTRAINT_VAR_OPERATIONS_REGEX).match   
match_float = re.compile(FLOAT_NUMBER_REGEX).match
match_int = re.compile(INT_NUMBER_REGEX).match
match_last_keyword = re.compile(LAST_KEYWORD_REGEX).match

# https://stackoverflow.com/questions/41129921/validate-an-iso-8601-datetime-string-in-python
# https://stackoverflow.com/questions/12756159/regex-and-iso8601-formatted-datetime
def validate_iso8601(str_val):    
    return validateRegex(str_val, match_iso8601)

def validate_constraint_time_operations(str_val):
    return validateRegex(str_val, match_timeoper)

def validate_constraint_var_operations(str_val):
    return validateRegex(str_val, match_varoper)

def validate_float(str_val):
    return validateRegex(str_val, match_float)

def validate_int(str_val):
    return validateRegex(str_val, match_int)

def validate_last_keyword(str_val):
    return validateRegex(str_val, match_last_keyword)    

def validateRegex(str_val, rematch):
    try:
        if rematch(str_val) is not None:
            return True
    except:
        pass
    return False    

def ifListToCommaSeparatedString(listorstring):
    if type(listorstring) is list:
        return ','.join(listorstring)
    else:
        return listorstring       

def parseNumericVersion(string_version):
    match = re.search(ERDDAP_NUMVERSION, string_version)
    try:
        numversion = float(match.group(1))
    except:
        numversion = 0
    return numversion


def parseERDDAPStatusPage(htmlcode, numversion):
    """
    This function expecto to get the html code of the status.html page, in the parameter `htmlcode`.
    This string is parsed using regular expressions to extract the metrics.  Will get the scalar 
    values and tables in pandas dataframe, all the data is returned in a OrderedDict.
    """

    # Helper functions
    def tryresearchi(sregex, text, group, options=re.MULTILINE):
        return forceint(tryresearch(sregex,text,group,options))

    def tryresearch(sregex, text, group, options=re.MULTILINE):
        match = re.search(sregex, text, options)
        if match:
            try:
                return match.group(group)
            except: 
                return ""
        else:
            return ""

    def forceint(val):
        if val:
            valdigits = filter(str.isdigit, val)
            if valdigits:
                return int(''.join(valdigits))
            else:
                return None
        else: 
            return None
    ####
    
    parsedStatus = OrderedDict()
    pre = re.search(r'(?<=<pre>)(.*)(?=<\/pre>)', htmlcode, re.DOTALL)
    if pre is None:
        return parsedStatus
    statusText = pre.group(1)
    parsedStatus['current-time'] = iso8601STRtoDT(tryresearch(r'^Current time is\s*(.*)', statusText, 1))
    parsedStatus['startup-time'] = iso8601STRtoDT(tryresearch(r'^Startup was at\s*(.*)$', statusText, 1))
    parsedStatus['ngriddatasets'] = tryresearchi(r'^nGridDatasets\s*=\s*(.*)$', statusText, 1)
    parsedStatus['ntabledatasets'] = tryresearchi(r'^nTableDatasets\s*=\s*(.*)$', statusText, 1)
    parsedStatus['ntotaldatasets'] = tryresearchi(r'^nTotalDatasets\s*=\s*(.*)$', statusText, 1)
    parsedStatus['ndatasetsfailed2load_sincelast_mld'] = tryresearchi(r'^n Datasets Failed To Load \(in the last major LoadDatasets\)\s*=\s*(\d*)$', statusText,1) 

    # Dataset names that failes to load
    _datasets_failes2load = tryresearch(r'^n Datasets Failed To Load \(in the last major LoadDatasets\) = \d*\n(.*)\(end\)',statusText,1, re.DOTALL | re.MULTILINE)
    _datasets_failes2load = _datasets_failes2load.replace('\n','').strip().split(',')
    _datasets_failes2load = [ dst.strip() for dst in _datasets_failes2load if dst != '' ]
    parsedStatus['datasetsfailed2load_sincelast_mld'] = _datasets_failes2load

    parsedStatus['nresponsefailed_since_lastmld'] = tryresearchi(r'Response Failed\s*Time \(since last major LoadDatasets\)\s*n =\s*(\d*)(?:,\s*median ~=\s*(\d*) ms)?', statusText, 1)
    parsedStatus['nresponsefailed_time_since_lastmld'] = tryresearchi(r'Response Failed\s*Time \(since last major LoadDatasets\)\s*n =\s*(\d*)(?:,\s*median ~=\s*(\d*) ms)?', statusText, 2)
    parsedStatus['nresponsefailed_since_lastdr'] = tryresearchi(r'Response Failed\s*Time \(since last Daily Report\)\s*n =\s*(\d*)(?:,\s*median ~=\s*(\d*) ms)?', statusText, 1)
    parsedStatus['nresponsefailed_time_since_lastdr'] = tryresearchi(r'Response Failed\s*Time \(since last Daily Report\)\s*n =\s*(\d*)(?:,\s*median ~=\s*(\d*) ms)?', statusText, 2)
    parsedStatus['nresponsefailed_since_startup'] = tryresearchi(r'Response Failed\s*Time \(since startup\)\s*n =\s*(\d*)(?:,\s*median ~=\s*(\d*) ms)?', statusText, 1)
    parsedStatus['nresponsefailed_time_since_startup'] = tryresearchi(r'Response Failed\s*Time \(since startup\)\s*n =\s*(\d*)(?:,\s*median ~=\s*(\d*) ms)?', statusText, 2)    

    parsedStatus['nresponsesucceeded_since_lastmld'] = tryresearchi(r'Response Succeeded\s*Time \(since last major LoadDatasets\)\s*n =\s*(\d*)(?:,\s*median ~=\s*(\d*) ms)?', statusText, 1)
    parsedStatus['responsesucceeded_time_since_lastmld'] = tryresearchi(r'Response Succeeded\s*Time \(since last major LoadDatasets\)\s*n =\s*(\d*)(?:,\s*median ~=\s*(\d*) ms)?', statusText, 2)    
    parsedStatus['nresponsesucceeded_since_lastdr'] = tryresearchi(r'Response Succeeded\s*Time \(since last Daily Report\)\s*n =\s*(\d*)(?:,\s*median ~=\s*(\d*) ms)?', statusText, 1)
    parsedStatus['responsesucceeded_time_since_lastdr'] = tryresearchi(r'Response Succeeded\s*Time \(since last Daily Report\)\s*n =\s*(\d*)(?:,\s*median ~=\s*(\d*) ms)?', statusText, 2)  
    parsedStatus['nresponsesucceeded_since_startup'] = tryresearchi(r'Response Succeeded\s*Time \(since startup\)\s*n =\s*(\d*)(?:,\s*median ~=\s*(\d*) ms)?', statusText, 1)
    parsedStatus['responsesucceeded_time_since_startup'] = tryresearchi(r'Response Succeeded\s*Time \(since startup\)\s*n =\s*(\d*)(?:,\s*median ~=\s*(\d*) ms)?', statusText, 2)            

    parsedStatus['ntaskthreadfailed_since_lastdr'] = tryresearchi(r'TaskThread Failed\s* Time \(since last Daily Report\)\s*n =\s*(\d*)(?:,\s*median ~=\s*(\d*) ms)?', statusText, 1)
    parsedStatus['taskthreadfailed_time_since_lastdr'] = tryresearchi(r'TaskThread Failed\s* Time \(since last Daily Report\)\s*n =\s*(\d*)(?:,\s*median ~=\s*(\d*) ms)?', statusText, 2)
    parsedStatus['ntaskthreadfailed_since_startup'] = tryresearchi(r'TaskThread Failed\s* Time \(since startup\)\s*n =\s*(\d*)(?:,\s*median ~=\s*(\d*) ms)?', statusText, 1)
    parsedStatus['taskthreadfailed_time_since_startup'] = tryresearchi(r'TaskThread Failed\s* Time \(since startup\)\s*n =\s*(\d*)(?:,\s*median ~=\s*(\d*) ms)?', statusText, 2)

    parsedStatus['ntaskthreadsucceeded_since_lastdr'] = tryresearchi(r'TaskThread Succeeded Time \(since last Daily Report\)\s*n =\s*(\d*)(?:,\s*median ~=\s*(\d*) ms)?', statusText, 1)
    parsedStatus['taskthreadsucceeded_time_since_lastdr'] = tryresearchi(r'TaskThread Succeeded Time \(since last Daily Report\)\s*n =\s*(\d*)(?:,\s*median ~=\s*(\d*) ms)?', statusText, 2)
    parsedStatus['ntaskthreadsucceeded_since_startup'] = tryresearchi(r'TaskThread Succeeded Time \(since startup\)\s*n =\s*(\d*)(?:,\s*median ~=\s*(\d*) ms)?', statusText, 1)
    parsedStatus['taskthreadsucceeded_time_since_startup'] = tryresearchi(r'TaskThread Succeeded Time \(since startup\)\s*n =\s*(\d*)(?:,\s*median ~=\s*(\d*) ms)?', statusText, 2)

    parsedStatus['nthreads_tomwait'] = tryresearchi(r'^Number of threads: Tomcat-waiting=(\d*), inotify=(\d*), other=(\d*)',statusText,1)
    parsedStatus['nthreads_inotify'] = tryresearchi(r'^Number of threads: Tomcat-waiting=(\d*), inotify=(\d*), other=(\d*)',statusText,2)
    parsedStatus['nthreads_other'] = tryresearchi(r'^Number of threads: Tomcat-waiting=(\d*), inotify=(\d*), other=(\d*)',statusText,3)

    parsedStatus['memoryinuse'] = tryresearchi(r'^MemoryInUse=\s*(\d*) MB \(highWaterMark=\s*(\d*) MB\) \(Xmx ~=\s*(\d*) MB\)', statusText,1)
    parsedStatus['highwatermark'] = tryresearchi(r'^MemoryInUse=\s*(\d*) MB \(highWaterMark=\s*(\d*) MB\) \(Xmx ~=\s*(\d*) MB\)', statusText,2)
    parsedStatus['xmx'] = tryresearchi(r'^MemoryInUse=\s*(\d*) MB \(highWaterMark=\s*(\d*) MB\) \(Xmx ~=\s*(\d*) MB\)', statusText,3)

    # Major LoadDatasets Time Series
    _major_loaddatasets_timeseries = tryresearch(r'Major LoadDatasets Time Series.*Memory \(MB\)\n\s*timestamp.*highWater\n((.|\n)*)(?:Major LoadDatasets Times Distribution \(since last Daily Report\))', statusText,1)
    _major_loaddatasets_timeseries = _major_loaddatasets_timeseries.replace('(','').replace(')','').split('\n')

    _major_loaddatasets_timeseries = [ row.split() for row in _major_loaddatasets_timeseries if row != '' ]
    _major_loaddatasets_timeseries = [ [ iso8601STRtoDT(col) if idx==0 else forceint(col) for idx, col in enumerate(row) ] for row in _major_loaddatasets_timeseries ]
    if numversion >= 2.10:
        mldts_columns = ['timestamp', 'mld_time', 'DL_ntry', 'DL_nfail', 'DL_ntotal', 'R_nsuccess','R_ns_median', 'R_nfailed','R_nf_median','R_memfail','NT_tomwait','NT_notify','NT_other','M_inuse','M_highwater']
    else:
        mldts_columns = ['timestamp', 'mld_time', 'DL_ntry', 'DL_nfail', 'DL_ntotal', 'R_nsuccess','R_ns_median', 'R_nfailed','R_nf_median','NT_tomwait','NT_notify','NT_other','M_inuse','M_highwater']

    _major_loaddatasets_timeseries_df = pd.DataFrame(_major_loaddatasets_timeseries, 
                                                     columns=mldts_columns)
    _major_loaddatasets_timeseries_df.set_index('timestamp',inplace=True)
    parsedStatus['major_loaddatasets_timeseries'] = _major_loaddatasets_timeseries_df

    # Timedistributions Loop
    td_items = [
        { 'key' : 'major_loaddatasets_timedistribution_since_lastdr'   , 'regex' : r'Major LoadDatasets Times Distribution \(since last Daily Report\):\n((.|\n)*)Major LoadDatasets Times Distribution \(since startup\):', 'group' : 1 },
        { 'key' : 'major_loaddatasets_timedistribution_since_startup'  , 'regex' : r'Major LoadDatasets Times Distribution \(since startup\):\n((.|\n)*)Minor LoadDatasets Times Distribution \(since last Daily Report\):', 'group' : 1 },
        { 'key' : 'minor_loaddatasets_timedistribution_since_lastdr'   , 'regex' : r'Minor LoadDatasets Times Distribution \(since last Daily Report\):\n((.|\n)*)Minor LoadDatasets Times Distribution \(since startup\):', 'group' : 1 },
        { 'key' : 'minor_loaddatasets_timedistribution_since_startup'  , 'regex' : r'Minor LoadDatasets Times Distribution \(since startup\):\n((.|\n)*)Response Failed Time Distribution \(since last major LoadDatasets\):', 'group' : 1 },
        { 'key' : 'response_failed_timedistribution_since_lastmld'     , 'regex' : r'Response Failed Time Distribution \(since last major LoadDatasets\):\n((.|\n)*)Response Failed Time Distribution \(since last Daily Report\):', 'group' : 1 },
        { 'key' : 'response_failed_timedistribution_since_lastdr'      , 'regex' : r'Response Failed Time Distribution \(since last Daily Report\):\n((.|\n)*)Response Failed Time Distribution \(since startup\):', 'group' : 1 },
        { 'key' : 'response_failed_timedistribution_since_startup'     , 'regex' : r'Response Failed Time Distribution \(since startup\):\n((.|\n)*)Response Succeeded Time Distribution \(since last major LoadDatasets\):', 'group' : 1 },
        { 'key' : 'response_succeeded_timedistribution_since_lastmld'  , 'regex' : r'Response Succeeded Time Distribution \(since last major LoadDatasets\):\n((.|\n)*)Response Succeeded Time Distribution \(since last Daily Report\):', 'group' : 1 },
        { 'key' : 'response_succeeded_timedistribution_since_lastdr'   , 'regex' : r'Response Succeeded Time Distribution \(since last Daily Report\):\n((.|\n)*)Response Succeeded Time Distribution \(since startup\):', 'group' : 1 },
        { 'key' : 'response_succeeded_timedistribution_since_startup'  , 'regex' : r'Response Succeeded Time Distribution \(since startup\):\n((.|\n)*)TaskThread Failed Time Distribution \(since last Daily Report\):', 'group' : 1 },
        { 'key' : 'taskthread_failed_timedistribution_since_lastdr'    , 'regex' : r'TaskThread Failed Time Distribution \(since last Daily Report\):\n((.|\n)*)TaskThread Failed Time Distribution \(since startup\):', 'group' : 1 },
        { 'key' : 'taskthread_failed_timedistribution_since_startup'   , 'regex' : r'TaskThread Failed Time Distribution \(since startup\):\n((.|\n)*)TaskThread Succeeded Time Distribution \(since last Daily Report\):', 'group' : 1 },
        { 'key' : 'taskthread_succeeded_timedistribution_since_lastdr' , 'regex' : r'TaskThread Succeeded Time Distribution \(since last Daily Report\):\n((.|\n)*)TaskThread Succeeded Time Distribution \(since startup\):', 'group' : 1 },
        { 'key' : 'taskthread_succeeded_timedistribution_since_startup', 'regex' : r'TaskThread Succeeded Time Distribution \(since startup\):\n((.|\n)*)SgtMap topography ', 'group' : 1 },
    ]

    for idx, td_item in enumerate(td_items):
        _td_item = tryresearch(td_item['regex'], statusText, 1)
        _td_item = _td_item.replace('&lt;','<').replace('&gt;','>').split('\n')
        _ntime__td_item = _td_item[0]
        parsedStatus[ 'n_' + td_item['key']] = tryresearchi(r'\s*n =\s*(\d*)(?:,\s*median ~=\s*(\d*) ms)?', _ntime__td_item, 1)
        parsedStatus[ 'nmedian_' + td_item['key']] = tryresearchi(r'\s*n =\s*(\d*)(?:,\s*median ~=\s*(\d*) ms)?', _ntime__td_item, 2)

        _td_item = _td_item[1:]
        _td_item = [ row.split(':') for row in _td_item if row != ''] 
        _td_item = [ [ col if idx==0 else forceint(col) for idx, col in enumerate(row) ] for row in _td_item ]
        _td_item_df = pd.DataFrame(_td_item, columns=['time_distribution', 'n'])
        parsedStatus[td_item['key']] = _td_item_df

    return parsedStatus


    
    