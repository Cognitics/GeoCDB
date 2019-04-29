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

def cleanPath(path):
    cleanPath = path.replace("\\",'/')
    return cleanPath

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
    #if(os.path.isfile(dbfFilename)):
    #    opendbf = True
    #    extendedAttrFields = convertDBF(sqliteCon,dbfFilename,extendedAttrTableName, 'Feature Extended Attributes')
    shpFields = []
    featureCount = convertSHP(sqliteCon,shpFilename,gpkgFile,datasetName,fClassRecords)
    
    return featureCount


if(False):
    # Create foreign key to the extended attributes
    if(len(extendedAttrTableName)>0):
        fkSQL = "ALTER TABLE " + featureTableName + " ADD COLUMN extended_attr INTEGER REFERENCES " + extendedAttrTableName + "(rowid);"
        fkCursor = sqliteCon.cursor()
        fkCursor.execute(fkSQL)
    if(len(extendedAttrFields)>0):
        # Create a view
        viewSQL = "CREATE VIEW " + featureTableName + extAttrSelector + " AS \nSELECT\n "
        for featAttr in shpFields:
            viewSQL += featureTableName + "." + featAttr + " AS " + selector + "." + featAttr + ",\n"
        for featAttr in extendedAttrFields:
            viewSQL += extendedAttrTableName + "." + featAttr + " AS " + extAttrSelector + "." + featAttr + ",\n"
        # There will be an extra comma at the end
        viewSQL = viewSQL[:-len(",\n")]
        viewSQL += "\nFROM \n" + featureTableName + "\n"
        viewSQL += "INNER JOIN " + extendedAttrTableName + " ON " + extendedAttrTableName + ".rowid = " + featureTableName + ".rowid;"
        #print(viewSQL)
        viewCursor = sqliteCon.cursor()
        viewCursor.execute(viewSQL)

def convertSHP(sqliteCon,shpFilename,gpkgFile,datasetName, fClassRecords):
    convertedFields = []
    featureCount = 0
    
    filenameOnly = os.path.basename(shpFilename)
    cdbFileName = filenameOnly[0:-4]
    base,ext = os.path.splitext(filenameOnly)
    dataSource = ogr.Open(shpFilename)
    if(dataSource==None):
        print("Unable to open " + shpFilename)
        return 0
    layer = dataSource.GetLayer(0)
    if(layer == None):
        print("Unable to read layer from " + shpFilename)
        return 0
    inFeature = layer.GetNextFeature()
    if inFeature is None:
        # If no features, the class-level attributes don't get created correctly, so don't create the attribute definitions
        return 0
    layerDefinition = layer.GetLayerDefn()
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)

    filenameParts = base.split("_")
    datasetCode = filenameParts[1]
    componentSelector1 = filenameParts[2]
    componentSelector2 = filenameParts[3]
    lod = filenameParts[4]
    uref = filenameParts[5]
    rref = filenameParts[6]

    datasetCodeInt = int(datasetCode[1:])
    componentSelector1Int = int(componentSelector1[1:])
    componentSelector2Int = int(componentSelector2[1:])
    if (lod[:2] == "LC"):
        lodInt = -int(lod[2:])
    else:
        lodInt = int(lod[1:])
    urefInt = int(uref[1:])
    rrefInt = int(rref[1:])
    
    #Create the layer if it doesn't already exist.
    outLayerName = datasetName + "_" + componentSelector1 + "_" + componentSelector2

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
        fieldTypeCode = ogr.OFTInteger
        fieldDef = ogr.FieldDefn(fieldName,fieldTypeCode)
        outLayer.CreateField(fieldDef)
        convertedFields.append(fieldName)
        fieldIndexes[fieldName] = fieldIdx
        fieldIdx += 1

        fieldName =  "_COMPONENT_SELECTOR_1"
        fieldTypeCode = ogr.OFTInteger
        fieldDef = ogr.FieldDefn(fieldName,fieldTypeCode)
        outLayer.CreateField(fieldDef)
        convertedFields.append(fieldName)
        fieldIndexes[fieldName] = fieldIdx
        fieldIdx += 1

        fieldName =  "_COMPONENT_SELECTOR_2"
        fieldTypeCode = ogr.OFTInteger
        fieldDef = ogr.FieldDefn(fieldName,fieldTypeCode)
        outLayer.CreateField(fieldDef)
        convertedFields.append(fieldName)
        fieldIndexes[fieldName] = fieldIdx
        fieldIdx += 1

        fieldName =  "_LOD"
        fieldTypeCode = ogr.OFTInteger
        fieldDef = ogr.FieldDefn(fieldName,fieldTypeCode)
        outLayer.CreateField(fieldDef)
        convertedFields.append(fieldName)
        fieldIndexes[fieldName] = fieldIdx
        fieldIdx += 1

        fieldName =  "_UREF"
        fieldTypeCode = ogr.OFTInteger
        fieldDef = ogr.FieldDefn(fieldName,fieldTypeCode)
        outLayer.CreateField(fieldDef)
        convertedFields.append(fieldName)
        fieldIndexes[fieldName] = fieldIdx
        fieldIdx += 1

        fieldName =  "_RREF"
        fieldTypeCode = ogr.OFTInteger
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
                    fieldTypeCode = ogr.OFTReal
                if(isinstance(fieldValue,int)):
                    fieldTypeCode = ogr.OFTInteger
                #DBase logical fields can have multiple values for true and false, best converted as text
                #if(isinstance(fieldValue,bool)):
                #    fieldTypeCode = ogr.OFSTBoolean
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

        outFeature.SetField(fieldIndexes["_DATASET_CODE"], datasetCodeInt)
        outFeature.SetField(fieldIndexes["_COMPONENT_SELECTOR_1"], componentSelector1Int)
        outFeature.SetField(fieldIndexes["_COMPONENT_SELECTOR_2"], componentSelector2Int)
        outFeature.SetField(fieldIndexes["_LOD"], lodInt)
        outFeature.SetField(fieldIndexes["_UREF"], urefInt)
        outFeature.SetField(fieldIndexes["_RREF"], rrefInt)

        #flatten attributes from the feature class attributes table, if a CNAM attribute exists
        try:
            cnamValue = inFeature.GetField('CNAM')
            fclassRecord = fClassRecords[cnamValue]
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
        except:
            #print("    File does not contain the CNAM attribute")
            cnamValue = ""

        #write the feature
        outLayer.CreateFeature(outFeature)
        outFeature = None
        inFeature = layer.GetNextFeature()

    return featureCount

#Return a dictionary of dictionaries 
#The top level dictionary maps CNAME values to a dictionary of key/value pairs representing column names -> values
def readDBF(dbfFilename):
    cNameRecords = {}

    dbfFields = DBF(dbfFilename).fields

    for record in DBF(dbfFilename,load=True):
        recordFields = {}        

        for field in record.keys():
            recordFields[field] = record[field]
            #print(record)

        cNameRecords[record['CNAM']] = recordFields
            
    return cNameRecords


def convertDBF(sqliteCon,dbfFilename,dbfTableName,tableDescription):
    a = readDBF(dbfFilename)
    return
    convertedFields = []
    cursor = sqliteCon.cursor()
    cursor.execute("BEGIN TRANSACTION")
    dbfFields = DBF(dbfFilename).fields
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
    #print(createString)
    
    cursor.execute(createString)

    contentsString = "insert into gpkg_contents (table_name,data_type,identifier,description,last_change) VALUES(?,'attributes',?,?,strftime('%Y-%m-%dT%H:%M:%fZ','now'))"
    contentsAttrs = (dbfTableName,dbfTableName,dbfTableName + " " + tableDescription)
    cursor.execute(contentsString,contentsAttrs)

    for record in DBF(dbfFilename):
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

def translateCDB(cDBRoot, outputRootDirectory):
    sys.path.append(cDBRoot)
    import generateMetaFiles
    shapeFiles = generateMetaFiles.generateMetaFiles(cDBRoot)
    datasourceDict = {}
    ogrDriver = ogr.GetDriverByName("GPKG")
    # Look for the Tiles Directory
    # For each whole Latitude (e.g. N45)
    #   For each whole Longitude
    #   Create N45W120.gpkg
    #   Walk the subdirectory below this
    for shapefile in shapeFiles:
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
        print("  Processing file " + shapename)
        # Create a geotile geopackage
        fullGpkgPath = subdir + "/" + datasetName + ".gpkg"
        print("    Output file " + datasetName + ".gpkg")
        #Use the same directory structure, but a different root directory.
        fullGpkgPath = fullGpkgPath.replace(cDBRoot,outputRootDirectory)

        # Make whatever directories we need for the output file.
        parentDirectory = os.path.dirname(cleanPath(fullGpkgPath))
        if not os.path.exists(parentDirectory):
            os.makedirs(parentDirectory)

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

        sqliteCon = sqlite3.connect(fullGpkgPath)
        #gpkgFileName = subdir + "\\" + lat + "\\" + lon + "\\" + dataset + ".gpkg"
        featureTableName = base
                                    
        # T015 2D Relationship dataset connections
        #todo
        # If it's 2D Relationship dataset connections (T015)
        #todo
        # 2D relationship tile connections (T011)
        #todo

        # Add Layer

                                
        
        featureClassAttrTableName = ""
        extendedAttrTableName = ""
        dbfFilename = shapefile
        #print(dbfFilename)

        # If it's a polygon (T005)
        # T006 Polygon feature class attributes
        # T018 Polygon Feature Extended-level attributes
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
    print("Usage: Option4.py <Input Root CDB Directory> <Output Directory for GeoPackage Files>")
    print("Example:")
    print("Option4.py F:\GeoCDB\Option4 F:\GeoCDB\Option4_output")

    exit()


cDBRoot = sys.argv[1]
outputDirectory = sys.argv[2]
translateCDB(cDBRoot,outputDirectory)