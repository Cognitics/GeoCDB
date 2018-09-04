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
        geoPackageFile = cDBRoot + shapefile[0:-3] + "gpkg"
        shapefile = cDBRoot + shapefile;
        subprocess.call([ogrPath,'-f', 'GPKG', '-t_srs', 'EPSG:4326', geoPackageFile,shapefile])
        print(shapefile + ' -> ' + geoPackageFile)
        if(removeShapefile):
            converter.removeShapeFile(shapefile)


if(len(sys.argv) != 3  and len(sys.argv) != 4):
    print("Usage: Option1.py <Root CDB Directory> <Path to ogr2ogr executable> [remove-shapefiles]")
    print("Example:")
    print("Option1.py F:\GeoCDB\Option1 F:\Python36_64\Lib\site-packages\osgeo\ogr2ogr.exe")
    print("\n-or-\n")
    print("Option1.py F:\GeoCDB\Option1 F:\Python36_64\Lib\site-packages\osgeo\ogr2ogr.exe remove-shapefiles")
    exit()
cDBRoot = sys.argv[1]
ogr2ogrPath = sys.argv[2]
removeShapefile = False
if((len(sys.argv)==4) and sys.argv[3]=="remove-shapefiles"):
    removeShapefile = True

sys.path.append(cDBRoot)
if((cDBRoot[-1:]!='\\') and (cDBRoot[-1:]!='/')):
    cDBRoot = cDBRoot + '/'
import generateMetaFiles
generateMetaFiles.generateMetaFiles(cDBRoot)
translateCDB(cDBRoot, ogr2ogrPath, removeShapefile)