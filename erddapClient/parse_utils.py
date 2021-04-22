import re
import datetime as dt
from netCDF4 import num2date
from erddapClient.erddap_constants import ERDDAP_Metadata_Rows, ERDDAP_Search_Results_Rows, ERDDAP_TIME_UNITS
from collections import OrderedDict

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
     Sample: nValues=16, evenlySpaced=false, averageSpacing=91 days 6h 24m 0s
    """
    dimensionAttributes = {}
    elements = value.split(',')
    for e in elements:
        k,v = e.split('=')
        dimensionAttributes['_' + k.strip()] = guessCastMetadataAttribute(v.strip())
    return dimensionAttributes


def castMetadataAttribute(data_type, valuestr):

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
    return dtvalue.strftime("%Y-%m-%dT%H:%M:%SZ")

def parse_griddap_resultvariables_slices(resultVariables):
    """
    This method will parse the ERDDAP griddap variable slicing,
    Detect if using the opendap extended format of slicing, like
    using, iso8601 dates, latitude, longitude values or keyword
    last, last-n
    """
    resultVariableStructure=[]
    for resultVariable in resultVariables:
        resultVariableStructure.append( parse_griddap_resultvariable_slice(resultVariable) )

    return resultVariableStructure

def parse_griddap_resultvariable_slice(resultVariable):
    """

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

        # print ("slice Elements: ", sliceelements)
        return sliceelements

def is_slice_element_opendap_extended(sliceElement):
    match_opendapextended = re.compile(SLICE_EXTENDED_DAP_FORMAT).match
    return validateRegex(sliceElement, match_opendapextended)

def get_value_from_opendap_extended_slice_element(sliceElement):
    return sliceElement.replace('(','').replace(')','')

def iso8601todt(iso8601string):
    # Consider all types of valid 8601 iso date formats
    return dt.datetime.strptime(iso8601string, "%Y-%m-%dT%H:%M:%SZ")

# Regular expression validators
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
GROUP_GRIDDAP_SLICE_ELEMENT = r'(?<=:)?((?:\([^\)]*\))|(?:\d+)|(?:\d+)|(?:\d+)|(?:last[+-]?\d*))(?=:?)'

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