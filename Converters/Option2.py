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

cDBRoot = r'F:\GeoCDB\Option2'

ogr2ogrPath = r'F:\Python36_64\Lib\site-packages\osgeo\ogr2ogr.exe'

#Find all shapefiles, convert to gpkg with ogr2ogr

def translateCDB(cDBRoot):
    '''
    for shapefile in shapeindex.shapeFiles:
        geoPackageFile = cDBRoot + shapefile[0:-3] + "gpkg"
        shapefile = cDBRoot + shapefile;
        subprocess.call([ogr2ogrPath,'-f', 'GPKG',geoPackageFile,shapefile])
        print(shapefile + ' -> ' + geoPackageFile)
    '''
    ogrDriver = ogr.GetDriverByName("GPKG")

    datasourceDict = {}
   
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
        gpkgFile = None
        if(gpkgFileName in datasourceDict.keys()):
            gpkgFile = datasourceDict[gpkgFileName]
        else:
            gpkgFile = ogrDriver.CreateDataSource(gpkgFileName)
            datasourceDict[gpkgFileName] = gpkgFile
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
        #converter.removeShapeFile(shapefile)
    for ds in datasourceDict.values():
        ds = None
    datasourceDict = {}


#translateCDB(cDBRoot)

for shapefile in shapeindex.shapeFiles:
    converter.removeShapeFile(cDBRoot + shapefile)