'''

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

try:
    from osgeo import ogr, osr, gdal
except:
    sys.exit('ERROR: cannot find GDAL/OGR modules')
from dbfread import DBF
import sqlite3

echoOn=False
       
gpkg_dr = ogr.GetDriverByName( 'GPKG' )


'''
*******************************************************************************************************
Class:           CDBgeopackage
Description:     This class maintains all connections to the Geopackage file and provides easy getters
                 to parameters of the geopackage
*******************************************************************************************************
'''
class CDBgeopackage:

    def __init__(self,fullFileName):
        self.fullFileName = fullFileName

        fileparts = self.fullFileName.split('\\')
        subdir = ""
        for i in range(len(fileparts)-4):
            if(i==0):
                subdir = fileparts[i]
            else:
                subdir = subdir + "\\" + fileparts[i]
        self.fullPath = subdir
        self.fileName = fileparts[-1]
        self.dataset = self.fileName[0:-5]
        self.selector1 = self.fileName[13:17]
        self.selector2 = self.fileName[18:22]
        self.isOpen = False
        self.gpkg = None
        self.sqlcon = None
        
    def print(self):
        print("GPKG full path : ",self.fullFileName)
        print("GPKG path only : ",self.fullPath)
        print("GPKG file only : ",self.fileName)
        print("GPKG dataset   : ",self.dataset)
        print("GPKG selector1 : ",self.selector1)
        print("GPKG selector2 : ",self.selector2)

    def dumpTables(self):
        sqliteCon=self.getSQLcon()
        cursor = sqliteCon.cursor()
        contentsString = 'SELECT * FROM ' + self.dataset
        cursor.execute(contentsString)
        count = 0
        for row in cursor :
            print(row)
            count = count + 1
        print(count, 'rows.')


    def open(self):
        if self.isOpen:
            return
        ogr.UseExceptions()
#        gpkg_dr = ogr.GetDriverByName( 'GPKG' )
        if gpkg_dr is None:
            print("error finding OGR driver for GEOPKG")
            return 'skip'

        self.gpkg=gpkg_dr.Open(self.fullFileName, update=1)
        if self.gpkg is None:
            print("error openning geopackage file ",self.fullFileName)
            return 'skip'
        self.isOpen = True

    def getGPKG(self):
        self.open()
        return self.gpkg

    def openSQLcon(self):
        if not self.sqlcon:
            self.open()
            self.sqlcon = sqlite3.connect(self.fullFileName)

    def close(self):
        self.gpkg=None

    def getSQLcon(self):
        if not self.sqlcon:
            self.openSQLcon()
        return self.sqlcon


            
#Table below has only CS2 matched - spec has all teh same CS2 for all vector datasets
DatasetInstanceToClass = {'T001':'T002',
                          'T003':'T004',
                          'T005':'T006',
                          'T007':'T008',
                          'T009':'T010'}

'''
*******************************************************************************************************
Function:        matchingClassDBF
Description:     Based on CDB convention, this fucntion will return the class DBF files matching an
                 instance shapefile
*******************************************************************************************************
'''
def matchingClassDBF(shapefileName):

        if echoOn:
                print("Checking match for ",shapefileName,"\n")
        fileparts = shapefileName.split('\\')
        subdir = ""
        for i in range(len(fileparts)-4):
            if(i==0):
                subdir = fileparts[i]
            else:
                subdir = subdir + "\\" + fileparts[i]
        datasetName = fileparts[-4][0:3]
        base = fileparts[-1]
        selector1 = base[13:17]
        selector2 = base[18:22]
        # strip out the .shp
        shapename = base[0:-4]

        classDBF=''

        if echoOn:
                print("Looking for dataset: ",datasetName," selector1: ",selector1," selector2: ",selector2,"\n")
        
        if (selector2 in DatasetInstanceToClass):
                selector2_out=DatasetInstanceToClass[selector2]
                # found a match - rebuilding the matching file name
                class_shp_out=shapefileName.replace(selector2,selector2_out)
                classDBF=class_shp_out.replace('shp','dbf')
                if not (os.path.exists(classDBF)):
                        print("Warning expected class DBF not found ",classDBF,"\n")
                        classDBF=''
                      
        if classDBF and echoOn:
                print("Matching ",shapefileName,"\nwith ",classDBF,"\n\n")

        return classDBF

'''
*******************************************************************************************************
Function:        readDBF
Description:     Return a dictionary of dictionaries 
                 The top level dictionary maps CNAME values to a dictionary of key/value pairs
                 representing column names -> values
*******************************************************************************************************
'''
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

	
'''
*******************************************************************************************************
Function:        addGeopackageClassAttToInstance
Description:     Based on a list of attributes (from class DBF), this function adds the attributes 
                 as fields into the geopackage file.
                 Note that this only adds the fileds definition but does not populate the shapefile
*******************************************************************************************************
'''
def addGeopackageClassAttToInstance(gpkgObject,fClassRecords):

    outLayer = gpkgObject.getGPKG().GetLayerByName(gpkgObject.dataset)

    convertedFields = []
    fieldIndexes = {}
    fieldIdx = 0
    if(outLayer!=None):
        if echoOn:
            print("Found layer\n")
        outputLayerDefinition = outLayer.GetLayerDefn()
        for i in range(outputLayerDefinition.GetFieldCount()):
            fieldName =  outputLayerDefinition.GetFieldDefn(i).GetName()
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

'''
*******************************************************************************************************
Function:        insertClassValueInGPKGinstance
Description:     Based on a list of attributes/value key pair (from class DBF), this function adds  
                 the attribute values (based on matching CNAM attribute, to each feature/instance
*******************************************************************************************************
'''
def insertClassValueInGPKGinstance(gpkgObject,fClassRecords):

    #start by adding the class attribute in the table
    addGeopackageClassAttToInstance(gpkgObject,fClassRecords)
    
    outLayer = gpkgObject.getGPKG().GetLayerByName(gpkgObject.dataset)
    outputLayerDefinition = outLayer.GetLayerDefn()
    gpkgObject.getGPKG().StartTransaction()

    #Itterate on DBF provided records for each CNAM
    for recordCNAM, row in fClassRecords.items():

        filterstring="CNAM = '"+recordCNAM+"'"

        if echoOn:
            print("Updating all features with CNAM ",recordCNAM)
        outLayer.ResetReading()
        outLayer.SetAttributeFilter(filterstring)
        cnt=0
        #Itterate on each features of the class and populate attributes
        for feature in outLayer:
            outLayer.SetFeature(feature)
            for fieldName,fieldValue in row.items():
                if (fieldName=='CNAM'):
                    continue 
                feature.SetField(fieldName,fieldValue)
            outLayer.SetFeature(feature)
            cnt+=1
        if echoOn:
            print("Updated ",cnt," Features")
    gpkgObject.getGPKG().CommitTransaction()


'''
*******************************************************************************************************
Function:        insertClassValueInGPKGtable
Description:     Based on a list of attributes/value key pair (from class DBF), this function adds  
                 the attribute values (based on matching CNAM attribute), to a new table in the GPKG
*******************************************************************************************************
'''
def insertClassValueInGPKGtable(gpkgObject,fClassRecords):

    gpkgObject.getGPKG().StartTransaction()

    convertedFields = []
    cursor = gpkgObject.getSQLcon().cursor()
#    cursor.execute("BEGIN TRANSACTION")
    dbfTableName = 'CLASS'
    createString = "CREATE TABLE '" + dbfTableName + "' ('CNAM' TEXT PRIMARY KEY "
    firstField = True

    # as all records in teh DBF has the same atributes, extract first element of
    # the dict in order to itterate on its attribute names.
    allkeys=list(fClassRecords.keys())

    if not any(allkeys):
        print("Error - class DBF seems empty")
        return
    index1Dic=fClassRecords.get(allkeys[0])

#    for recordCNAM, row in fClassRecords.items():
    for fieldName in index1Dic.keys():

        if (fieldName=='CNAM'):
            # skip CNAM as it is already established as primary key
            continue
        
        convertedFields.append(fieldName)
        createString += ','
        createString += "'" + fieldName + "' "

        createFieldTypeString  = "TEXT"
        fieldTypeCode = ogr.OFTString
        if(isinstance(index1Dic[fieldName],float)):
            createFieldTypeString  = "REAL"
        if(isinstance(index1Dic[fieldName],int)):
            createFieldTypeString  = "INTEGER"
        if(isinstance(index1Dic[fieldName],bool)):
            createFieldTypeString  = "BOOLEAN"
        firstField = False
        createString += createFieldTypeString
    createString += ")"
    print(createString)
    cursor.execute(createString)

    contentsString = "insert into gpkg_contents (table_name,data_type,identifier,description,last_change) VALUES(?,'attributes',?,?,strftime('%Y-%m-%dT%H:%M:%fZ','now'))"
    contentsAttrs = (dbfTableName,dbfTableName,dbfTableName + " Class attribute")
    cursor.execute(contentsString,contentsAttrs)

    #start populating the new table

    #print(record)
    #Itterate on DBF provided records for each CNAM
    for recordCNAM, row in fClassRecords.items():
        
        insertValues = []
        insertValuesString = ""
        insertString = ""
        if echoOn:
            print("Updating all features with CNAM ",recordCNAM)

        for fieldName,fieldValue in row.items():
            if(len(insertString)>0):
                insertString += ","
                insertValuesString += ","
            else:
                insertString = "INSERT INTO " + dbfTableName + " ("
                insertValuesString += " VALUES ("
            insertString += fieldName
            insertValues.append(fieldValue)
            insertValuesString += "?"
        insertValuesString += ")"
        insertString += ") "
        insertString += insertValuesString
        print(insertString)
        cursor.execute(insertString,tuple(insertValues))
        print("Executed")

#    cursor.execute("COMMIT TRANSACTION")
    gpkgObject.getGPKG().CommitTransaction()
    print(gpkgObject.getGPKG())
