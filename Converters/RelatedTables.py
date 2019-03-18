import sys

class Relationship:
    def __init__(self):
        self.baseTableName = ""
        self.baseTableColumn = ""
        self.relatedTableName = ""
        self.relationshipName = ""
        self.mappingTableName = ""

def createRTESchema(sqliteCon):
    #See if the schema already exists
    cur = sqliteCon.cursor()
    cur.execute("BEGIN")
    #query = "select * from gpkg_extensions WHERE extension_name='related_tables'"
    #cur.execute(query)
    #rows = cur.fetchAll()
    #if(len(rows)==0):
    #    query = "insert into gpkg_extensions (table_name"

    query = '''CREATE TABLE IF NOT EXISTS 'gpkgext_relations' "
        "( id INTEGER PRIMARY KEY AUTOINCREMENT, base_table_name TEXT NOT NULL, "
        "base_primary_column TEXT NOT NULL DEFAULT 'id', related_table_name TEXT NOT NULL, "
        "related_primary_column TEXT NOT NULL DEFAULT 'id', relation_name TEXT NOT NULL, "
        "mapping_table_name TEXT NOT NULL UNIQUE )'''
    cur.execute(query)
    sqliteCon.commit()


def addRelatedMediaTable(sqliteCon, tableName):
    query = "CREATE TABLE IF NOT EXISTS '" + tableName + "' ( id INTEGER PRIMARY KEY AUTOINCREMENT, data BLOB NOT NULL, content_type TEXT NOT NULL )"
    cur = sqliteCon.cursor()
    cur.execute("BEGIN")
    #todo
    sqliteCon.commit()

def addRelationshipTable(sqliteCon, relationship):
    cur = sqliteCon.cursor()
    cur.execute("BEGIN")
    query = "CREATE TABLE IF NOT EXISTS '" + relationship.mappingTableName  + "' ( base_id INTEGER NOT NULL, related_id INTEGER NOT NULL )"
    cur.execute(query)
    query = '''
        INSERT INTO gpkgext_relations (base_table_name,base_primary_column,related_table_name,related_primary_column,
            relation_name,mapping_table_name) VALUES(?,?,?,?,?,?)"
            '''
    parameters = (relationship.baseTableName,
        relationship.baseTableColumn,
        relationship.relatedTableName,
        relationship.relatedTableColumn,
        relationship.relationshipName,
        relationship.mappingTableName)
    cur.execute(query,parameters)
    
    sqliteCon.commit()

def getRelationshipTables(sqliteCon, tableName):
    results = []
    query = "select * from gpkgext_relations WHERE base_table_name=?"
    cur = sqliteCon.cursor()
    cur.execute(query,(tableName))
    for row in cur:
        relationship = Relationship()
        relationship.baseTableName = row["base_table_name"]
        relationship.baseTableColumn = row["base_primary_column"]
        relationship.relatedTableName = row["related_table_name"]
        relationship.relatedTableColumn = row["related_primary_column"]
        relationship.relationshipName = row["relation_name"]
        relationship.mappingTableName = row["mapping_table_name"]
        results.append(relationship)
    return results

def getRelatedFeatureIDs(sqliteCon, tableName, fid):
    query = "SELECT * FROM " + tableName + "where base_id=?"
    results = []
    cur = sqliteCon.cursor()
    cur.execute("BEGIN")
    parameters = (fid)
    query = "SELECT related_id FROM " + tableName + "where base_id=?"
    cur.execute(query,parameters)
    for row in cur:
        results.append(row["related_id"])
    return results

def addFeatureRelationship(sqliteCon,relationship,baseId,relatedId):
    cur = sqliteCon.cursor()
    cur.execute("BEGIN")
    query = "INSERT INTO " + relationship.mappingTableName + " (base_id,related_id) VALUES(?,?)"
    cur = sqliteCon.cursor()
    cur.execute("BEGIN",(baseId,relatedId))
    cur.commit()


