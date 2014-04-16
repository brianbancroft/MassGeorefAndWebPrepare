#Prepare Folders
import arcpy,os

def getTiffs(folder):
    tifList = []
    list = os.listdir(folder)
    for l in list:
        if l[-4:] == ".tif":
           tifList.append(l)
    del list
    return tifList

def appendFiles(list,folder,char):
    for l in list:
        new = l[:-4] + char + ".tif"
        os.rename(folder + "\\" + l, folder + "\\" + new)

cropFolder = arcpy.GetParameterAsText(0)
mapFolder = arcpy.GetParameterAsText(1)

if os.path.exists(cropFolder):
    cropList = getTiffs(cropFolder)
    appendFiles(cropList,cropFolder,"_C")


if os.path.exists(mapFolder):
    mapList = getTiffs(mapFolder)
    appendFiles(mapList,mapFolder,"_W")