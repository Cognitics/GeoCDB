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
import datetime
import random
import sqlite3

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


layerCounts = [1,10,50,100,500,1000,5000,10000,50000,100000]

ogrDriver = ogr.GetDriverByName("GPKG")
'''
for i in layerCounts:
    gpkgFileName = "testFile_" + str(i) + ".gpkg"
    gpkgFile = ogrDriver.CreateDataSource(gpkgFileName)
    for j in range(i):
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(4326)
        outLayerName = "layer_" + str(j)
        outLayer = gpkgFile.CreateLayer(outLayerName,srs,geom_type=ogr.wkbPolygon)
        idField = ogr.FieldDefn("id", ogr.OFTInteger)
        outLayer.CreateField(idField)
'''

'''
# GDAL Open Timing
for i in layerCounts:
    gpkgFileName = "testFile_" + str(i) + ".gpkg"
    #print("Opening " + gpkgFileName)
    geoPackageStart = datetime.datetime.now()
    dataSource = ogr.Open(gpkgFileName)
    if(dataSource == None):
        print("Unable to open " + gpkgFileName)
        continue
    #count layers
    layerCount = dataSource.GetLayerCount()
    del dataSource
    
    geoPackageEnd = datetime.datetime.now()
    geoPackageDelta = geoPackageEnd - geoPackageStart
    print(str(i) + "," + str(geoPackageDelta.total_seconds()))
    #print("Closed " + filePath)

    '''


'''
#SQLite Open Timing


for i in layerCounts:
    gpkgFileName = "testFile_" + str(i) + ".gpkg"
    #print("Opening " + gpkgFileName)
    geoPackageStart = datetime.datetime.now()
    sqliteCon = sqlite3.connect(gpkgFileName)
    if(sqliteCon == None):
        print("Unable to open " + gpkgFileName)
        continue
    #count layers
    layerSQL = "SELECT COUNT(*) as LayerCount from gpkg_geometry_columns;"
    layerCursor = sqliteCon.cursor()
    layerCursor.execute(layerSQL)
    rows = layerCursor.fetchall()
    layerCount = 0
    if(len(rows) > 0):
        layerCount = rows[0][0]    
    del layerSQL    
    geoPackageEnd = datetime.datetime.now()
    geoPackageDelta = geoPackageEnd - geoPackageStart
    print(str(i) + "," + str(geoPackageDelta.total_seconds()))
    #print("Closed " + filePath)

 '''

 # Total GeoPackage Count and Average Layers per GeoPackage