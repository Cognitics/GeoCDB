'''
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
'''
import os
import sys
import subprocess

import converter
try:
    from osgeo import ogr, osr, gdal
except:
    sys.exit('ERROR: cannot find GDAL/OGR modules')
from dbfread import DBF
import sqlite3

version_num = int(gdal.VersionInfo('VERSION_NUM'))
print("GDAL Version " + str(version_num))

if version_num < 2020300:
    sys.exit('ERROR: Python bindings of GDAL 2.2.3 or later required due to GeoPackage performance issues.')

#Find all shapefiles, convert to gpkg with ogr2ogr

def translateCDB(cDBRoot,ogrPath, removeShapefile):
    sys.path.append(cDBRoot)
    import shapeindex

    for shapefile in shapeindex.shapeFiles:
        geoPackageFile = shapefile[0:-3] + "gpkg"
        if(os.path.getsize(shapefile)>0):
            #'-t_srs', 'EPSG:4326', '-s_srs', 'EPSG:4326', 
            subprocess.call([ogrPath,'-f', 'GPKG', geoPackageFile,shapefile])
            print(shapefile + ' -> ' + geoPackageFile)
        if(removeShapefile):
            converter.removeShapeFile(shapefile)


if(len(sys.argv) != 3):
    print("Usage: Option1d.py <Input Root CDB Directory> <Output Directory for GeoPackage Files>")
    exit()

cDBRoot = sys.argv[1]
outputDirectory = sys.argv[2]

#generate a list of all the shapefiles.
import generateMetaFiles
generateMetaFiles.generateMetaFiles(cDBRoot)

