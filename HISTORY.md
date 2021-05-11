# Package history

## Version 0.0.8b

- Added methods to parse ERDDAP status.html page, results are stored in DataFrames and scalars. Method is available in erddapClient.ERDDAP_Server.parseStatusPage()
- Bug fix method setConstraints()

## Version 0.0.7b

- Added the methods getxArray and getncDataset that can get subsets of ERDDAP griddap datasets and return xarray or netCDF4.Dataset objects
- Parsing methods for griddap querys of extended opendap format, to integer indexes equivalents.

## Version 0.0.6b

- Removed os.path.join usage to build url strings, that caused the search operations to fail on windows.
- Added test on windows os.

## Version 0.0.5b

- pip package issues fix.

## Version 0.0.4b

- Relocation of getDataFrame method, to base class erddap_dataset, this can be used by griddap_dataset also.

## Version 0.0.3b

- Refactor of private methods
- Improved docstring using pdoc
- Published API reference in [https://hmedrano.github.io/erddap-python/](https://hmedrano.github.io/erddap-python/)

## Version 0.0.2b

- Pytests
- First pip package