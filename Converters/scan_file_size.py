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
import math


def scanDirectory(cDBRoot):
    allocUnits = [2048,4096,8192,16384,128*1024,256*1024]
    fileCount = 0
    totalFileSize = 0
    totalDiskSizes = {} # Key is the alloc unit size, value is the accumulated size
    for allocationUnitSize in allocUnits:
        totalDiskSizes[allocationUnitSize] = 0

    for root, dirs, files in os.walk(cDBRoot):
        path = root.split(os.sep)
        for file in files:
            base,ext = os.path.splitext(file)
            filePath = os.path.join(root,file)
            if((ext==".shp") or 
            (ext==".dbf") or
            (ext==".dbt") or
            (ext==".shx")):
                actualFileSize = os.path.getsize(filePath)
                totalFileSize += actualFileSize
                fileCount += 1
                for allocationUnitSize in allocUnits:
                    onDiskSize = (math.ceil(actualFileSize / allocationUnitSize)  * allocationUnitSize)
                    totalDiskSizes[allocationUnitSize] = totalDiskSizes[allocationUnitSize] + onDiskSize
                    
        #pyFile.write(']\n')
    print("Total File Count:" + str(fileCount))
    print("Total File Size:" + str(totalFileSize))
    print("Total On Disk Size:")
    print("0," + str(totalFileSize))
    for allocationUnitSize in allocUnits:
        print(str(allocationUnitSize) + "," + str(totalDiskSizes[allocationUnitSize]))
    

scanDirectory(r'E:\CDB\northwest_cdb_part2')
#scanDirectory(r'E:\MUTC_CDB')
#scanDirectory(r'E:\CDB_Yemen_4.0.0')
