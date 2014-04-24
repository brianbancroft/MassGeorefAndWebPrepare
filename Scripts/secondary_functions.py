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

###Function:  Create Blank Error Log
def createErrorLog(dir):
    #construct sheet
    fc = "errorLog-" + str(datetime.date.today()) + ".xls"
    wb = xlwt.Workbook(encoding = 'UTF-8')
    ws = wb.add_sheet("log")

    #Populate first row with headings
    cellEntry = ["File","Map_Title","Map_Subtitle","grid_type","scale",
                 "province_state","bounding","SE_LAT","SE_LONG","SW_LAT",
                 "SW_LONG","NW_LAT","NW_LONG","NE_LAT","NE_LONG",
                 "YEAR","ERROR"]
    n = 0
    while n < len(cellEntry):
        ws.write(0,n,cellEntry[n])
        n += 1

    #save book
    if os.path.isfile("C:/Temp" + "/" + fc) == False:
        wb.save(dir + "/" + fc)
    else:
        fc  = ("errorLog-" +
               datetime.datetime.now().strftime("%m-%d_t%H%M") + ".xls")
        wb.save(dir + "/" + fc)

    return(dir + "/" + fc)

###Function: Create Success Log
def createLog(dir):
    #construct sheet
    fc = "success_log-" + str(datetime.date.today()) + ".xls"
    wb = xlwt.Workbook(encoding = 'UTF-8')
    ws = wb.add_sheet("log")

    #Populate first row
    cellEntry = ["File","Map_Title","Map_Subtitle","grid_type","scale",
                 "province_state","bounding","SE_LAT","SE_LONG","SW_LAT",
                 "SW_LONG","NW_LAT","NW_LONG","NE_LAT","NE_LONG",
                 "YEAR"]
    n = 0
    while n < len(cellEntry):
        ws.write(0,n,cellEntry[n])
        n += 1

    #save book
    if os.path.isfile("C:/Temp" + "/" + fc) == False:
        wb.save(dir + "/" + fc)
    else:
        fc  = ("success_log-" +
               datetime.datetime.now().strftime("%m-%d_t%H%M") + ".xls")
        wb.save(dir + "/" + fc)
    return(dir + "/" + fc)

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
