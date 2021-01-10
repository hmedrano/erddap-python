

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

