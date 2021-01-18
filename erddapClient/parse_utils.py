import re
import datetime as dt



class ERDDAP_Metadata_Rows:
    ROW_TYPE       = 0
    VARIABLE_NAME  = 1
    ATTRIBUTE_NAME = 2
    DATA_TYPE      = 3
    VALUE          = 4

class ERDDAP_Search_Results_Rows:
    GRIDDAP     = 0
    SUBSET      = 1
    TABLEDAP    = 2
    MAKEAGRAPH  = 3
    WMS         = 4
    FILES       = 5
    ACCESIBLE   = 6
    TITLE       = 7
    SUMMARY     = 8
    FGDC        = 9
    ISO19115    = 10
    INFO        = 11
    BACKINFO    = 12
    RSS         = 13
    EMAIL       = 14
    INSTITUTION = 15
    DATASETID   = 16


def parseDictMetadata(dmetadata):
    """
     This function parses the metadata json response from a erddap dataset
     This function receives a python dictionary created with the metadata response from a erddap dataset,
     It parses this dictionary and creates two new dictionarys, one with all the metatada, and another
     one with the variables and its attributes
    """ 
    _variables={}
    _global={}
    _metadata=[] 
    for row in dmetadata['table']['rows']:
        drow = dict(zip(dmetadata['table']['columnNames'],row))
        if row[ERDDAP_Metadata_Rows.VARIABLE_NAME] != 'NC_GLOBAL':
            if row[ERDDAP_Metadata_Rows.VARIABLE_NAME] in _variables:
                _variables[row[ERDDAP_Metadata_Rows.VARIABLE_NAME]][row[ERDDAP_Metadata_Rows.ATTRIBUTE_NAME]] = \
                    parseMetadataAttribute(row[ERDDAP_Metadata_Rows.DATA_TYPE], row[ERDDAP_Metadata_Rows.VALUE])
            else:
                _variables[row[ERDDAP_Metadata_Rows.VARIABLE_NAME]] = {} 
                _variables[row[ERDDAP_Metadata_Rows.VARIABLE_NAME]]['data_type'] = row[ERDDAP_Metadata_Rows.DATA_TYPE]
        else: # Global attributes
            _global[row[ERDDAP_Metadata_Rows.ATTRIBUTE_NAME]] = parseMetadataAttribute(row[ERDDAP_Metadata_Rows.DATA_TYPE], row[ERDDAP_Metadata_Rows.VALUE])
        _metadata.append(drow)

    return _metadata, _variables, _global


def parseMetadataAttribute(data_type, valuestr):

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


#DATE_ISO8601_REGEX = r'^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$'

# Regular expression validators
DATE_ISO8601_REGEX = r'^\d{4}(-\d\d(-\d\d(T\d\d(:\d\d)?(:\d\d)?(\.\d+)?(([+-]\d\d:\d\d)|Z)?)?)?)?$'
CONSTRAINT_TIME_OPERATIONS_REGEX = r'^(max|min)\(\w(\w|\d)*\)((-|\+)\d+(millis|seconds|minutes|hours|days|months|years))?$'
CONSTRAINT_VAR_OPERATIONS_REGEX = r'^(max|min)\(\w(\w|\d)*\)((-|\+)\d+(.\d+)?)?$' 

match_timeoper = re.compile(CONSTRAINT_TIME_OPERATIONS_REGEX).match   
match_iso8601 = re.compile(DATE_ISO8601_REGEX).match
match_varoper = re.compile(CONSTRAINT_VAR_OPERATIONS_REGEX).match   

# https://stackoverflow.com/questions/41129921/validate-an-iso-8601-datetime-string-in-python
# https://stackoverflow.com/questions/12756159/regex-and-iso8601-formatted-datetime
def validate_iso8601(str_val):    
    return validateRegex(str_val, match_iso8601)

def validate_constraint_time_operations(str_val):
    return validateRegex(str_val, match_timeoper)

def validate_constraint_var_operations(str_val):
    return validateRegex(str_val, match_varoper)

def validateRegex(str_val, rematch):
    try:
        if rematch(str_val) is not None:
            return True
    except:
        pass
    return False    