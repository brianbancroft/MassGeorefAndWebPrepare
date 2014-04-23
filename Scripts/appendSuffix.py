#This script appends the file names of all tifs in a directory 
#to use the special nomenclature for the special georeference tool.
import arcpy
import os


#function - find all tiffs in the specified directory
def getTiffs(folder):
    tifList = []
    list = os.listdir(folder)
    for l in list:
        if l[-4:] == ".tif" or l[-4:] == ".TIF":
           tifList.append(l)
    del list
    return tifList

#function - Appends the characters of the file chosen
def appendFiles(list,folder,char):
    for l in list:
        new = l[:-4] + char + ".tif"
        os.rename(folder + "\\" + l, folder + "\\" + new)

#START
cropFolder = arcpy.GetParameterAsText(0)
mapFolder = arcpy.GetParameterAsText(1)

if os.path.exists(cropFolder):
    cropList = getTiffs(cropFolder)
    appendFiles(cropList,cropFolder,"_C")


if os.path.exists(mapFolder):
    mapList = getTiffs(mapFolder)
    appendFiles(mapList,mapFolder,"_W")
