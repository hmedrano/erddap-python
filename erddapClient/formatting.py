

MAX_SUMMARY_LEN = 75

def erddap_server_repr(sobj):
    summary = ["<erddapClient.{}>".format(type(sobj).__name__)]
    summary.append("Server version:  {}".format(sobj.version))
    # summary.append("Server version_string:  {}".format(sobj.version_string))
    return "\n".join(summary)


def simple_dataset_repr(ds):
    summary = ["<erddapClient.{}>".format(type(ds).__name__)]
    dstTitle = ds.getAttribute('title')
    truncatedTitle = (dstTitle[:MAX_SUMMARY_LEN] + '..') if len(dstTitle) > MAX_SUMMARY_LEN else dstTitle
    summary.append("\"{}\"".format(truncatedTitle))
    return ' '.join(summary)


def dataset_str(ds):
    summary = ["<erddapClient.{}>".format(type(ds).__name__)]
    summary.append("Title:       {}".format(ds.getAttribute('title')))
    summary.append("Server URL:  {}".format(ds.erddapurl))
    summary.append("Dataset ID:  {}".format(ds.datasetid))
    return "\n".join(summary)


def tabledap_str(ds):
    summary = [ "" ] 
    if hasattr(ds,'lastRequestURL'):
        summary.append("Generated URL: " + ds.lastRequestURL)
    summary.append("Variables: ")
    for variableName, variableAttributes in ds.variables.items():
        summary.append("  {} ({}) ".format(variableName, variableAttributes['_dataType']) )
        if 'standard_name' in variableAttributes:
            summary.append("    Standard name: {} ".format(variableAttributes['standard_name']) )
        if 'units' in variableAttributes:
            summary.append("    Units:         {} ".format(variableAttributes['units']) )

    return "\n".join(summary)


def griddap_str(ds):
    summary = [ "", "Dimensions: " ]
    for dimensionName, dimensionAttributes in ds.dimensions.items():
        summary.append("  {} ({}) range={} ".format(dimensionName, dimensionAttributes['_dataType'], dimensionAttributes['actual_range']) )
        if 'standard_name' in dimensionAttributes:
            summary.append("    Standard name: {} ".format(dimensionAttributes['standard_name']) )
        if 'units' in dimensionAttributes:
            summary.append("    Units:         {} ".format(dimensionAttributes['units']) )

    summary.append("Variables: ")    
    for variableName, variableAttributes in ds.variables.items():
        summary.append("  {} ({}) ".format(variableName, variableAttributes['_dataType']) )
        if 'standard_name' in variableAttributes:
            summary.append("    Standard name: {} ".format(variableAttributes['standard_name']) )
        if 'units' in variableAttributes:
            summary.append("    Units:         {} ".format(variableAttributes['units']) )

    return "\n".join(summary)


def erddap_search_results_repr(srobj):
    summary = ["<erddapClient.{}>".format(type(srobj).__name__)]
    summary.append ("Results:  {}".format(len(list(srobj))))
    summary.append('[')
    for idx, item in enumerate(list(srobj)):
        summary.append( "  {}".format(idx) + " - <erddapClient.{}>".format(type(item.dataset).__name__) + \
                        " " + item.datasetid + " , \"" + item.title + "\"")
    summary.append(']')
    return '\n'.join(summary)    