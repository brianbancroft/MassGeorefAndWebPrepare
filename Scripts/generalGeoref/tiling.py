import arcpy, xlrd
import secondary_functions

def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
    
def createFootprint(dir):
    in_table = "raster_footprint.shp"
    if not arcpy.Exists(dir + "\\" + in_table):
        arcpy.CreateFeatureclass_management(dir, in_table)
        fieldList = ["filename","title","subtitle",
                     "province","year","Grid_Type","Scale","geoRef_rdy","location1","location2","location3"]

        typeList = ["TEXT","TEXT","TEXT","TEXT","SHORT","TEXT","TEXT","TEXT","TEXT","TEXT","TEXT"]
        
        n = 0
        while n < len(fieldList): 
            arcpy.AddField_management(dir + "/" + in_table, fieldList[n] , typeList[n])
            n += 1

    return(dir + "/" + in_table)


####a4. createFootprint:###
def footprint(row, fc, yearText, gSuccess):
    #From Excel row, pull xy data into an array of arrays of floats
    #Example: [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]

    if is_int(yearText) == True:
        year = int(yearText)
    else:
        year = 0

    featArray = [[(row[14].value),(row[13].value)],
                   [(row[12].value),(row[11].value)],
                   [(row[10].value), (row[9].value)],
                   [(row[8].value),(row[7].value)]]
   
    #Turn Array into a polygon object

    featGeom = arcpy.Polygon(arcpy.Array([arcpy.Point(*Coords)
                                          for Coords in featArray]))
    #Create insertCursor
    cursor = arcpy.da.InsertCursor(fc, ("filename", "title",
                                        "subtitle", "province", "year",
                                        "Grid_Type", "Scale","geoRef_rdy", "SHAPE@"))

    #NEW:  If not feature exists, insert the row.  
    
    #Use the cursor to insert a row
    cursor.insertRow((row[0].value[:-5],row[1].value,
                      row[2].value, row[5].value, year,
                      row[3].value, row[4].value, gSuccess,
                      featGeom))
    secondary_functions.removeLayers()

    del cursor