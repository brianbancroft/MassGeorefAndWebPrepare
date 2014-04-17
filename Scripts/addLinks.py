'''This script is designed to add website information to the index shapefile for the spatial index
which uses the BrechinBulk mass georeferencing tool. THIS TOOL WILL NOT WORK FOR THE GENERAL GEOREF, SADLY.'''
#Inputs: the feature class encased in a zipfile, the directory of the individual rasters in zips,
#the prefix of the URL where the tiles are hosted.
#Output: The feature class encased in a zipfile. 

import arcpy, os, zipfile

dir = arcpy.GetParameterAsText(0)
fc = arcpy.GetParameterAsText(1)
url = arcpy.GetParameterAsText(2)
myZip = fc


fc_folder = os.path.dirname(os.path.realpath(fc))
with zipfile.ZipFile(fc, "r") as z:
    newPath = fc_folder + "\\tempPath\\"
    z.extractall(newPath)
os.remove(fc)

#Add the fields and populate them
list = os.listdir(newPath)
if list[0][:-3] == list[1][:-3]:

    fc = newPath + "\\" + os.listdir(newPath)[0][:-3] + "shp"
    cursor = arcpy.da.UpdateCursor(fc, ("filename","location1","location2"))
    for row in cursor:
        file = row[0]
        if os.path.exists(dir + "\\" + row[0] + "Crop.zip"):
            row[1] = url + "/" + row[0] + "Crop.zip"
        if os.path.exists(dir + "\\" + row[0] + "White.zip"):
            row[2] = url + "/" + row[0] + "White.zip"
        cursor.updateRow(row)
    del cursor
#Zip the results.  

list = os.listdir(newPath)         
with zipfile.ZipFile(myZip, "w") as z:
    for l in list:
        z.write(newPath + l,l,zipfile.ZIP_DEFLATED)
        
for l in list:
    os.remove(newPath + l)
        
