'''
Copyright 2018, US Army Geospatial Center, Leidos Inc., and Cognitics Inc.

Developed as a joint work by The Army Geospatial Center, Leidos Inc., 
and Cognitics Inc. 

Permission is granted to use this code for any purpose as long as this
copyright and permission header remains intact in each source file.
'''
import os
import sys
import sqlite3



rootdir = r'd:\cdb'

for root, subFolders, files in os.walk(rootdir):
    #for folder in subFolders:
        #outfileName = rootdir + "/" + folder + "/py-outfile.txt" # hardcoded path
        #folderOut = open( outfileName, 'w' )
        #print "outfileName is " + outfileName
        
    for file in files:
        base,ext = os.path.splitext(file)
        if(ext.lower()=='.gpkg'):
            fullFileName = os.path.join(root,file)
            conn = sqlite3.connect(fullFileName)
            cursor = conn.execute('select table_name from gpkg_geometry_columns')
            for row in cursor:
                cmd = "CREATE INDEX idx_" + row[0] + "_composite on '" + row[0] + "'('_DATASET_CODE','_COMPONENT_SELECTOR_1','_COMPONENT_SELECTOR_2','_LOD','_UREF','_RREF')"
                conn.execute(cmd)
            conn.close()
