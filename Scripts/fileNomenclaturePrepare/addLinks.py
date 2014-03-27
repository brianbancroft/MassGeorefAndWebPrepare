#This tool is a specific tool for a specific purpose.

import arcpy, os

dir = arcpy.GetParameterAsText(0)
fc = arcpy.GetParameterAsText(1)
url = arcpy.GetParameterAsText(2)
cursor = arcpy.da.UpdateCursor(fc, ("filename","location1","location2"))

for row in cursor:
    file = row[0]
    if os.path.exists(dir + "\\" + row[0] + "Crop.zip"):
        row[1] = url + "/" + row[0] + "Crop.zip"
    if os.path.exists(dir + "\\" + row[0] + "White.zip"):
        row[2] = url + "/" + row[0] + "White.zip"
    cursor.updateRow(row)
