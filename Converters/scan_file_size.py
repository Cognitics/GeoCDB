'''
Copyright 2018, US Army Geospatial Center, Leidos Inc., and Cognitics Inc.

Developed as a joint work by The Army Geospatial Center, Leidos Inc., 
and Cognitics Inc. 

Permission is granted to use this code for any purpose as long as this
copyright and permission header remains intact in each source file.
'''

import os
import sys

cDBRoot = r'D:\CDB\northwest_cdb_part2'
fileCount = 0
totalSize = 0

#create python file for the dictionary

# shapeFiles = ['xxx.shp','yyy.shp']

pyFile = open('shapeindex.py','w')
pyFile.write('shapeFiles = [')
first = True
for root, dirs, files in os.walk(cDBRoot):
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
            if(ext==".shp"):
                if(first != True):
                    pyFile.write(",")
                first = False
                # Add this file to the list if it's a shape file
                pyFile.write("\n\tr'" + filePath + "'")
pyFile.write(']\n')
print("Total File Count:" + str(fileCount))
print("Total File Size:" + str(totalSize))


