
import dbfread

#Return a dictionary of dictionaries 
#The top level dictionary maps CNAME values to a dictionary of key/value pairs representing column names -> values
def readDBF(dbfFilename):
    cNameRecords = {}
    dbfields = None
    try:
        dbfFields = dbfread.DBF(dbfFilename).fields
        for record in dbfread.DBF(dbfFilename,load=True):
            recordFields = {}

            for field in record.keys():
                recordFields[field] = record[field]
                #print(record)

            cNameRecords[record['CNAM']] = recordFields
    except dbfread.exceptions.DBFNotFound:
        return None
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