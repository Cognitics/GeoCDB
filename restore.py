
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
from shutil import copyfile

try:
    from osgeo import ogr, osr, gdal
except:
    sys.exit('ERROR: cannot find GDAL/OGR modules')
from dbfread import DBF

def restoreCDB(fromCDB, toCDB):
    
    fileCount = 0
    totalSize = 0

    gdal.UseExceptions()
    #create python file for the dictionary

   
    first = True
    for root, dirs, files in os.walk(fromCDB):
        path = root.split(os.sep)
        hasShapeFile = False
        for file in files:
            base,ext = os.path.splitext(file)
            filePath = os.path.join(root,file)
            if((ext==".shp") or 
            (ext==".dbf") or
            (ext==".dbt") or
            (ext==".shx")):
                fileCount += 1
                totalSize += os.path.getsize(filePath)
                #copy file
                fromPath = filePath
                relPath = fromPath[len(fromCDB):]
                destPath = toCDB + relPath
                print(fromPath + " -> " + destPath)
                copyfile(fromPath,destPath)

restoreCDB("d:\\cdb", "f:\GeoCDB\Option4")