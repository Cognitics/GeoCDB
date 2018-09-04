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
import shapeindex
import shapemeta
import datetime
import random
#import dbfread

try:
    from osgeo import ogr, osr, gdal
except:
    sys.exit('ERROR: cannot find GDAL/OGR modules')
version_num = int(gdal.VersionInfo('VERSION_NUM'))
print("GDAL Version " + version_num)

if version_num < 2020300:
    sys.exit('ERROR: Python bindings of GDAL 2.2.3 or later required due to GeoPackage performance issues.')

shpDriver = ogr.GetDriverByName("ESRI Shapefile")
gpkgDriver = ogr.GetDriverByName("GPKG")

if(False):
    gdal.UseExceptions()

    shapeMetaData = open('shapemeta.py','w')
    shapeMetaData.write('shapeMetaData = {\n')
    # Gather extents for each shapefile
    shapeExtents = {}
    for shapeFile in shapeindex.shapeFiles:
        # Open the shapefile
        try:
            if(os.path.isfile(shapeFile) and os.path.getsize(shapeFile) > 0):
                dataSource = ogr.Open(shapeFile)
                if(dataSource == None):
                    print("Unable to open " + shapeFile)
                    continue
                layer = dataSource.GetLayer(0)
                if(layer == None):
                    print("Unable to read layer from " + shapeFile)
                    continue
                #envelope = ogr.
                west,east,south,north = layer.GetExtent(True)
                extents = {}
                extents['north'] = north;
                extents['south'] = south;
                extents['east'] = east;
                extents['west'] = west;
                shapeExtents[shapeFile] = extents
                if(west != 0):
                    shapeMetaData.write("r'{}': ".format(shapeFile))
                    shapeMetaData.write("[{},{},{},{}],\n".format(north,south,east,west))
        except Exception:
            pass
    # an empty record just to account for the trailing commas above
    shapeMetaData.write("'' : [0,0,0,0]\n")
    shapeMetaData.write('}')
    shapeMetaData.close()
#D:\CDB\northwest_cdb_part2\Tiles\N48\W125\204_HydrographyNetwork\LC\U0\N48W125_D204_S002_T005_LC09_U0_R0.shp

#(lat/lon) -> geopackage dataset
#filename -> (lat,lon)
geocells = {}
layerMap = {}

# filename -> handle
geopackages = {}


def GetWhereClause(shapeFileName):
     
    base,ext = os.path.splitext(shapeFileName)
    filenameParts = base.split("_")
    datasetCode = filenameParts[1]
    componentSelector1 = filenameParts[2]
    componentSelector2 = filenameParts[3]
    lod = filenameParts[4]
    uref = filenameParts[5]
    rref = filenameParts[6]
    whereClause = "_DATASET_CODE = '{}' AND _COMPONENT_SELECTOR_1 = '{}' AND _COMPONENT_SELECTOR_2 = '{}' AND _LOD='{}' AND _UREF='{}' AND _RREF='{}'".format(datasetCode,componentSelector1,componentSelector2,lod,uref,rref)
    return whereClause

def GetLayerName(shapeFileName,datasetName):
    tableName = ''
    base,ext = os.path.splitext(shapeFileName)
    filenameParts = base.split("_")
    datasetCode = filenameParts[1]
    componentSelector1 = filenameParts[2]
    componentSelector2 = filenameParts[3]
    lod = filenameParts[4]
    uref = filenameParts[5]
    rref = filenameParts[6]
    #Create the layer if it doesn't already exist.
    tableName = datasetName + componentSelector1 + componentSelector2
    return tableName


def getGeoPackageFileNameFromLayer(layer):
    parts = layer.split('\\')
    #print(parts)
    geocell = ""
    for j in range(6):
        if(j!=0):
            geocell = geocell + "\\"
        geocell = geocell + parts[j]
    geocell = geocell + "\\"
    geocell = geocell + parts[4] + '_'
    geocell = geocell + parts[5]
    geocell = geocell + ".gpkg"
    return geocell

def getGeoPackage(layer):
    global opened
    global missing
    global geopackages
    gpkgFileName = getGeoPackageFileNameFromLayer(layer)
    if(gpkgFileName in geopackages.keys()):
        return geopackages[gpkgFileName]
    print("trying to open " + gpkgFileName)
    gdal.SetConfigOption("LIST_ALL_TABLES","NO")
    dataSource = ogr.Open(gpkgFileName)
    print("done with open " + gpkgFileName)
    #dataSource = None
    if(dataSource==None):
        print("Unable to open " + gpkgFileName)                
    geopackages[gpkgFileName] = dataSource
    return geopackages[gpkgFileName]


#if(False):
def TestShapeFiles():
    opened = 0
    missing = 0
    featureCount = 0
    # start a timer
    shapeStart = datetime.datetime.now()
    # repeat len(shapeindex.shapeFiles) times
    for i in range(len(shapeindex.shapeFiles)):
        # randomly find a shape file and open it with gdal
        rndIndex = random.randint(0,len(shapeindex.shapeFiles)-1)
        fullFilePath = shapeindex.shapeFiles[rndIndex]
        dataSource = ogr.Open(fullFilePath)
        if(dataSource==None):
            #print("Unable to open " + fullFilePath)
            missing = missing + 1
            continue
        else:
            opened = opened + 1

        layer = dataSource.GetLayer(0)
        if(layer == None):
            print("Unable to read layer from " + fullFilePath)
            continue
        else:
            #layer.ResetReading()
            feature = layer.GetNextFeature()
            while(feature != None):
                feature = layer.GetNextFeature()
                featureCount = featureCount + 1

    # end the timer, record delta time
    shapeEnd = datetime.datetime.now()
    shapeDelta = shapeEnd - shapeStart
    print("Shapefile elapsed " + str(shapeDelta))
    print("Opened " + str(opened) + " Empty " + str(missing))
    print("Read " + str(featureCount) + " features.")

def TestGeoPackage():
    # Gather up all the geocells from the filenames
    opened = 0
    missing = 0

    featureCount = 0;
    #start a timer
    geoPackageStart = datetime.datetime.now()
    for i in range(len(shapeindex.shapeFiles)):
        # randomly find a shape file and open it with gdal
        rndIndex = random.randint(0,len(shapeindex.shapeFiles)-1)
        fullFilePath = shapeindex.shapeFiles[rndIndex]
        dataSource = getGeoPackage(fullFilePath)
        if(dataSource is not None):
            shapeFilename = os.path.basename(fullFilePath)
            #get the dataset name from the fullFilePath
            pathparts = fullFilePath.split('\\')
            layerName = GetLayerName(shapeFilename,pathparts[6])
            #layerName = layerName[:-4]
            layer = dataSource.GetLayerByName(layerName)
            if(layer == None):
                #print("Unable to open layer: " + layerName)
                missing = missing + 1
            else:
                layer.SetAttributeFilter(GetWhereClause(shapeFilename))
                #layer.ResetReading()
                feature = layer.GetNextFeature()
                while(feature != None):
                    feature = layer.GetNextFeature()
                    featureCount = featureCount + 1
                opened = opened + 1
        missing = missing + 1
    #for record in DBF('people.dbf'):
    geoPackageEnd = datetime.datetime.now()
    geoPackageDelta = geoPackageEnd - geoPackageStart
    print("GeoPackage elapsed " + str(geoPackageDelta))
    print("Opened " + str(opened) + " Empty " + str(missing))
    #print("Opened " + str(opened) + " Empty " + str(missing))
    print("Read " + str(featureCount) + " features.")

TestShapeFiles()

TestGeoPackage()

