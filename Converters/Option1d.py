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
import dbfconvert
import RelatedTables
try:
    from osgeo import ogr, osr, gdal
except:
    sys.exit('ERROR: cannot find GDAL/OGR modules')

import sqlite3

version_num = int(gdal.VersionInfo('VERSION_NUM'))
print("GDAL Version " + str(version_num))

if version_num < 2020300:
    sys.exit('ERROR: Python bindings of GDAL 2.2.3 or later required due to GeoPackage performance issues.')

def cleanPath(path):
    cleanPath = path.replace("\\",'/')
    return cleanPath

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
    baseName,ext = os.path.splitext(filenameOnly)
    filenameParts = baseName.split("_")
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

    #If this isn't a feature shapefile (e.g. a FC or extended attr), just ignore and continue
    if(dbfFilename==None):
        return None
    convertedFields = []
    fClassRecords = {}
    layerComponents = getFilenameComponents(shpFilename)
    if(os.path.isfile(dbfFilename)):
        fClassRecords = dbfconvert.readDBF(dbfFilename)

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
        outLayer = gpkgFile.CreateLayer(outLayerName,srs,geom_type=layerDefinition.GetGeomType(),options=["FID=id"])
        
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

        #Create fields for featureClass Attributes
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
        outFeature.SetField(fieldIndexes["_RREF"], layerComponents['rref'])
        
        #flatten attributes from the feature class attributes table
        if(cnamValue in fClassRecords.keys()):
            fclassFields = fClassRecords[cnamValue]
            for field in fclassFields.keys():
                outFeature.SetField(fieldIndexes[field],fclassFields[field])

        #write the feature
        outLayer.CreateFeature(outFeature)
        outFeature = None
        inFeature = layer.GetNextFeature()
    gpkgFile.CommitTransaction()
    return featureCount


def getOutputGeoPackageFilePath(shpFilename,cdbInputPath,cdbOutputPath):
    baseShapefileName = os.path.basename(shpFilename)
    inputDir = os.path.dirname(shpFilename)
    outputDir = inputDir.replace(cdbInputPath,cdbOutputPath)
    fulloutputFilePath = os.path.join(outputDir,baseShapefileName)
    fullGPKGOutputFilePath = fulloutputFilePath[0:-4] + '.gpkg'
    return fullGPKGOutputFilePath

#create the extended attributes table
def createExtendedAttributesTable(sqliteCon,shpFilename):
    #create the table
    if(sqliteCon == None):
        print("Unable to access database when creating extended attributes table")
        return None
    extendedAttributesDBFFilename = converter.getExtendedAttrFileName(shpFilename)    
    dbfTableName = getExtendedAttrTableName(shpFilename)
    if(os.path.exists(extendedAttributesDBFFilename)):
        return converter.convertDBF(sqliteCon,extendedAttributesDBFFilename,
            dbfTableName,'Extended Attributes')
    return None

def getExtendedAttrTableName(shpFilename):
    extendedAttributesDBFFilename = converter.getExtendedAttrFileName(shpFilename)
    shpBaseFilename = os.path.basename(shpFilename)
    dbfTableName = shpBaseFilename[0:-4]
    return dbfTableName

#convert a shapefile into a GeoPackage file using GDAL.
def convertShapeFile(shpFilename, cdbInputDir, cdbOutputDir):    
    fcAttrName = converter.getFeatureClassAttrFileName(shpFilename)    
    if(fcAttrName==None):
        return None
    #Create the features table, adding the feature class columns
    outputGeoPackageFile = getOutputGeoPackageFilePath(shpFilename,cdbInputDir, cdbOutputDir)
    # Make whatever directories we need for the output file.
    parentDirectory = os.path.dirname(cleanPath(outputGeoPackageFile))
    if not os.path.exists(parentDirectory):
        os.makedirs(parentDirectory)

    #Read all the feature records from the DBF at once (using GDAL)
    #copyFeaturesFromShapeToGeoPackage(shpFilename,outputGeoPackageFile)
    fClassRecords = converter.readDBF(fcAttrName)
    #Read Featureclass records
    featureTableName = converter.getFeatureAttrTableName(shpFilename)
    copyFeaturesFromShapeToGeoPackage(shpFilename,outputGeoPackageFile)
    #convertSHP(sqliteCon,shpFilename,outputGeoPackageFile, fClassRecords, True)
    sqliteCon = sqlite3.connect(outputGeoPackageFile)
    if(createExtendedAttributesTable(sqliteCon,shpFilename)):
        dbfTableName = getExtendedAttrTableName(shpFilename)
        RelatedTables.createRTESchema(sqliteCon)
        relationship = RelatedTables.Relationship()
        relationship.baseTableName = "fid"
        relationship.baseTableName = featureTableName
        relationship.baseTableColumn = "fid"
        relationship.relatedTableName = dbfTableName
        relationship.relationshipName = "CDB EA"
        relationship.mappingTableName = featureTableName + "_" + dbfTableName
        RelatedTables.addRelationshipTable(sqliteCon,relationship)
        #TODO: Link all extended attributes via related tables
        # For each feature row, match the CEAI,GEAI,VEAI records in the extended attributes
        # table, and link them with RelatedTables.addFeatureRelationship

    sqliteCon.close()
    return

def translateCDB(cdbInputDir, cdbOutputDir):
    sys.path.append(cdbInputDir)
    import generateMetaFiles
    shapeFiles = generateMetaFiles.generateMetaFiles(cDBRoot)

    for shapefile in shapeFiles:
        convertShapeFile(shapefile,cdbInputDir,cdbOutputDir)


if(len(sys.argv) != 3):
    print("Usage: Option1d.py <Input Root CDB Directory> <Output Directory for GeoPackage Files>")
    exit()

cDBRoot = sys.argv[1]
outputDirectory = sys.argv[2]
translateCDB(cDBRoot,outputDirectory)

