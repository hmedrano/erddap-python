

MAX_SUMMARY_LEN = 75

def simple_dataset_repr(ds):
    summary = ["<pyerddap.{}>".format(type(ds).__name__)]
    dstTitle = ds.getAttribute('title')
    truncatedTitle = (dstTitle[:MAX_SUMMARY_LEN] + '..') if len(dstTitle) > MAX_SUMMARY_LEN else dstTitle
    summary.append("\"{}\"".format(truncatedTitle))
    return ' '.join(summary)

def dataset_repr(ds):
    summary = ["<pyerddap.{}>".format(type(ds).__name__)]
    summary.append("Title:       {}".format(ds.getAttribute('title')))
    summary.append("Server URL:  {}".format(ds.erddapurl))
    summary.append("Dataset ID:  {}".format(ds.datasetid))
    summary.append("Variables: ")
    for variableName, variableAttributes in ds.variables.items():
        summary.append("  {} ({}) ".format(variableName, variableAttributes['data_type']) )
        if 'standard_name' in variableAttributes:
            summary.append("    Standard name: {} ".format(variableAttributes['standard_name']) )
        if 'units' in variableAttributes:
            summary.append("    Units:         {} ".format(variableAttributes['units']) )


    return "\n".join(summary)


def erddap_search_results_repr(srobj):
    summary = ["<pyerddap.{}>".format(type(srobj).__name__)]
    summary.append ("Results:  {}".format(len(list(srobj))))
    summary.append('[')
    for item in list(srobj):
        summary.append( " " + item.__simple_repr__() )
    summary.append(']')
    return '\n'.join(summary)    