'''
Copyright 2018, US Army Geospatial Center, Leidos Inc., and Cognitics Inc.

Developed as a joint work by The Army Geospatial Center, Leidos Inc., 
and Cognitics Inc. 

Permission is granted to use this code for any purpose as long as this
copyright and permission header remains intact in each source file.
'''
import os
import sys
import subprocess
import shapeindex
import converter
try:
    from osgeo import ogr, osr, gdal
except:
    sys.exit('ERROR: cannot find GDAL/OGR modules')
from dbfread import DBF
import sqlite3

version_num = int(gdal.VersionInfo('VERSION_NUM'))
print(version_num)
if version_num < 1100000:
    sys.exit('ERROR: Python bindings of GDAL 1.10 or later required')

cDBRoot = r'F:\GeoCDB\Option1'

ogr2ogrPath = r'F:\Python36_64\Lib\site-packages\osgeo\ogr2ogr.exe'

#Find all shapefiles, convert to gpkg with ogr2ogr

def translateCDB(cDBRoot):
    for shapefile in shapeindex.shapeFiles:
        geoPackageFile = cDBRoot + shapefile[0:-3] + "gpkg"
        shapefile = cDBRoot + shapefile;
        subprocess.call([ogr2ogrPath,'-f', 'GPKG', '-t_srs', 'EPSG:4326', geoPackageFile,shapefile])
        print(shapefile + ' -> ' + geoPackageFile)
        converter.removeShapeFile(shapefile)




translateCDB(cDBRoot)