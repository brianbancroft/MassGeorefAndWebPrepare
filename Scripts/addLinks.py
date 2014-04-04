'''This is a tool for ArcGIS that can be used after the georeferencing process to add link fields to the spatial index
eventually, I would like to have this integrated with the main files as an option, but constraints divert my 
attention elsewhere. 

This tool only works with shapefiles or zip files whose   '''


import arcpy, os, zipfile

dir = arcpy.GetParameterAsText(0)
fc = arcpy.GetParameterAsText(1) #optional
url = arcpy.GetParameterAsText(2)

#NEW MOD (V1.3) - check if input class if a zipfile.  If it is, 
zipBool = arcpy.GetParameter(3) #optional
zipFile = arcpy.GetParameterAsText(4) #optional
if zipBool:
    fc = zipFile
    fc_folder = os.path.dirname(os.path.realpath(fc))
    with zipfile.ZipFile(fc, "r") as z:
        newPath = fc_folder + "\\tempPath\\"
        z.extractall(newPath)
    os.remove(fc)
    
    #Add the fields and populate them
    list = os.listdir(newPath)
    if list[0][:-3] == list[1][:-3]:
    
        fc = os.listdir(newPath)[0][:-3] + "shp"
        cursor = arcpy.da.UpdateCursor(fc, ("filename","location1","location2"))
        for row in cursor:
            file = row[0]
            if os.path.exists(dir + "\\" + row[0] + "Crop.zip"):
                row[1] = url + "/" + row[0] + "Crop.zip"
            if os.path.exists(dir + "\\" + row[0] + "White.zip"):
                row[2] = url + "/" + row[0] + "White.zip"
            cursor.updateRow(row)

#Zip the results.  
if zipBool:
    list = os.listdir(newPath)         
    with zipfile.ZipFile(my_zip, "w") as z:
        for l in list:
            z.write(newPath + l,l,zipfile.ZIP_DEFLATED)
            
    for l in list:
        os.remove(newPath + l)
            
