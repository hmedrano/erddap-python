# Package history

## Version new

- Bug fix: The search method could not receive a phrase to search, using double quotes in phrase, i.e. "phrase to search"
- Refactored tabs for spaces, 4 spaces per tab.
- Added `orderBySum` filter to the tabledap class, available in ERDDAP v2.16 and up.

## Version 1.0.0

- Releasing a stable version of erddap-python, growing community backed.
- Added slicing capabilities to ERDDAP_Griddap_Dimension classes.
- Added special methods and properties to ERDDAP_Griddap_Dimension type 'time'
- Validation of opendap request of griddap datasets.
- Added a new way to request griddap subsets using regular slice objects, using integer indexing or real dimensions values, The methods `setSubsetI`, `setSubset`.

## Version 0.0.10b

- Bug fix: MLD timeseries parsing for ERDDAP version 2.12 wasn't working.

## Version 0.0.9b

- Added parse status support for ERDDAP version 2.12, new metrics: nunique_users_since_startup. New columns for MLD timeseries: R_toomany and open_files_percent.
- Included `__version__` number property in erddapClient class

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