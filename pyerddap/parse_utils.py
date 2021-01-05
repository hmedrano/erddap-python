

class ERDDAP_Metadata_Rows:
    ROW_TYPE       = 0
    VARIABLE_NAME  = 1
    ATTRIBUTE_NAME = 2
    DATA_TYPE      = 3
    VALUE          = 4


def parseDictMetadata(dmetadata):
    """
     This function parses the metadata json response from a erddap dataset
     This function receives a python dictionary created with the metadata response from a erddap dataset,
     It parses this dictionary and creates two new dictionarys, one with all the metatada, and another
     one with the variables and its attributes
    """ 
    _variables={}
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
        _metadata.append(drow)

    return _metadata, _variables


def parseMetadataAttribute(data_type, valuestr):

    if data_type != 'String' and ',' in valuestr:
        _lvaluestr = valuestr.split(',')
    elif data_type == 'String':
        return valuestr
    else:
        _lvaluestr = [valuestr]

    if data_type in ['float', 'double']:
        _castedvalue =  [float(v) for v in _lvaluestr] 
    elif data_type in ['short', 'int', 'byte', 'char', 'short', 'long']:
        _castedvalue =  [int(v) for v in _lvaluestr] 

    if len(_castedvalue) == 1:
        return _castedvalue[0]
    else:
        return _castedvalue