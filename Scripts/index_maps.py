#Main Program, used to index rasters.  This is intended to be run in ArcGIS 10.1 or higher.  

#import basic modules
import os, arcpy, shutil

#import all modules from 3rd parties
import xlrd, xlwt, zipfile

#import local modules
import secondary_functions
import index_error_handling
import tiling

# Output directory:
outputDir = arcpy.GetParameterAsText(2)

# Excel Files, multipart input:
workbookName = arcpy.GetParameterAsText(0)

#Spatial Coordinate System
coordSys = arcpy.GetParameter(1)
coordSys = coordSys.factoryCode

# union shape file (Optional)
unionShapeFileZip = arcpy.GetParameterAsText(3)
unionShapefile = ""

#Create Scratch Directory
scratchDir = outputDir + "\\" + "scratch"
cropTemp = scratchDir + "\\crop"
restoredTemp = scratchDir + "\\restored"

if not os.path.exists(scratchDir):
    os.mkdir(scratchDir)

#Set Data Frame Coordinate system to NAD 1927:
secondary_functions.setDataFrameGCS(coordSys)
                         
#Create errorlog, successlog.  
errorLog = index_error_handling.createErrorLog(outputDir)

#Determine if the input zip file spatial index exists. Unzip it and use it.
if os.path.exists(unionShapeFileZip):
    with zipfile.ZipFile(unionShapeFileZip, "r") as z:
        tempZipDir = scratchDir + "\\zipTemp"
        os.mkdir(tempZipDir)
        z.extractall(tempZipDir)
    for f in os.listdir(tempZipDir):
        if f[-3:] == "shp":
            unionShapefile = tempZipDir + "\\" + f
        
    arcpy.Project_management(unionShapefile, scratchDir + "\\" + "raster_footprint.shp",
                             coordSys)
    unionShapefile = scratchDir + "\\" + "raster_footprint.shp"
    secondary_functions.emptyTempFolder(tempZipDir)
    os.removedirs(tempZipDir)
    

#Verify if the union shapefile exists.  Project, or define projection.
if arcpy.Exists(unionShapefile) != True:
    arcpy.AddMessage("Creating new footprint file")
    #Create new footprint shapefile
    unionShapefile = tiling.createFootprint(scratchDir)
    arcpy.DefineProjection_management(unionShapefile, coordSys)


#open workbook
workbook = xlrd.open_workbook(workbookName)

#create list of spreadsheeks in open workbook
worksheetList = workbook.sheet_names()

#For loop - for spreadsheet in spreadsheetList
for tabIndex in worksheetList:
    
    #Ensure spreadsheet isn't named "template" or "Template"
    if tabIndex != "Template" and tabIndex != "template":

        #Open Worksheet
        worksheet = workbook.sheet_by_name(tabIndex)
        arcpy.AddMessage("\nIndexing entries from year: " + worksheet.name + "\n")

        #Get row count, for loop cycling through rows
        for rownum in xrange(worksheet.nrows):

            #skip first row (if rowNum != 0)
            if rownum != 0:
                errorMessage = ""
                #open row
                worksheetRow = worksheet.row(rownum)
                arcpy.AddMessage("Adding entry " + worksheetRow[0].value + " to spatial index")
                errorMessage = index_error_handling.checkForError(worksheetRow)  
                #does errorMessage equal ""?
                if errorMessage != "":                        
                    index_error_handling.addError(worksheetRow, tabIndex,
                                                      errorMessage, errorLog)
                    if errorMessage == "bounding not rectangular - manual georef required" or errorMessage == "no name match":
                        tiling.footprint(worksheetRow, unionShapefile,
                                         tabIndex, 'False')
                        arcpy.AddMessage("Entry " + worksheetRow[0].value + " successfuly added to spatial index")
                    else:
                        arcpy.AddMessage("Entry " + worksheetRow[0].value + " not added to spatial index. Bad Coordinates?")

                else:
                    tiling.footprint(worksheetRow, unionShapefile,
                                     tabIndex ,'True')
                    arcpy.AddMessage("Entry " + worksheetRow[0].value + " successfuly added to spatial index")

#Remove duplicate features
fields = ["filename","Grid_Type"]
arcpy.AddMessage("Removing identical features in spatial index...")
arcpy.DeleteIdentical_management(unionShapefile, fields)

#move footprint to zip
arcpy.AddMessage("Indexing complete. Carrying out final stages")
if arcpy.Exists(scratchDir + "\\" + "raster_footprint.shp"):
    secondary_functions.removeLayers()
    secondary_functions.removeLayers()
    arcpy.AddField_management(scratchDir + "\\" + "raster_footprint.shp", "DATE_YEAR", "DATE")
    arcpy.ConvertTimeField_management(scratchDir + "\\" + "raster_footprint.shp","year","yyyy",
                                      "DATE_YEAR")
    #arcpy.AddMessage("Converting Feature Class into Layer")
    #arcpy.MakeFeatureLayer_management(scratchDir + "\\" + "raster_footprint.shp",
    #                                  outputDir + "\\" +  "spatial_index_lyr")
    secondary_functions.zipFolder(scratchDir, outputDir + "\\" + "FOOTPRINT_SHP" + ".zip","")
    secondary_functions.emptyTempFolder(scratchDir)
    os.removedirs(scratchDir)