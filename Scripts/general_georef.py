#Main Program, used to georeference and index rasters without nomenclature

#This is intended to be run in ArcGIS 10.1 or higher.  

#import basic modules
import os, arcpy, shutil

#import all modules from 3rd parties
import xlrd, xlwt, zipfile

#import local modules
import secondary_functions
import error_handling
import tiling
import georef

#Get directory with Excel Files (Parameter - from arcgis tool)

# Excel Files, multipart input:
workbookName = arcpy.GetParameterAsText(0)

# rasters:
tifDir = arcpy.GetParameterAsText(1)


#Boolean that verifies if you want to georeference
georefBool = arcpy.GetParameter(2)

# Output directory:
outputDir = arcpy.GetParameterAsText(3)

#Generic Metadata file.  Custom metadata out of scope for this project. Optional
metadataLoc = arcpy.GetParameterAsText(4)


#5 Spatial Coordinate System
coordSys = arcpy.GetParameter(5)
coordSys = coordSys.factoryCode

#6. union shape file (Optional)
#unionShapefile = ""
unionShapeFileZip = arcpy.GetParameterAsText(6)
unionShapefile = ""

#######################END PARAMETERS#####################################

#Create Scratch Directory
scratchDir = outputDir + "\\" + "scratch"
cropTemp = scratchDir + "\\crop"

if not os.path.exists(scratchDir):
    os.mkdir(scratchDir)
if not os.path.exists(cropTemp):
	os.mkdir(cropTemp)

#Set Data Frame Coordinate system to input paramater:
secondary_functions.setDataFrameGCS(coordSys)
                         
#Get list of all files within that directory
dirList = os.listdir(tifDir)

#Get list of tiffs, ensure it is just a list of tiffs with nothing else.  
tifList = []
for l in dirList:
    if l[-4:] == ".tif" or l[-4:] == ".TIF":
        tifList.append(l)
del dirList



#Create errorlog
errorLog = error_handling.createErrorLog(outputDir)
arcpy.AddMessage("Error log created - no errors found yet")


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
        arcpy.AddMessage("Opening worksheet for " + worksheet.name)


        #Get row count, for loop cycling through rows
        for rownum in xrange(worksheet.nrows):

            #skip first row (if rowNum != 0)
            if rownum != 0:
                errorMessage = ""
                #open row
                worksheetRow = worksheet.row(rownum)
                arcpy.AddMessage("Testing index entry for " + worksheetRow[0].value)
                errorMessage = error_handling.checkForError(worksheetRow, tifList,"")  
                
                #Determine if errors exist, if not then georeference if required and package.
                if errorMessage != "":
                        arcpy.AddMessage("Error found for " + worksheetRow[0].value + ". Check error log")
                        error_handling.addError(worksheetRow, tabIndex,
                                                errorMessage, errorLog)
                else:
                    arcpy.AddMessage("No errors found for " + worksheetRow[0].value)
                    if georefBool:
                        arcpy.AddMessage("Now georeferencing " + worksheetRow[0].value)
                        georef.georef(worksheetRow, tifDir,
                                      worksheetRow[0].value,
                                      cropTemp, coordSys)

                        #(Zip all files in the //scratch// directory, move the new file to the output directory
                        zipArch = outputDir + "\\" + worksheetRow[0].value[:-4] + ".zip"
                        
                        secondary_functions.zipFolder(cropTemp, zipArch, metadataLoc)
                        #Remove all layers from data pane
                        tiling.footprint(worksheetRow, unionShapefile,
                                         tabIndex ,'True')
                        secondary_functions.emptyTempFolder(cropTemp)
                    else:
                        #Copy features to temp folder
                        secondary_functions.emptyTempFolder(cropTemp)
                        shutil.copyfile(tifDir + "\\" + worksheetRow[0].value,
                                        cropTemp + "\\" + worksheetRow[0].value)
                        zipArch = outputDir + "\\" + worksheetRow[0].value[:-4] + ".zip"
                        secondary_functions.zipFolder(cropTemp, zipArch, metadataLoc)                     
                        secondary_functions.emptyTempFolder(cropTemp)
                        tiling.footprint(worksheetRow, unionShapefile,
                                     tabIndex, 'False')
                                                
                    
                if errorMessage == "bounding not rectangular - manual georef required":
                    #Copy features to temp folder
                    secondary_functions.emptyTempFolder(cropTemp)
                    shutil.copyfile(tifDir + "\\" + worksheetRow[0].value,
                                    cropTemp + "\\" + worksheetRow[0])
                    zipArch = outputDir + "\\" + worksheetRow[0].value[:-4] + ".zip"
                    secondary_functions.zipFolder(cropTemp, zipArch, metadataLoc)                     
                    secondary_functions.emptyTempFolder(cropTemp)
                    tiling.footprint(worksheetRow, unionShapefile,
                                 tabIndex, 'False')
                arcpy.AddMessage("Archiving finished for " + worksheetRow[0].value)
                    
#Clean folders
os.removedirs(cropTemp)
arcpy.AddMessage("All indexing and archiving complete")

#Remove duplicate features
fields = ["filename","Grid_Type"]
arcpy.AddMessage("Removing identical features in spatial index...")
arcpy.DeleteIdentical_management(unionShapefile, fields)

#move footprint to scratch folder
arcpy.AddMessage("Indexing complete. Carrying out final stages")
if arcpy.Exists(scratchDir + "\\" + "raster_footprint.shp"):
    secondary_functions.removeLayers()
    arcpy.AddField_management(scratchDir + "\\" + "raster_footprint.shp", "DATE_YEAR", "DATE")
    arcpy.ConvertTimeField_management(scratchDir + "\\" + "raster_footprint.shp","year","yyyy",
                                      "DATE_YEAR")
    secondary_functions.zipFolder(scratchDir, outputDir + "\\" + "FOOTPRINT_SHP" + ".zip",metadataLoc)
    secondary_functions.emptyTempFolder(scratchDir)
    os.removedirs(scratchDir)
