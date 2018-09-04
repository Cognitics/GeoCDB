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
