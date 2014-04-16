###a3. georef:###
import arcpy
import secondary_functions
import os


def georef(xlRow, inDir, inRas, scratch,coord):

    #set scratch location of georeferenced file
    outRas = scratch + "/" + inRas
    inRasPath = inDir + "/" + inRas

    #Use arcpy.GetRasterProperties_management to get position of raster edges
    import arcpy
    fcLeft = arcpy.GetRasterProperties_management(inRasPath, "LEFT")
    fcRight = arcpy.GetRasterProperties_management(inRasPath, "RIGHT")
    fcTop = arcpy.GetRasterProperties_management(inRasPath, "TOP")
    fcBottom = arcpy.GetRasterProperties_management(inRasPath, "BOTTOM")


    #Use xlrd to get the real-world location of the raster edges
    tgTopRight_x = float(xlRow[14].value)
    tgTopRight_y = float(xlRow[13].value)
    tgTopLeft_x = float(xlRow[12].value) 
    tgTopLeft_y = float(xlRow[11].value)
    tgBottomRight_x = float(xlRow[8].value)
    tgBottomRight_y = float(xlRow[7].value)
    tgBottomLeft_x = float(xlRow[10].value)
    tgBottomLeft_y = float(xlRow[9].value)
    
    #Pad data to create the source and destination coordinates to be used.
    srcPts = ("'" + str(fcRight) + " " + str(fcBottom) + "';'" + str(fcLeft)
              + " " + str(fcBottom) + "';'" + str(fcLeft) + " " + str(fcTop)
              + "';'" + str(fcRight) + " " + str(fcTop) + "'")

    destPts = ("'" + str(tgBottomRight_x) + " " + str(tgBottomRight_y) +
               "';'" + str(tgBottomLeft_x)+ " " + str(tgBottomRight_y) +
               "';'" + str(tgTopLeft_x) + " " + str(tgTopLeft_y)   +
               "';'" + str(tgTopRight_x) + " " + str(tgTopRight_y) + "'")

    
    #Define the projection of the raster 
    arcpy.DefineProjection_management(inRasPath, coord)
    #Remove layers from data frame
    secondary_functions.removeLayers()

    #Run the warp_management tool to georeference the raster.
    #output also goes to the scratch directory + // cropped + //outRas//
    arcpy.Warp_management(inRasPath,srcPts,destPts,outRas)
    

