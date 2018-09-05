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


def translateCDB(cDBRoot, removeShapefile):

    sys.path.append(cDBRoot)
    import shapeindex

    ogrDriver = ogr.GetDriverByName("GPKG")

    gpkgFileName = cDBRoot + "CDB.gpkg"
    gpkgFile = None
    for shapefile in shapeindex.shapeFiles:
        
        fileparts = shapefile.split('\\')
        subdir = cDBRoot
        for i in range(len(fileparts)-6):
            if(i==0):
                subdir + fileparts[i]
            else:
                subdir = subdir + "\\" + fileparts[i]
        lat = fileparts[-6]
        lon = fileparts[-5]
        dataset = fileparts[-4]
        gpkgFileName = subdir + "\\" + lat + "\\" + lon + "\\" + dataset + ".gpkg"
        #dataset
        
        if(gpkgFile == None):
            gpkgFile = ogrDriver.CreateDataSource(gpkgFileName)
        if(gpkgFile == None):
            print("Unable to create " + gpkgFileName)
            continue
        shapefile = cDBRoot + shapefile
        dataSource = ogr.Open(shapefile)
        if(dataSource==None):
            print("Unable to open " + shapefile)
            continue
        layer = dataSource.GetLayer(0)
        if(layer == None):
            print("Unable to read layer from " + shapefile)
            continue
        #print(shapefile)
        print(shapefile + ' -> ' + gpkgFileName)
        layerDefinition = layer.GetLayerDefn()
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(4326)

        #Get the shapefile filename, then get everything except the last 4 bytes ('.shp')
        outLayerName = fileparts[-1][0:-4]

        outLayer = gpkgFile.CreateLayer(outLayerName,srs,geom_type=layerDefinition.GetGeomType())
        outLayer.StartTransaction()
        # Add fields
        for i in range(layerDefinition.GetFieldCount()):
            fieldName =  layerDefinition.GetFieldDefn(i).GetName()
            fieldTypeCode = layerDefinition.GetFieldDefn(i).GetType()
            fieldType = layerDefinition.GetFieldDefn(i).GetFieldTypeName(fieldTypeCode)
            fieldWidth = layerDefinition.GetFieldDefn(i).GetWidth()
            GetPrecision = layerDefinition.GetFieldDefn(i).GetPrecision()
            fieldDef = ogr.FieldDefn(fieldName,fieldTypeCode)
            outLayer.CreateField(fieldDef)
        layer.ResetReading()
        featureCount = 0
        inFeature = layer.GetNextFeature()
        while inFeature is not None:
            featureCount += 1
            outFeature = ogr.Feature(outLayer.GetLayerDefn())
            inGeometry = inFeature.GetGeometryRef()
            outFeature.SetGeometry(inGeometry)
            # set the output features to match the input features
            for i in range(layerDefinition.GetFieldCount()):
                fieldName = layerDefinition.GetFieldDefn(i).GetNameRef()
                outFeature.SetField(fieldName,inFeature.GetField(i))
            #write the feature
            outLayer.CreateFeature(outFeature)
            outFeature = None
            inFeature = layer.GetNextFeature()
        outLayer.CommitTransaction()
        print("Translated " + str(featureCount) + " features.")
        dataSource = None
        if(removeShapefile):
            converter.removeShapeFile(shapefile)
    for ds in datasourceDict.values():
        ds = None
    datasourceDict = {}


if(len(sys.argv) != 2  and len(sys.argv) != 3):
    print("Usage: Option2.py <Root CDB Directory> [remove-shapefiles]")
    print("Example:")
    print("Option2.py F:\GeoCDB\Option2")
    print("\n-or-\n")
    print("Option2.py F:\GeoCDB\Option2 remove-shapefiles")
    exit()
cDBRoot = sys.argv[1]
removeShapefile = False
if((len(sys.argv)==3) and sys.argv[2]=="remove-shapefiles"):
    removeShapefile = True

sys.path.append(cDBRoot)
if((cDBRoot[-1:]!='\\') and (cDBRoot[-1:]!='/')):
    cDBRoot = cDBRoot + '/'
import generateMetaFiles
generateMetaFiles.generateMetaFiles(cDBRoot)
translateCDB(cDBRoot,removeShapefile)
