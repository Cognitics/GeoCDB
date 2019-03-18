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
import dbfread

try:
    from osgeo import ogr, osr, gdal
except:
    sys.exit('ERROR: cannot find GDAL/OGR modules')

def removeShapeFile(shpFile):
    os.remove(shpFile)
    os.remove(shpFile[0:-3] + "dbf")
    os.remove(shpFile[0:-3] + "dbt")
    os.remove(shpFile[0:-3] + "shx")

def getFeatureClassSelector(fclassSelector):
    # If it's a polygon (T005)
        # T006 Polygon feature class attributes
        if(fclassSelector=='T005'):
            return 'T006'
        # If it's a point feature (T001)
        # T002 Point feature class attributes
        elif(fclassSelector=='T001'):
            return 'T002'
        # If it's a lineal (T003)
        # T004 Lineal feature class attributes
        elif(fclassSelector=='T003'):
            return 'T004'
        # If it's a Lineal Figure Point Feature (T007)
        # T008 Lineal Figure Point feature class attributes
        elif(fclassSelector=='T007'):
            return'T008'
        # If it's a Polygon Figure Point Feature (T009)
        # T010 Polygon figure point feature class attributes
        elif(fclassSelector=='T009'):
            return'T010'

def getExtendedAttributesSelector(fclassSelector):
    # If it's a polygon (T005)
        # T018 Polygon Feature Extended-level attributes
        if(fclassSelector=='T005'):
            return 'T018'
        # If it's a point feature (T001)
        # T016 Point Feature Extended-level attributes
        elif(fclassSelector=='T001'):
            return 'T016'
        # If it's a lineal (T003)
        # T017 Lineal Feature Extended-level attributes
        elif(fclassSelector=='T003'):
            return 'T017'
        # If it's a Lineal Figure Point Feature (T007)
        # T019 Lineal Figure Extended-level attributes
        elif(fclassSelector=='T007'):
            return'T019'
        # If it's a Polygon Figure Point Feature (T009)
        # T020 Polygon Figure Extended-level attributes
        elif(fclassSelector=='T009'):
            return'T020'


def getSelector2(shpFilename):
    base = os.path.basename(shpFilename)
    selector2 = base[18:22]
    return selector2


def getFeatureClassAttrFileName(shpFilename):
    #get the selector of the feature table
    featuresSelector2 = getSelector2(shpFilename)
    #get the corresponding feature class table
    fcAttrSelector = getFeatureClassSelector(featuresSelector2)
    if(fcAttrSelector==None):
        return None

    dbfFilename = shpFilename.replace(featuresSelector2,fcAttrSelector)
    dbfFilename = dbfFilename.replace('.shp','.dbf')
    return dbfFilename

def getExtendedAttrFileName(shpFilename):
    #get the selector of the feature table
    featuresSelector2 = getSelector2(shpFilename)
    #get the corresponding feature class table
    fcAttrSelector = getExtendedAttributesSelector(featuresSelector2)
    if(fcAttrSelector==None):
        return None
    dbfFilename = shpFilename.replace(featuresSelector2,fcAttrSelector)
    dbfFilename = dbfFilename.replace('.shp','.dbf')
    return dbfFilename

def getFeatureAttrTableName(shpFilename):
    tableName = os.path.basename(shpFilename)[0:-4]
    return tableName


def getOutputGeoPackageFilePath(shpFilename,cdbInputPath,cdbOutputPath):
    baseShapefileName = os.path.basename(shpFilename)
    inputDir = os.path.dirname(shpFilename)
    outputDir = inputDir.replace(cdbInputPath,cdbOutputPath)
    fulloutputFilePath = os.path.join(outputDir,baseShapefileName)
    fullGPKGOutputFilePath = fulloutputFilePath[0:-4] + '.gpkg'
    return fullGPKGOutputFilePath

def convertTable(gpkgFile, sqliteCon, datasetName, shpFilename,  selector, fclassSelector, extAttrSelector):
    featureCount = 0
    dbfFilename = shpFilename
    base = os.path.basename(dbfFilename)
    featureTableName = base[:-4]

    dbfFilename = dbfFilename.replace(selector,fclassSelector)
    dbfFilename = dbfFilename.replace('.shp','.dbf')
    
    base = os.path.basename(dbfFilename)
    featureClassAttrTableName = base.replace(selector,fclassSelector)
    featureClassAttrTableName = featureClassAttrTableName[:-4]
    fClassRecords = {}
    # Polygon feature class attributes
    if(os.path.isfile(dbfFilename)):
        opendbf = True
        fClassRecords = readDBF(dbfFilename)
    
    # Polygon Feature Extended-level attributes    
    dbfFilename = shpFilename
    dbfFilename = dbfFilename.replace(selector,extAttrSelector)
    dbfFilename = dbfFilename.replace('.shp','.dbf')
    extendedAttrTableName = base.replace(selector,extAttrSelector)
    extendedAttrTableName = extendedAttrTableName[:-4]
    extendedAttrFields = []
    if(os.path.isfile(dbfFilename)):
        opendbf = True
        extendedAttrFields = convertDBF(sqliteCon,dbfFilename,extendedAttrTableName, 'Feature Extended Attributes')
    shpFields = []
    featureCount,shpFields = convertSHP(sqliteCon,shpFilename,gpkgFile,datasetName,fClassRecords)
    
    return featureCount

'''
def convertSHP(sqliteCon,shpFilename,gpkgFilename,fClassRecords = None, includeComponents = True):
    convertedFields = []
    featureCount = 0
    
    filenameOnly = os.path.basename(shpFilename)
    #cdbFileName = filenameOnly[0:-4]
    base,ext = os.path.splitext(filenameOnly)
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

    filenameParts = base.split("_")
    #datasetCode = filenameParts[1]
    #componentSelector1 = filenameParts[2]
    #componentSelector2 = filenameParts[3]
    #lod = filenameParts[4]
    #uref = filenameParts[5]
    #rref = filenameParts[6]

    gpkgFile = ogrDriver.CreateDataSource(gpkgFilename)
    fieldIndexes = {}
    fieldIdx = 0
    #Create the layer if it doesn't already exist.
    outLayerName = getFeatureAttrTableName(shpFilename)
    outLayer = outputDataSource.GetLayerByName(outLayerName)

    if(outLayer==None):
        outLayer = outputDataSource.CreateLayer(outLayerName,srs,geom_type=layerDefinition.GetGeomType())
        if(outLayer==None):
            print("Unable to create layer " + outLayerName)
            exit(0)
        
        # Add fields
        for i in range(layerDefinition.GetFieldCount()):
            fieldName =  layerDefinition.GetFieldDefn(i).GetName()
            fieldTypeCode = layerDefinition.GetFieldDefn(i).GetType()
            #fieldType = layerDefinition.GetFieldDefn(i).GetFieldTypeName(fieldTypeCode)
            #fieldWidth = layerDefinition.GetFieldDefn(i).GetWidth()
            #precision = layerDefinition.GetFieldDefn(i).GetPrecision()
            fieldDef = ogr.FieldDefn(fieldName,fieldTypeCode)
            outLayer.CreateField(fieldDef)
            convertedFields.append(fieldName)
            fieldIndexes[fieldName] = fieldIdx
            fieldIdx += 1

        if(includeComponents):
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
        if(fClassRecords != None):
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
    else:
        #Get the field indexes
        outLayerDefinition = outLayer.GetLayerDefn()
        for i in range(outLayerDefinition.GetFieldCount()):
            fieldName =  outLayerDefinition.GetFieldDefn(i).GetName()
            convertedFields.append(fieldName)
            fieldIndexes[fieldName] = fieldIdx
            fieldIdx += 1

    outLayer.StartTransaction()
    layerDefinition = outLayer.GetLayerDefn()
    layer.ResetReading()
    featureCount = 0
    inFeature = layer.GetNextFeature()
    while inFeature is not None:
        featureCount += 1
        outFeature = ogr.Feature(layerDefinition)
        inGeometry = inFeature.GetGeometryRef()
        outFeature.SetGeometry(inGeometry)
        if(includeComponents):
            cnamValue = inFeature.GetField('CNAM')
            fclassRecord = fClassRecords[cnamValue]
            outFeature.SetField("_DATASET_CODE", filenameParts[1])
            outFeature.SetField("_COMPONENT_SELECTOR_1", filenameParts[2])
            outFeature.SetField("_COMPONENT_SELECTOR_2", filenameParts[3])
            outFeature.SetField("_LOD", filenameParts[4])
            outFeature.SetField("_UREF", filenameParts[5])
            outFeature.SetField("_RREF", filenameParts[6])
        # set the output features to match the input features
        for i in range(layerDefinition.GetFieldCount()):
            # Look for CNAM to link to the fClassRecord fields
            fieldName = layerDefinition.GetFieldDefn(i).GetNameRef()
            if(fieldName in ("_DATASET_CODE","_COMPONENT_SELECTOR_1","_COMPONENT_SELECTOR_2","_LOD","_UREF","_RREF")):
                continue
            if(fieldName in fclassRecord):
                fieldValue = fclassRecord[fieldName]
            if((fclassRecord != None) and (fieldName in fclassRecord)):
               outFeature.SetField(fieldName, fieldValue)
            else:
               outFeature.SetField(fieldName,inFeature.GetField(i))
        if(fClassRecords != None):
            #flatten attributes from the feature class attributes table
            if(cnamValue in fClassRecords.keys()):
                fclassFields = fClassRecords[cnamValue]
                for field in fclassFields.keys():
                    outFeature.SetField(fieldIndexes[field],fclassFields[field])
        #write the feature
        outLayer.CreateFeature(outFeature)
        outFeature = None
        inFeature = layer.GetNextFeature()
    outLayer.CommitTransaction()
    return featureCount,convertedFields
'''
#Return a dictionary of dictionaries 
#The top level dictionary maps CNAME values to a dictionary of key/value pairs representing column names -> values
def readDBF(dbfFilename):
    cNameRecords = {}

    dbfFields = dbfread.DBF(dbfFilename).fields

    for record in dbfread.DBF(dbfFilename,load=True):
        recordFields = {}        

        for field in record.keys():
            recordFields[field] = record[field]
            #print(record)

        cNameRecords[record['CNAM']] = recordFields
            
    return cNameRecords


def convertDBF(sqliteCon,dbfFilename,dbfTableName,tableDescription):
    dbfTable = readDBF(dbfFilename)
    convertedFields = []
    cursor = sqliteCon.cursor()
    cursor.execute("BEGIN TRANSACTION")
    dbfFields = dbfread.DBF(dbfFilename).fields
    createString = "CREATE TABLE '" + dbfTableName + "' ('fid' INTEGER PRIMARY KEY AUTOINCREMENT "
    firstField = True
    for fieldno in range(len(dbfFields)):
        # add column
        field = dbfFields[fieldno]
        convertedFields.append(field)
        createString += ','
        createString += "'" + field.name + "' "
        createFieldTypeString  = "TEXT"
        if(field.type=='F' or field.type=='O' or field.type=='N'):
            createFieldTypeString  = "REAL"
        elif(field.type == 'I'):
            createFieldTypeString  = "INTEGER"
        firstField = False
        createString += createFieldTypeString
    createString += ")"
    
    cursor.execute(createString)

    contentsString = "insert into gpkg_contents (table_name,data_type,identifier,description,last_change) VALUES(?,'attributes',?,?,strftime('%Y-%m-%dT%H:%M:%fZ','now'))"
    contentsAttrs = (dbfTableName,dbfTableName,dbfTableName + " " + tableDescription)
    cursor.execute(contentsString,contentsAttrs)

    for record in dbfTable:
        #print(record)
        insertValues = []
        insertValuesString = ""
        insertString = ""
                                            
        for key,value in record.items():
            if(len(insertString)>0):
                insertString += ","
                insertValuesString += ","
            else:
                    insertString = "INSERT INTO " + dbfTableName + " ("
                    insertValuesString += " VALUES ("
            insertString += key
            insertValues.append(value)
            insertValuesString += "?"
        insertValuesString += ")"
        insertString += ") "
        insertString += insertValuesString
        #print(insertString)
        cursor.execute(insertString,tuple(insertValues))
    cursor.execute("COMMIT TRANSACTION")
    return convertedFields
