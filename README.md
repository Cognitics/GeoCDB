# GeoCDB
Experimental Code for Conversion and Profiling the Proposed Implementation of [GeoPackage](http://www.geopackage.org) in the [Open Geospatial Consortium (OGC)](http://www.opengeospatial.org/) [CDB Standard](http://www.opengeospatial.org/standards/cdb)


## Warning:

This code will modify an existing CDB repository by adding GeoPackage files and
removing ShapeFiles. **This will permanently alter the CDB database**.

This software code is experimental and may not work as expected. Backup your CDB and 
_use at your own risk_.

Please contact kbentley@cognitics.net with any questions, comments, pull requests,
etc.

## Converter Procedure

* Software Installations
  * Download and install python 3.7 (I think the script was tested with 3.6, but 3.7 has worked good)
    * https://www.python.org/ftp/python/3.7.2/python-3.7.2-amd64.exe
  * Download and unzip GDAL executable somewhere on disk (if you don’t already have it)
    * http://download.gisinternals.com/sdk/downloads/release-1900-x64-gdal-2-4-0-mapserver-7-2-2.zip
  * Download and install the GDAL python package
    * http://download.gisinternals.com/sdk/downloads/release-1900-x64-gdal-2-4-0-mapserver-7-2-2/GDAL-2.4.0.win-amd64-py3.7.msi
  * Download and install the dbfread python library
    * https://files.pythonhosted.org/packages/4c/94/51349e43503e30ed7b4ecfe68a8809cdb58f722c0feb79d18b1f1e36fe74/dbfread-2.0.7-py2.py3-none-any.whl
    * python -m pip install _pathToDownloadedFileAbove_
  * There is probably easier ways to install these python packages, but our work internet breaks the easier methods that auto download and install
* Running the converter
  * Add the GDAL bin directory in the path (first, in case other programs have older versions of GDAL)
    * set PATH=_gdalBinDir_;%PATH%
    * set GDAL_DATA=_gdalBinDir_\gdal-data
* Run the conversion
  * pathToConverters\Option1d.py _PathToInputCDB_ _PathToOutputCDB_

---
Copyright 2018, US Army Geospatial Center, Leidos Inc., and Cognitics Inc.

Developed as a joint work by The Army Geospatial Center, Leidos Inc., 
and Cognitics Inc. 

Permission is hereby granted, free of charge, to any person obtaining a copy of 
this software and associated documentation files (the "Software"), to deal in 
the Software without restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the 
Software, and to permit persons to whom the Software is furnished to do so, subject 
to the following conditions:

The above copyright notice and this permission notice shall be included in all 
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A 
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT 
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION 
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE 
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.



