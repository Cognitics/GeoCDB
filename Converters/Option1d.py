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
from dbfconvert import DBF

try:
    from osgeo import ogr, osr, gdal
except:
    sys.exit('ERROR: cannot find GDAL/OGR modules')

import sqlite3

version_num = int(gdal.VersionInfo('VERSION_NUM'))
print("GDAL Version " + str(version_num))

if version_num < 2020300:
    sys.exit('ERROR: Python bindings of GDAL 2.2.3 or later required due to GeoPackage performance issues.')

def getOutputLayerName(shpFilename):
    filenameOnly = os.path.basename(shpFilename)
    filenameParts = filenameOnly.split("_")
    datasetCode = filenameParts[1]
    datasetName = filenameParts[-4]
    componentSelector1 = filenameParts[2]
    componentSelector2 = filenameParts[3]
    lod = filenameParts[4]
    uref = filenameParts[5]
    #Create the layer if it doesn't already exist.
    outLayerName = datasetName + "_" + lod + "_" + componentSelector1 + "_" + componentSelector2
    return outLayerName

def getFilenameComponents(shpFilename):
    components = {}
    filenameOnly = os.path.basename(shpFilename)
    filenameParts = filenameOnly.split("_")
    datasetCode = filenameParts[1]
    components['datasetcode'] = datasetCode
    componentSelector1 = filenameParts[2]
    components['selector1'] = componentSelector1
    componentSelector2 = filenameParts[3]
    components['selector2'] = componentSelector2
    lod = filenameParts[4]
    components['lod'] = lod
    uref = filenameParts[5]
    components['uref'] = uref
    rref = filenameParts[6]
    components['rref'] = rref

    return components

def copyFeaturesFromShapeToGeoPackage(shpFilename, gpkgFilename):
    dbfFilename = converter.getFeatureClassAttrFileName(shpFilename)
    convertedFields = []
    fClassRecords = {}
    layerComponents = getFilenameComponents(shpFilename)
    if(os.path.isfile(dbfFilename)):
        fClassRecords = DBF.readDBF(dbfFilename)

    dataSource = ogr.Open(shpFilename)
    if(dataSource==None):
        print("Unable to open " + shpFilename)
        return 0
    layer = dataSource.GetLayer(0)
    if(layer == None):
        print("Unable to read layer from " + shpFilename)
        return 0
    layerDefinition = layer.GetLayerDefn()
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)
    outLayerName = getOutputLayerName(shpFilename)

    ogrDriver = ogr.GetDriverByName("GPKG")
    gpkgFile = ogrDriver.CreateDataSource(gpkgFilename)

    if(gpkgFile == None):
        print("Unable to create " + gpkgFilename)
        return
    gpkgFile.StartTransaction()
    outLayer = gpkgFile.GetLayerByName(outLayerName)
    fieldIdx = 0
    fieldIndexes = {}
    if(outLayer!=None):
        outputLayerDefinition = outLayer.GetLayerDefn()
        for i in range(outputLayerDefinition.GetFieldCount()):
            fieldName =  outputLayerDefinition.GetFieldDefn(i).GetName()
            convertedFields.append(fieldName)
            fieldIndexes[fieldName] = fieldIdx
            fieldIdx += 1
    else:
        outLayer = gpkgFile.CreateLayer(outLayerName,srs,geom_type=layerDefinition.GetGeomType())
        
        # Add fields
        for i in range(layerDefinition.GetFieldCount()):
            fieldName =  layerDefinition.GetFieldDefn(i).GetName()
            fieldTypeCode = layerDefinition.GetFieldDefn(i).GetType()
            fieldType = layerDefinition.GetFieldDefn(i).GetFieldTypeName(fieldTypeCode)
            fieldWidth = layerDefinition.GetFieldDefn(i).GetWidth()
            GetPrecision = layerDefinition.GetFieldDefn(i).GetPrecision()
            fieldDef = ogr.FieldDefn(fieldName,fieldTypeCode)
            outLayer.CreateField(fieldDef)
            convertedFields.append(fieldName)
            fieldIndexes[fieldName] = fieldIdx
            fieldIdx += 1

        # Add the LOD and UXX fields
        fieldName =  "_DATASET_CODE"
        fieldTypeCode = ogr.OFTString
        fieldDef = ogr.FieldDefn(fieldName,fieldTypeCode)
        outLayer.CreateField(fieldDef)
        convertedFields.append(fieldName)
        fieldIndexes[fieldName] = fieldIdx
        fieldIdx += 1

        fieldName =  "_COMPONENT_SELECTOR_1"
        fieldTypeCode = ogr.OFTString
        fieldDef = ogr.FieldDefn(fieldName,fieldTypeCode)
        outLayer.CreateField(fieldDef)
        convertedFields.append(fieldName)
        fieldIndexes[fieldName] = fieldIdx
        fieldIdx += 1

        fieldName =  "_COMPONENT_SELECTOR_2"
        fieldTypeCode = ogr.OFTString
        fieldDef = ogr.FieldDefn(fieldName,fieldTypeCode)
        outLayer.CreateField(fieldDef)
        convertedFields.append(fieldName)
        fieldIndexes[fieldName] = fieldIdx
        fieldIdx += 1

        fieldName =  "_LOD"
        fieldTypeCode = ogr.OFTString
        fieldDef = ogr.FieldDefn(fieldName,fieldTypeCode)
        outLayer.CreateField(fieldDef)
        convertedFields.append(fieldName)
        fieldIndexes[fieldName] = fieldIdx
        fieldIdx += 1

        fieldName =  "_UREF"
        fieldTypeCode = ogr.OFTString
        fieldDef = ogr.FieldDefn(fieldName,fieldTypeCode)
        outLayer.CreateField(fieldDef)
        convertedFields.append(fieldName)
        fieldIndexes[fieldName] = fieldIdx
        fieldIdx += 1

        fieldName =  "_RREF"
        fieldTypeCode = ogr.OFTString
        fieldDef = ogr.FieldDefn(fieldName,fieldTypeCode)
        outLayer.CreateField(fieldDef)
        convertedFields.append(fieldName)
        fieldIndexes[fieldName] = fieldIdx
        fieldIdx += 1

        #create fields for featureClass Attributes
    
        for recordCNAM, row in fClassRecords.items():
            for fieldName,fieldValue in row.items():
                if(fieldName in convertedFields):
                    continue
                fieldTypeCode = ogr.OFTString
                if(isinstance(fieldValue,float)):
                    fieldTypeCode = ogr.OFSTFloat32
                if(isinstance(fieldValue,int)):
                    fieldTypeCode = ogr.OFTInteger
                if(isinstance(fieldValue,bool)):
                    fieldTypeCode = ogr.OFSTBoolean
                fieldDef = ogr.FieldDefn(fieldName,fieldTypeCode)

                outLayer.CreateField(fieldDef)
                convertedFields.append(fieldName)
                fieldIndexes[fieldName] = fieldIdx
                fieldIdx += 1
            #read one record to get the field name/types
            break

    layerDefinition = outLayer.GetLayerDefn()
    layer.ResetReading()
    featureCount = 0
    inFeature = layer.GetNextFeature()
    while inFeature is not None:
        featureCount += 1
        outFeature = ogr.Feature(layerDefinition)
        #Copy the geometry and attributes 
        outFeature.SetFrom(inFeature)

        cnamValue = inFeature.GetField('CNAM')
        fclassRecord = fClassRecords[cnamValue]
        outFeature.SetField(fieldIndexes["_DATASET_CODE"], layerComponents['datasetcode'])
        outFeature.SetField(fieldIndexes["_COMPONENT_SELECTOR_1"], layerComponents['selector1'])
        outFeature.SetField(fieldIndexes["_COMPONENT_SELECTOR_2"], layerComponents['selector2'])
        outFeature.SetField(fieldIndexes["_LOD"], layerComponents['lod'])
        outFeature.SetField(fieldIndexes["_UREF"], layerComponents['uref'])
        outFeature.SetField(fieldIndexes["_RREF"], layerComponents['href'])
        
        '''
        # set the output features to match the input features
        for i in range(layerDefinition.GetFieldCount()):
            # Look for CNAM to link to the fClassRecord fields
            fieldName = layerDefinition.GetFieldDefn(i).GetNameRef()
            if(fieldName in ("_DATASET_CODE","_COMPONENT_SELECTOR_1","_COMPONENT_SELECTOR_2","_LOD","_UREF","_RREF")):
                continue
            if(fieldName in fclassRecord):
                fieldValue = fclassRecord[fieldName]
            if((fclassRecord != None) and (fieldName in fclassRecord)):
               outFeature.SetField(fieldIndexes[fieldName], fieldValue)
            else:
               outFeature.SetField(fieldIndexes[fieldName],inFeature.GetField(i))
        '''
        #write the feature
        outLayer.CreateFeature(outFeature)
        outFeature = None
        inFeature = layer.GetNextFeature()
    
    return featureCount

#convert a shapefile into a GeoPackage file using GDAL.
def convertTable(sqliteCon, shpFilename, cdbInputDir, cdbOutputDir):
    import converter
    fcAttrName = converter.getFeatureClassAttrFileName(shpFilename)    
    
    #Create the features table, adding the feature class columns
    outputGeoPackageFile = converter.getOutputGeoPackageFilePath(shpFilename,cdbInputDir, cdbOutputDir)
    ogrDriver = ogr.GetDriverByName("GPKG")
    #create the extended attributes table
    
    #Read the feature class attributes into a table
    fcAttrRows = DBF.readDBF(fcAttrName)
    #Read all the feature records from the DBF at once (using GDAL)
    copyFeaturesFromShapeToGeoPackage(shpFilename,outputGeoPackageFile)

    #Flatten Feature class records into the feature table
        
    #Link all extended attributes via related tables
    return

#Convert extended attributes table
def convertExtendedAttributes(sqliteCon,dbfFileName,gpkgLayerName):
    #DBF.convertDBF(sqliteCon,dbfFilename,dbfTableName,tableDescription):
    return

def translateCDB(cDBRoot,ogrPath, removeShapefile):
    sys.path.append(cDBRoot)
    import shapeindex

    datasourceDict = {}
    ogrDriver = ogr.GetDriverByName("GPKG")
    for shapefile in shapeindex.shapeFiles:
        fileparts = shapefile.split('\\')
        subdir = ""
        for i in range(len(fileparts)-4):
            if(i==0):
                subdir = fileparts[i]
            else:
                subdir = subdir + "\\" + fileparts[i]
        lat = fileparts[-6]
        lon = fileparts[-5]
        datasetName = fileparts[-4]
        UXX = fileparts[-3]
        LXX = fileparts[-2]
        base = fileparts[-1]
        selector2 = base[18:22]
        # strip out the .shp
        shapename = base[0:-4]
        # Create a geotile geopackage
        fullGpkgPath = subdir + "/" + datasetName + ".gpkg"

        gpkgFile = None
        if(fullGpkgPath in datasourceDict.keys()):
            gpkgFile = datasourceDict[fullGpkgPath]
        else:
            gpkgFile = ogrDriver.CreateDataSource(fullGpkgPath)
            datasourceDict[fullGpkgPath] = gpkgFile
        if(gpkgFile == None):
            print("Unable to create " + fullGpkgPath)
            continue
        gpkgFile.StartTransaction()
        dbfFilename = shapefile
        sqliteCon = sqlite3.connect(fullGpkgPath)
        if(selector2=='T005'):
            featureCount = convertTable(gpkgFile,sqliteCon,datasetName,dbfFilename,selector2,'T006','T018')

        # If it's a point feature (T001)
        # T002 Point feature class attributes
        # T016 Point Feature Extended-level attributes
        elif(selector2=='T001'):
            featureCount = convertTable(gpkgFile,sqliteCon,datasetName,dbfFilename,selector2,'T002','T016')
        # If it's a lineal (T003)
        # T004 Lineal feature class attributes
        # T017 Lineal Feature Extended-level attributes
        elif(selector2=='T003'):
            featureCount = convertTable(gpkgFile,sqliteCon,datasetName,dbfFilename,selector2,'T004','T017')
        # If it's a Lineal Figure Point Feature (T007)
        # T019 Lineal Figure Extended-level attributes
        # T008 Lineal Figure Point feature class attributes
        elif(selector2=='T007'):
            featureCount = convertTable(gpkgFile,sqliteCon,datasetName,dbfFilename,selector2,'T008','T019')
        # If it's a Polygon Figure Point Feature (T009)
        # T010 Polygon figure point feature class attributes
        # T020 Polygon Figure Extended-level attributes
        elif(selector2=='T009'):
            featureCount = convertTable(gpkgFile,sqliteCon,datasetName,dbfFilename,selector2,'T010','T020')
        if(featureCount>0):
            print("Translated " + str(featureCount) + " features.")
        gpkgFile.CommitTransaction()


if(len(sys.argv) != 3):
    print("Usage: Option1d.py <Input Root CDB Directory> <Output Directory for GeoPackage Files>")
    exit()

cDBRoot = sys.argv[1]
outputDirectory = sys.argv[2]

#generate a list of all the shapefiles.
import generateMetaFiles
generateMetaFiles.generateMetaFiles(cDBRoot)

