import datetime
import xlrd
import xlwt
import os


#Function -Check for error
#Third varible in function determines case between brechin and general tools
def checkForError(row, rasList,case):
    output = "no name match"
    #Go to first raster in list of rasters - for loop
    for raster in rasList:
        #does the raster name match cycled match the one in the excel row object?
        if case == "brechin":
            if str(row[0].value[:-5]) == str(raster[:-5]):
                #are all the numerical fields filled?
                n = 7
                while n <= 14:
                    if output != "incomplete latlong fields" and output != "invalid character in latlong fields":
                        if row[n].value == "": 
                            output = "incomplete latlong fields"
                        if str(type(row[n].value)) != "<type 'float'>":
                            output = "invalid character in latlong fields"
                    if output != "incomplete latlong fields" and output != "invalid character in latlong fields":
                        output = "bounding not rectangular - manual georef required"
                        if row[6].value == 'Rectangular' or row[6].value == 'rectangular':
                            output = ""
                    n += 1

        else:
            if str(row[0].value) == str(raster):
                #are all the numerical fields filled?
                n = 7
                while n <= 14:
                    if output != "incomplete latlong fields" and output != "invalid character in latlong fields":
                        if row[n].value == "": 
                            output = "incomplete latlong fields"
                        if str(type(row[n].value)) != "<type 'float'>":
                            output = "invalid character in latlong fields"
                    if output != "incomplete latlong fields" and output != "invalid character in latlong fields":
                        output = "bounding not rectangular - manual georef required"
                        if row[6].value == 'Rectangular' or row[6].value == 'rectangular':
                            output = ""
                    n += 1                            

    return output

###addError:           
def addError(inrow, yr, error, wrkBk):

    #open output workbook using xlrd 
    workbook = xlrd.open_workbook(wrkBk)
    worksheet = workbook.sheet_by_index(0)
    #get length of workbook
    nrows = worksheet.nrows - 1

    #create output workbook from scratch
    outwb = xlwt.Workbook(encoding = 'UTF-8')
    outws = outwb.add_sheet("log")

    #populate existing cells from outsheet into new book
    n = 0
    while n <= nrows:
        m = 0
        while m < 17:
            outws.write(n,m,worksheet.cell(n,m).value)
            m += 1
        n += 1
    del m

    #populate new row with the row entries from the source spreadsheet
    m = 0
    while m <= 14:
        outws.write(n,m, inrow[m].value)
        m += 1

    #add year, province, error type
    outws.write(n,15,yr)
    outws.write(n,16,error)

    #Save and overwrite
    outwb.save(wrkBk)

#Create Error Log
def createErrorLog(dir):
    #construct sheet
    fc = "errorLog-indexing-" + str(datetime.date.today()) + ".xls"
    wb = xlwt.Workbook(encoding = 'UTF-8')
    ws = wb.add_sheet("log")

    #Populate first row
    cellEntry = ["File","Map_Title","Map_Subtitle","grid_type","scale",
                 "PROV_STATE","bounding","SE_LAT","SE_LONG","SW_LAT",
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
