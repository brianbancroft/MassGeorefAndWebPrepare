#Main Program, used to georeference and index rasters.
#Requires a Specific Nomenclature of files.
#See documentation for explanations
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


# Output directory:
#outputDir = "C:/Temp/outputDir" 
outputDir = arcpy.GetParameterAsText(0)

# Excel Files, multipart input:
#fileDir = "C:/Temp/" 
workbookName = arcpy.GetParameterAsText(1)

#Generic Metadata file.  Custom metadata out of scope for this project. Optional
metadataLoc = arcpy.GetParameterAsText(2)

#3. geotif directory:
#tifDir = "C:/Temp/tiffs"
tifDir = arcpy.GetParameterAsText(3)

#4. Special Tiff directory. Optional
whiteDir = arcpy.GetParameterAsText(4)

#5 Spatial Coordinate System
coordSys = arcpy.GetParameter(5)
coordSys = coordSys.factoryCode

#6. union shape file (Optional)
unionShapeFileZip = arcpy.GetParameterAsText(6)
unionShapefile = ""

#######################END PARAMETERS#####################################
georefToggle = False

#Create Scratch Directory
scratchDir = outputDir + "\\" + "scratch"
cropTemp = scratchDir + "\\crop"

if not os.path.exists(scratchDir):
    os.mkdir(scratchDir)
if not os.path.exists(cropTemp):
	os.mkdir(cropTemp)

#Set Data Frame Coordinate system to NAD 1927:
arcpy.AddMessage("Changing data frame coordinate system")
secondary_functions.setDataFrameGCS(coordSys)
                         
#Get list of all files within that directory
dirList = os.listdir(tifDir)

#Get list of tiffs, ensure it is just a list of tiffs with nothing else.  
tifList = []
for l in dirList:
    if l[-4:] == ".tif":
        tifList.append(l)
del dirList



#Create errorlog, successlog.
arcpy.AddMessage("Creating error log - no problems yet, though")
errorLog = error_handling.createErrorLog(outputDir)
#successLog = createLog(outputDir)

#Determine if the input zip file spatial index exists. Unzip it and use it.
if os.path.exists(unionShapeFileZip):
    with zipfile.ZipFile(unionShapeFileZip, "r") as z:
        tempZipDir = scratchDir + "\\zipTemp"
        os.mkdir(tempZipDir)
        z.extractall(tempZipDir)
    for f in os.listdir(tempZipDir):
<<<<<<< HEAD
        if f[-3:] == "shp":
=======
        if f[2:] == "shp":
>>>>>>> ebb1cfdcc882dd96f1aa86f3e3466b9bbd57d5c3
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
arcpy.AddMessage("Footprint file set up. Opening excel file index")
workbook = xlrd.open_workbook(workbookName)

#create list of spreadsheeks in open workbook
worksheetList = workbook.sheet_names()

#For loop - for spreadsheet in spreadsheetList
for tabIndex in worksheetList:
    arcpy.AddMessage("Opening the worksheet for " + tabIndex)
    #Ensure spreadsheet isn't named "template" or "Template"
    if tabIndex != "Template" and tabIndex != "template":

        #Open Worksheet
        worksheet = workbook.sheet_by_name(tabIndex)

        #Get row count, for loop cycling through rows
        for rownum in xrange(worksheet.nrows):
            #skip first row (if rowNum != 0)
            if rownum != 0:
                errorMessage = ""
                #open row
                worksheetRow = worksheet.row(rownum)
                arcpy.AddMessage("now inspecting " + worksheetRow[0].value[:-6])
                #Third varible in function determines case between brechin and general tools
                errorMessage = error_handling.checkForError(worksheetRow, tifList,"brechin")  
                #does errorMessage equal ""?
                if errorMessage != "":
                        arcpy.AddMessage("Problem observed with " + worksheetRow[0].value[:-6] + ". Adding entry to error log")
                        error_handling.addError(worksheetRow, tabIndex,
                                                errorMessage, errorLog)
                else:
                    arcpy.AddMessage(worksheetRow[0].value[:-6] + " seems to be alright. georeferencing.")
                    georef.georef(worksheetRow, tifDir, 
                                  worksheetRow[0].value[:-5] + "C.tif",
                                  cropTemp, coordSys)

                    secondary_functions.removeLayers()

                    #(Zip all files in the //scratch// directory, move the new file to the output directory
                    arcpy.AddMessage(worksheetRow[0].value[:-6] + " now georeferenced. Now Archiving.")
                    zipArch = outputDir + "\\" + worksheetRow[0].value[:-5] + "Crop.zip"
                    
                    secondary_functions.zipFolder(cropTemp, zipArch, metadataLoc)

                    arcpy.AddMessage(worksheetRow[0].value[:-6] + " now archived. Now adding to spatial index.")
                    tiling.footprint(worksheetRow, unionShapefile,
                                     tabIndex ,'True')

                if errorMessage == "bounding not rectangular - manual georef required":
                    arcpy.AddMessage(worksheetRow[0].value[:-6]  + " Can't be georeferenced automatically, but it's now being added to the index")
                    tiling.footprint(worksheetRow, unionShapefile,
                                     tabIndex, 'False')

                if os.path.exists(whiteDir):
                    if errorMessage != "no name match" and errorMessage != "incomplete latlong fields":
                        arcpy.AddMessage(worksheetRow[0].value[:-6]  +
                                         "'s restored version is now being archived.")
                        
                        secondary_functions.emptyTempFolder(cropTemp)
                        shutil.copyfile(whiteDir + "\\" + worksheetRow[0].value[:-5] + "W.tif" ,
                                                      cropTemp + "\\" + worksheetRow[0].value[:-5] + "W.tif")
                        zipArch = outputDir + "\\" + worksheetRow[0].value[:-5] + "White.zip"
                        secondary_functions.zipFolder(cropTemp, zipArch, metadataLoc)                     
                secondary_functions.emptyTempFolder(cropTemp)
                arcpy.AddMessage("All work with " + worksheetRow[0].value[:-6] + "is now done.")

os.removedirs(cropTemp)
arcpy.AddMessage("All Geoprocessing done. Now archiving the spatial index feature class")
arcpy.DeleteIdentical_management(unionShapefile ,
                                 'filename;title;subtitle;province;year;Grid_Type;Scale', '#', '0')



#Remove duplicate features
fields = ["filename","Grid_Type"]
arcpy.AddMessage("Removing identical features in spatial index...")
arcpy.DeleteIdentical_management(unionShapefile, fields)
#Final Cleanup
arcpy.AddMessage("Indexing complete. Carrying out final stages")
if arcpy.Exists(scratchDir + "\\" + "raster_footprint.shp"):
    secondary_functions.removeLayers()
    arcpy.AddField_management(scratchDir + "\\" + "raster_footprint.shp", "DATE_YEAR", "DATE")
    arcpy.ConvertTimeField_management(scratchDir + "\\" + "raster_footprint.shp","year","yyyy",
                                      "DATE_YEAR")
    #arcpy.AddMessage("Converting Feature Class into Layer")
    #arcpy.MakeFeatureLayer_management(scratchDir + "\\" + "raster_footprint.shp",
    #                                  outputDir + "\\" +  "spatial_index_lyr")
    secondary_functions.zipFolder(scratchDir, outputDir + "\\" + "FOOTPRINT_SHP" + ".zip",metadataLoc)
    secondary_functions.emptyTempFolder(scratchDir)
    os.removedirs(scratchDir)
