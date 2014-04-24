import arcpy
import os
import xlwt
import xlrd
import shutil
import zipfile

###Function:  Set Coordinate System
def setDataFrameGCS(c):
    mxd = arcpy.mapping.MapDocument("CURRENT")
    df = arcpy.mapping.ListDataFrames(mxd)[0]
    df.spatialReference = arcpy.SpatialReference(c)
    del mxd

###Function: Remove Layers in data frame
def removeLayers():
    mxd = arcpy.mapping.MapDocument("CURRENT")
    for df in arcpy.mapping.ListDataFrames(mxd):
        for lyr in arcpy.mapping.ListLayers(mxd, "", df):
            arcpy.mapping.RemoveLayer(df, lyr)
    del mxd


###Function: emptyTempFolder(folder)
def emptyTempFolder(folder):
    list = os.listdir(folder)
    for l in list:
        os.remove( folder + "\\" + l)

###Function: Archive files into zip
def zipFolder(my_dir, my_zip,metadata):
    list = os.listdir(my_dir)         
    with zipfile.ZipFile(my_zip, "w") as z:
        for l in list:
            if not l[-4:] == "lock":
                z.write(my_dir +"\\" + l,l,zipfile.ZIP_DEFLATED)
        if os.path.exists(metadata):
            z.write(metadata,list[0][:-3]+"xml",zipfile.ZIP_DEFLATED)
