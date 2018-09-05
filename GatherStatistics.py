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
#import shapeindex
#import shapemeta
import datetime
import random
#import dbfread

try:
    from osgeo import ogr, osr, gdal
except:
    sys.exit('ERROR: cannot find GDAL/OGR modules')
version_num = int(gdal.VersionInfo('VERSION_NUM'))
print("GDAL Version " + str(version_num))

if version_num < 2020300:
    sys.exit('ERROR: Python bindings of GDAL 2.2.3 or later required due to GeoPackage performance issues.')

shpDriver = ogr.GetDriverByName("ESRI Shapefile")
gpkgDriver = ogr.GetDriverByName("GPKG")

#randomize indexes into array
#for each entry

#Plot layer count vs. open time across all options

# Open all GeoPackage files
#min/max/stddev for open times
#total time


def gatherGeoPackageStats(cDBRoot):
    totalLayerCount = 0

    geoPackageStats = []
    for root, dirs, files in os.walk(cDBRoot):
        path = root.split(os.sep)
        hasShapeFile = False
        for file in files:
            base,ext = os.path.splitext(file)
            filePath = os.path.join(root,file)
            if(ext==".gpkg"):
                #start timer
                geoPackageStart = datetime.datetime.now()
                #open dataset
                try:
                    #print("Opening " + filePath)
                    dataSource = ogr.Open(filePath)
                    if(dataSource == None):
                        print("Unable to open " + filePath)
                        continue
                    #count layers
                    layerCount = dataSource.GetLayerCount()
                    totalLayerCount = totalLayerCount + layerCount
                    del dataSource
                    #print("Closed " + filePath)
                    geoPackageEnd = datetime.datetime.now()
                    geoPackageDelta = geoPackageEnd - geoPackageStart
                    stat = [str(filePath),str(layerCount),str(geoPackageDelta.total_seconds())]
                    geoPackageStats.append(stat)
                except Exception:
                        pass

    return len(geoPackageStats),totalLayerCount
'''
    geoPackageStats.sort()
    #write a csv file
    gpkgStats = open("geopackageStats.csv",'w')
    gpkgStats.write('layer_count,file,open_time\n')
    for stat in geoPackageStats:
        gpkgStats.write( str(stat[1]) + "," + stat[0] + "," + str(stat[2]) + "\n")
    gpkgStats.close()
    return geoPackageStats
    '''



#Random layer query
#min/max/stddev for feature count query
#total time

#gatherGeoPackageStats("f:\\GeoCDB\\")
print("Option, Total GeoPackage Files, Average Layers")
numFiles,numLayers = gatherGeoPackageStats("f:\\GeoCDB\\Option1")
print("Option 1, " + numFiles + "," + numLayers / numFiles)
numFiles,numLayers = gatherGeoPackageStats("f:\\GeoCDB\\Option2")
print("Option 2, " + numFiles + "," + numLayers / numFiles)
numFiles,numLayers = gatherGeoPackageStats("f:\\GeoCDB\\Option3")
print("Option 3, " + numFiles + "," + numLayers / numFiles)
numFiles,numLayers = gatherGeoPackageStats("f:\\GeoCDB\\Option4")
print("Option 4, " + numFiles + "," + numLayers / numFiles)