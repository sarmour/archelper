"""
This module helps reduce the need to know arcpy for mapping. There are a few basic functions here that, when combined correctly, can create any number of maps quickly. This tool can use multiple CSVs, columns, and MXDs to create a large number of maps. Module users should use the create_dir() function first to set-up the correct C:/Mapping_Project structure. This module is designed to work with a csv containing values that should be mapped using graduated symbology. The user needs a CSV, shapefiles for mapping, mapping documents (.mxd files), and symbology.
"""
import arcpy
import operator
import os
import itertools
from glob import glob
import csv


def create_dir(folderpath='C:/Mapping_Project'):
    """Creates an empty folder directory on the C drive called Mapping_Project. Use this folder for mapping projects. under C:\Mapping_Project a subdirectory will be created with the following folders:
    MXDs: Put the mxd templates here.
    Out: All maps will go to this folder by default.
    Symbology: Create symbology layer files in this folder. This is not necessary, but is recommended.
    CSVs: You can loop through all CSVs in a folder. Like symbology, CSVs can go anywhere, but placing them in this folder is convenient.
    Shapefiles: You can use either a folder of shapefiles or a file geodatabase with shapefiles. The MXD templates must point to the corresponding shapefiles used in mapping. You can use this folder for convenience if there are many shipefile files.
     """

    maindir = 'C:/Mapping_Project'
    folderlist = [maindir, maindir + r'/MXDs', maindir + r'/Out', maindir + r'/Symbology', maindir + r'/CSVs', maindir + r'/Shapefiles']

    for item in folderlist:
        try:
            if not os.path.exists(item):
                os.mkdir(item)
        except:
            print "There was an error creating the directory:", item

    print "Empty folder directory created at C:/Mapping_Project. Put mxds, shapefiles, etc. in this folder directory."


def create_workspace(name):
    """Checks if a .gbp workspace exists in the mapping_project folder. This script returns the path of the workspace. The file geodatabase workspace replaces shapefiles in ArcGIS10.1 and later. You can create a file geodatabase using ArcCatalog as well. Once you create a filegeodatabase, import shapefiles into it using the Table to Geodatabase tool in the "ArcToolbox>Conversion Tools>To Geodatabase"  section.
    """
    gdbpath = 'C://Mapping_Project//' + name + '.gdb'
    if not os.path.exists(gdbpath):
        arcpy.CreateFileGDB_management('C://Mapping_Project//', name + '.gdb')
    else:
        print 'The workspace', name, 'exists at the path "C://Mapping_Project"'
    return gdbpath


def csv_checkmissingshpvals(inputfile, joincol, shapefile, shapefileheader, headers=True, filedelimiter=","):
    """Checks to see if any join column values in the inputfile are missing in the  shapefile or geodatabase table. The shapefile/geodatabase table can also be a geodatabase table. Returns a list of missing inputfile values in a shapefile that wil not be mapped. Headers is True by default.

        Default file delimiter is comma delimited but tab delimited can be used as well by specifiying '\t'.
    """
    with open(inputfile, "rb") as csvdata:
        csvinfo = csv.reader(csvdata, delimiter=filedelimiter)
        if headers:
            csvinfo.next()
        shpvals = []
        rows = arcpy.SearchCursor(shapefile, fields=shapefileheader)
        for row in rows:
            shpvals.append(str(row.getValue(shapefileheader)))
        results = []
        for l in csvinfo:
            if l[joincol] not in shpvals:
                results.append(l[joincol])
        if not results:
            print "All inputfile join values have a join value in the shapefile/table."
        return results


def file_getcols(inputfile, filedelimiter=","):
    """ Returns a list of the inputfile headers.
    Default file delimiter is comma delimited but tab delimited can be used as well by specifiying '\t'.
    """
    with open(inputfile, 'rb') as csvdata:
        cols = csv.reader(csvdata, delimiter=filedelimiter).next()
        return cols


def file_sort(inputfile, colindex=0, reverse=False, headers=True, filedelimiter=","):
    """ Sorts an inputfile based on the colindex. If reverse is True, the values will be sorted in reverse index. Common file delimiters are comma ',' and tab '\t'.

        Default file format is comma delimited     """
    with open(inputfile, 'rb') as csvdata:
        csvinfo = csv.reader(csvdata, delimiter=filedelimiter)
        if headers:
            headers = csvinfo.next()
        if reverse:
            vals = sorted(csvinfo, key=operator.itemgetter(colindex), reverse=True)
        else:
            vals = sorted(csvinfo, key=operator.itemgetter(colindex))
    with open(inputfile, 'wb') as outfile:
        wr = csv.writer(outfile, delimiter=filedelimiter)
        if headers:
            wr.writerow(headers)
        for l in vals:
            wr.writerow(l)
    print "Finished sorting the inputfile"


def file_jointable(inputfile, workspace, delimiter):
    """ Imports the file to an arcgis geodatabase workspace and returns a string with the workspace and table name. The first row of data in a csv/txt file will be used for column headers.

        File format options are csv, txt, dbf, xls, xlsx, OLE, INFO, VPF, personal/file/SDE geodtabase.
    """
    tablename = os.path.basename(inputfile)[:-4]
    try:
        arcpy.Delete_management(workspace + '//' + tablename)
        print "Old table in workspace deleted, replaced by new table ", workspace + '//'+tablename
    except:
        pass
    arcpy.TableToTable_conversion(inputfile, workspace, tablename)
    print "New table in workspace added to the workspace with name ", workspace + '//'+tablename
    return workspace + '//'+tablename

def shp_getcols(shapefile):
    """Returns a list of shapefile or geodtabase table columns."""
    mylist = []
    for field in arcpy.ListFields(shapefile):
        mylist.append(str(field.name.strip()))
    return mylist

def shp_removecols(shapefile, cols):
    """Removes fields from shapefile or geodatabase table specified in the cols list. Columns can only have 10 characters if a shapefile is being edited."""
    for col in cols:
        if shapefile[-4] == ".shp":
            col = col[:10]
        if arcpy.ListFields(shapefile, col):
            arcpy.DeleteField_management(shapefile, col)
            print 'Field deleted:', col
        else:
            print 'No field to delete:', col


def shp_addcols(shapefile, cols, datatype):
    """ Adds each column in the list of cols to the shapefile or geodatabase table. Columns can only have 10 characters in a shapefile. All columns added will be given the same datatype. If you try to add a duplicate column that is already in the shapefile, the existing duplicate column will be deleted.

        Possible fields types:

        TEXT Any string of characters.
        FLOAT  Fractional numbers between -3.4E38 and 1.2E38.
        DOUBLE  Fractional numbers between -2.2E308 and 1.8E308.
        SHORT  Whole numbers between -32,768 and 32,767.
        LONG  Whole numbers between -2,147,483,648 and 2,147,483,647.
        DATE Date and/or time.
        BLOB Long sequence of binary numbers. You need a custom loader or viewer or a third-party application to load items into a BLOB field or view the contents of a BLOB field.
        RASTER Raster images. All ArcGIS software-supported raster dataset formats can be stored, but it is highly recommended that only small images be used.
        GUID Globally unique identifier.

        NOTE: Geodatabase fields will be nullable.  For shapefiles, null values will be converted to the following value based upon

    Important: When adding values to a shapefile, Null values will be substituted.

        Shapefile null value substitution-
            Number  replaced by 0
            Text replaced by " "
            Date replaced by 0 but displays <null>

        For more info visit: http://desktop.arcgis.com/en/desktop/latest/manage-data/shapefiles/geoprocessing-considerations-for-shapefile-output.htm#GUID-A10ADA3B-0988-4AB1-9EBA-AD704F77B4A2

    """
    if isinstance(cols, list):
        for col in cols:
            if shapefile[-4] == ".shp":
                col = col[:10]
            if arcpy.ListFields(shapefile, col):
                print 'Removed existing column from the shapefile:', col
                arcpy.DeleteField_management(shapefile, col)
                arcpy.AddField_management(shapefile, col, datatype, field_is_nullable='NULLABLE')
            else:
                arcpy.AddField_management(shapefile, col, datatype, field_is_nullable='NULLABLE')
            print 'Added column to the shapefile:', col, datatype
    else:
        if shapefile[-4] == ".shp":
            col = col[:10]
        if arcpy.ListFields(shapefile, col):
            print 'Removed existing column from the shapefile:', col
            arcpy.DeleteField_management(shapefile, col)
            arcpy.AddField_management(shapefile, col, datatype)
        else:
            arcpy.AddField_management(shapefile, col, datatype)
        print 'Added column to the shapefile:', col, datatype


def shp_joincsv(csvfile, shapefile, shapefilejoincol, csvjoinindex, csvstartfield, csvfieldtype="double", filedelimiter=",", csvendfield=None, usecustomlabel = False, customnodatalabel=-9999):
    """ This function manually joins the CSV to the shapefile and does not use geodatabase tables. This method should be easier and faster in most cases. In the CSV, the join column must be before the columns with mapping values. This code will map all fields from the mapping column onward (to the right). Headers of the csv will be used as field names and have a 10 character limit. Field names must not start with numbers either.
        CSV field type can be 'double' or 'text'. If the fieldtype added is a double and there is no value, a a custom value of -9999 by default will be added. Arcpy automatically converts nulls to the values shown below, which is misleading. Use the customnodatalabel value and the symbology settings to represent no data. The default is -9999.

        Shapefile null value substitution- Use a feature class to avoid this
            Number 0
            Text " "
            Date 0 but displays <null>
        """

    isshp = False
    if shapefile[-4:] == ".shp":
        isshp = True
    cols = file_getcols(csvfile)

    i = 0
    newcols = []
    for col in cols:
        if csvendfield:
            if i >= csvstartfield and i < csvendfield:
                if isshp:
                    newcols.append(col[:10])
                else:
                    newcols.append(col)
        else:
            if i >= csvstartfield:
                if isshp:
                    newcols.append(col[:10])
                else:
                    newcols.append(col)
        i += 1
    shp_addcols(shapefile, newcols, csvfieldtype)
    i = 0

    with open(csvfile, 'rb') as csvfile:
        lib = dict()
        csvfile = csv.reader(csvfile, delimiter=filedelimiter)
        csvfile.next()
        for line in csvfile:
            if csvendfield:
                lib[line[csvjoinindex]] = lib.get(line[csvjoinindex], line[csvstartfield:csvendfield + 1])
            else:
                lib[line[csvjoinindex]] = lib.get(line[csvjoinindex], line[csvstartfield:])
    rows = arcpy.UpdateCursor(shapefile)
    shpjoinlist = []
    for row in rows:
        shpjoinval = str(row.getValue(shapefilejoincol))
        shpjoinlist.append(shpjoinval)
        try:
            vals = lib.get(shpjoinval)
        except:
            if usecustomlabel:
                for ind, field in enumerate(newcols):
                    row.setValue(str(field), customnodatalabel)
                    rows.updateRow(row)
                continue
            else:
                continue

        for ind, field in enumerate(newcols):
            try:
                if csvfieldtype.lower() == "double":
                    row.setValue(str(field), float(vals[ind]))
                elif csvfieldtype.lower() == "text":
                    row.setValue(str(field), str(vals[ind]))
                else:
                    row.setValue(str(field), str(vals[ind]))
            except:
##                print "Could not set value for:", shpjoinval, "for the field:", field
                row.setValue(str(field), None)
            rows.updateRow(row)

    del rows
    return


def shp_jointable(injointable, injoinfield, combinedtable, combinedtablefield, fields):
    """ Joins a workspace table to another workspace table or shapefile. The workspace table is generated by csv_jointable(). The jointable and shapefile variables should include the full file path ie. 'C:/path/to/shapefile.shp' or 'c:path/to/workspace.gbp/tablename' """
    new_fields = []
    for col in fields:
        if combinedtable[-4:] == ".shp":
            col = col[:10]
        new_fields.append(col)
        if arcpy.ListFields(combinedtable, col):
            arcpy.DeleteField_management(combinedtable, col)
    arcpy.JoinField_management(injointable, injoinfield, combinedtable, combinedtablefield, fields)
    print "Finished shapefile join."


def map_create1(mxds, shapefile, mapcols, symbology, labels=False, prefix=None, perchange_labels=False, LC_labels=False, mapresolution=600, nodatavalue=-9999):
    """This function will create maps for all mxds specified and all fields in the mapcols list. Shapefile can be a shapefile or geodtabase table. The prefixed symbology options are 'Percent_Change' and 'Diff_LC' or importy symbology from  your own layer file. Labels can be set to True or False. If Diff_LC or Percent_change is specified, labels will be formatted accordingly. Use the prefix variable to add a prefix to the output file name. Using a prefix is strongly recommended when mapping multiple CSVs. """

    if isinstance(mxds, str):
        newmxd = []
        newmxd.append(mxds)
        mxds = newmxd
    if isinstance(mapcols, str):
        newmapcols = []
        newmapcols.append(mapcols)
        mapcols = newmapcols
    isshp = False
    if shapefile[-4:] == ".shp":
        isshp = True
    newmapcols = []
    for col in mapcols:
        if isshp:
            col = col[:10]
        newmapcols.append(col)
    if symbology.lower() == "percent_change":
        symbpath = arcpy.mapping.Layer("C:/Mapping_Project/MXDs/Symbology/PercentChange.lyr")
    elif symbology.lower() == "diff_lc":
        symbpath = arcpy.mapping.Layer('C:/Mapping_Project/MXDs/Symbology/DifferenceinLossCost.lyr')
    elif symbology[-4:] == '.lyr':
        symbpath = arcpy.mapping.Layer(symbology)
    else:
        print "You need to choose a valid symbology type: 'Percent_Change','Diff_LC', or a layerfile path"
        return
    for mxd in mxds:
        mxdobj = arcpy.mapping.MapDocument(mxd)
        df = arcpy.mapping.ListDataFrames(mxdobj)[0]  # May need to change this to allow multiple dataframes in the future.
        for lyr in arcpy.mapping.ListLayers(mxdobj, data_frame = df):
            if (lyr.name.lower() == os.path.basename(shapefile).replace(".shp", "").lower() and isshp) or (lyr.name.lower() == os.path.basename(shapefile).lower() and not isshp):
                lyr.symbologyType == "GRADUATED_COLORS"
                for field in newmapcols:
                    arcpy.mapping.UpdateLayer(df, lyr, symbpath, True)  # if you get a value error, it could be because of the layers source symbology no longer being available. It could also be because of a join issue or incorrect column names. The column name character limit is 10 for shapefiles.
                    lyr.symbology.valueField = field
                    if labels:
                        lyr.showLabels = True
                        if (symbology.lower() == "percent_change") or (perchange_labels):
                            expres = "str(int(round(float(["+field+"])*100,0))) + '%'"
                        elif (symbology.lower() == "diff_lc") or (LC_labels):
                            expres = "str(round(float(["+field+"]),3))"
                        else:
                            expres = "["+field+"]"
                        for lblClass in lyr.labelClasses:
                            print lblClass, expres
                            lblClass.expression = expres
                            if isshp:
                                lblClass.SQLQuery = field + " <> " + str(nodatavalue)
                            lblClass.showClassLabels = True
                    else:
                        lyr.showLabels = False
                    arcpy.RefreshActiveView()
                    if prefix:
                        outpath = 'C:/Mapping_Project/Out/' + prefix + '_' + os.path.basename(mxd).rstrip('.mxd') + '_' + field + '.jpg'
                        print "Making a map at:", outpath
                    else:
                        outpath = 'C:/Mapping_Project/Out/' + os.path.basename(mxd).rstrip('.mxd') + '_' + field + '.jpg'
                        "Making a map at:", outpath
                    arcpy.mapping.ExportToJPEG(mxdobj, outpath, resolution=mapresolution)

# def shp_maxmin_newshp(shapefile, shapejoincol, shapefile2, shapejoincol2, addcols):
#     """Not using this function for the project, but it works, so i'm leaving it here. This function adds max and min values associated with shapefile1 to shapefile2. If shapefile 1 has 3 postcodes in a county, this script will add the max and min value to shapefile 2 for that county. The value -9999 in a shapefile is treated as unknown rather than a minimum change."""
#     i= 0
#     for col in addcols:
#         addcols[i] = col[:10]
#         i += 1
#     i = 0
#     shp_addcols(shapefile2, addcols, "STRING")
#     rows = arcpy.SearchCursor(shapefile)
#     shpvallist = []
#     joinlist = []
#     for row in rows:
#         vals = {}
#         vals[shapejoincol2] = row.getValue(shapejoincol2)
#         joinlist.append(vals[shapejoincol2])
#         for val in addcols:
#             vals[val] = float(row.getValue(val))
#         shpvallist.append(vals)

#     joinlist = set(joinlist)
#     coldict = {}
#     for col in addcols:
#         newdict = {}
#         for adminval in joinlist:
#             vals = []
#             for row in shpvallist:
#                 if row[shapejoincol2] == adminval:
#                     if int(row[col]) == -9999: #use -9999 as a key for no data
#                         vals.append('')
#                     else:
#                         vals.append(row[col])
#             try:
#                 maxval = max(v for v in vals if v <> '')
#             except:
#                 maxval = "None"
#             try:
#                 minval = min(vals)
#             except:
#                 minval = "None"
#             maxval = str(int(round(maxval *100,0)))
#             minval = str(int(round(minval *100,0)))
#             newdict[adminval] = minval + "% to "+ maxval + "%"
#         coldict[col] = newdict

#     for col in addcols:
#         vals = coldict[col]
#         del rows
#         rows = arcpy.UpdateCursor(shapefile2)
#         for row in rows:
#             shpjoinval = row.getValue(shapejoincol2)
#             try:
#                 row.setValue(str(col),str(vals[shpjoinval]))
#                 rows.updateRow(row)
#             except:
#                 pass

# def shp_maxmin_byfield(shapefile, shapejoincol, aggregation_column, maxmin_cols, percent_change = False, diff_lc = False):
#     """This function will loop through a shapefile and group values based upon the specified 'aggregation_column'. The function will then calculate the maximum and minimum for each of the maxmin_cols specified. A new field will be added to the shapefile that includes "L_" and the first 8 characters of each value in the maxmin_cols. Use these new columns to label the max and min values when creating maps. Returns the new label columns. If percent_change = True, the labels will represent a percentage. If diff_lc is true, the labels will have 2 digits."""
#     newcols = []
#     for col in maxmin_cols:
#         newcols.append("L_" + col[:8])
#     shp_addcols(shapefile, newcols, "STRING")
#     for col in maxmin_cols:
#         col =  col[:10]
#         rows = arcpy.UpdateCursor(shapefile)
#         shpvallist = []
#         for row in rows:
#             adminval = row.getValue(aggregation_column)
#             maxminkey = str(row.getValue(shapejoincol))
#             val = float(row.getValue(col))
#             shpvallist.append([adminval, maxminkey, val])
#         del row, rows
#         mydict = {}
#         shpvallist.sort(key = operator.itemgetter(0,2)) #must sort to use itertools.groupby
#         for k,g in itertools.groupby(shpvallist, operator.itemgetter(0)):
#             vals = list(g)
#             if len(vals) == 0:
#                 continue
#             elif len(vals) == 1:
#                 if float(vals[0][2]) == -9999:
#                     continue
#                 maxval =  list(vals[0])
#                 minval =  list(vals[0])
#             else:
#                 vals = [y for y in vals if y[2] <> -9999]
#                 vals = sorted(vals, key = lambda x: x[2])
#                 minval = list(vals[0])
#                 maxval = list(vals[-1])
#             try:
#                 if percent_change == True:
#                     maxval[2] = "{:.0%}".format(maxval[2])
#                     minval[2] = "{:.0%}".format(minval[2])
#                 elif diff_lc == True:
#                     maxval[2] = "{:.2f}".format(maxval[2])
#                     minval[2] = "{:.2f}".format(minval[2])
#             except:
#                 print "Had issues formatting the number: " + maxval[2] + " or " + minval[2]
#             mydict[k]= {'maxpost':maxval[1],'maxchange':maxval[2],'minpost':minval[1],'minchange':minval[2]}
#             del minval, maxval
#         rows = arcpy.UpdateCursor(shapefile)
#         for row in rows:
#             adminval = row.getValue(aggregation_column)
#             maxminkey = row.getValue(shapejoincol)
#             if maxminkey == mydict[adminval]['maxpost']:
#                     row.setValue(str('L_' + col[:8]),mydict[adminval]['maxchange'])
#                     rows.updateRow(row)
#             elif maxminkey == mydict[adminval]['minpost']:
#                     row.setValue(str('L_' + col[:8]),mydict[adminval]['minchange'])
#                     rows.updateRow(row)
#         del row, rows
#     print newcols
#     return newcols

# def shp_calcfield(shapefile, fieldname, py_expression):
#     """Calculate values for a field given a python expression as a string. The py expression should be formatted with ! characters before and after the field name. ie.py_expression ='str(!POSTCODE!) + '_' + str(!JOIN!) """
#     arcpy.CalculateField_management (shapefile, fieldname, py_expression,"Python")


# def mxd_getlist():
#     """ Returns a list of mxdfiles in the C:\workspace\MXDs folder"""
#     return glob(os.path.join("C:/Mapping_Project/MXDs","*.mxd"))

# def mxd_getlayers(mxds):
#     """Prints the available layers in the mxd document. A string version of the layer name is returned. mxd_getlayers(mxds = 'mxdpath' or ['mxdpath1','mxdpath2'])"""

#     lyrlist = []
#     if isinstance(mxds, list):
#         for mxdpath in mxds:
#             print mxdpath
#             mxd = arcpy.mapping.MapDocument(mxdpath)
#             i = 0
#             for lyr in arcpy.mapping.ListLayers(mxd):
#                 lyrlist.append([os.path.basename(mxdpath), str(lyr.name), i])
#                 i += 1
#         print 'MXD/tLAYER/tLAYER_INDEX' #adding cols to what is getting printed
#         for row in lyrlist:
#             print row
#         return lyrlist
#     elif isinstance(mxds,str):
#         mxd = arcpy.mapping.MapDocument(mxds)
#         i = 0
#         for lyr in arcpy.mapping.ListLayers(mxd):
#             lyrlist.append([os.path.basename(mxds), str(lyr.name), i])
#             i += 1
#         print 'MXD/tLAYER/tLAYER_INDEX'
#         for row in lyrlist:
#             print row
#         return lyrlist
#     else:
#         print "The mxd needs to be formatted as a list, not a string. add brackets around the variable ['mxdpath']"



# def map_create2(mxds,shapefile,mapcols, labelfields, symbology, prefix = False):
#     """This function will create maps for all mxds specified and all fields in the mapcols list. The symbology options = 'Percent_Change' and 'Diff_LC'. This function allows specification of different label fields for the mapcols labels. ie use mapcols as difference in loss cost, but label the max and min percent change column. The mapcols and labelfields lists must be ordered in the same order so that the first value of mapcols will get labelled with the first value in labelfields."""

#     i= 0
#     for col in mapcols:
#         mapcols[i] = col[:10]
#         i += 1

#     if isinstance(mxds, str):
#         newmxd = []
#         newmxd.append(mxds)
#         mxds = newmxd
#     if isinstance(mapcols, str):
#         newmapcols = []
#         newmapcols.append(mapcols)
#         mapcols = newmapcols

#     mapresolution = 300 #300 is common.

#     if symbology.lower() == "percent_change":
#         symbpath = arcpy.mapping.Layer("C:/Mapping_Project/MXDs/Symbology/PercentChange.lyr")
#     elif symbology.lower() == "diff_lc":
#         symbpath = arcpy.mapping.Layer('C:/Mapping_Project/MXDs/Symbology/DifferenceinLossCost.lyr')
#     elif symbology [-4:] == '.lyr':
#         symbpath = arcpy.mapping.Layer(symbology)
#     else:
#         print "You need to choose a symbology type: 'Percent_Change','Diff_LC', or a layerfile path"
#         return
#     for mxd in mxds:
#         mxdobj = arcpy.mapping.MapDocument(mxd)
#         df = arcpy.mapping.ListDataFrames(mxdobj)[0] #leave as default for these maps(will it change for other perils????)

#         for lyr in arcpy.mapping.ListLayers(mxdobj):
#             if lyr.name == os.path.basename(shapefile).replace(".shp",""):
#                 lyr.symbologyType == "GRADUATED_COLORS"
#                 for field, label in zip(mapcols, labelfields):
#                     field = field [:10]
#                     label = label [:10]
#                     # print field, label

#                     arcpy.mapping.UpdateLayer(df, lyr, symbpath, True)
#                     lyr.symbology.valueField = field
#                     expres = "["+label+"]"
#                     # print expres
#                     if lyr.supports("LABELCLASSES"):
#                         lyr.showLabels = True
#                         for lblClass in lyr.labelClasses:
#                             lblClass.expression = expres
#                             lblClass.SQLQuery = field +" <> -9999"
#                             lblClass.showClassLabels = True
#                     arcpy.RefreshActiveView()

#                     if prefix:
#                         outpath = 'C:/Mapping_Project/Out/'+ prefix +'_' + os.path.basename(mxd).rstrip('.mxd') +'_' + field +'.jpg'
#                         print "Making a map at:", outpath
#                     else:
#                         outpath = 'C:/Mapping_Project/Out/'+ os.path.basename(mxd).rstrip('.mxd') +'_' + field + '.jpg'
#                         "Making a map at:", outpath
#                     arcpy.mapping.ExportToJPEG(mxdobj, outpath, resolution=mapresolution)


# def map_create3(mxds,shp1, shp2,  mapcols,symbology, labels1 = False,labels2 = False, prefix = None):
#     """This function will update the symbology and labels for two shapefiles. They must have the same mapcols. This function will then create maps for all mxds specified and all fields in the mapcols list. The symbology options = 'Percent_Change' and 'Diff_LC'.  Symbology options are diff_lc and percent_change. If labels1 or labels2 is True, the mapcols will be labelled """

#     i= 0
#     for col in mapcols:
#         mapcols[i] = col[:10]
#         i += 1

#     if isinstance(mxds, str):
#         newmxd = []
#         newmxd.append(mxds)
#         mxds = newmxd
#     if isinstance(mapcols, str):
#         newmapcols = []
#         newmapcols.append(mapcols)
#         mapcols = newmapcols

#     mapresolution = 300 #300 is common.

#     if symbology.lower() == "percent_change":
#         symbpath = arcpy.mapping.Layer("C:/Mapping_Project/MXDs/Symbology/PercentChange.lyr")
#     elif symbology.lower() == "diff_lc":
#         symbpath = arcpy.mapping.Layer('C:/Mapping_Project/MXDs/Symbology/DifferenceinLossCost.lyr')
#     elif symbology [-4:] == '.lyr':
#         symbpath = arcpy.mapping.Layer(symbology)
#     else:
#         print "You need to choose a symbology type: 'Percent_Change','Diff_LC', or a layerfile path"
#         return
#     for mxd in mxds:
#         mxdobj = arcpy.mapping.MapDocument(mxd)
#         df = arcpy.mapping.ListDataFrames(mxdobj)[0] #leave as default for these maps(will it change for other perils????)

#         for lyr in arcpy.mapping.ListLayers(mxdobj):
#             if lyr.name == os.path.basename(shp1).replace(".shp",""):
#                 lyr1 = lyr
#             elif lyr.name == os.path.basename(shp2).replace(".shp",""):
#                 lyr2 = lyr

#         lyr1.symbologyType == "GRADUATED_COLORS"
#         lyr2.symbologyType == "GRADUATED_COLORS"

#         for field in mapcols:
#             field = field [:10]
#             # print os.path.basename(mxd).rstrip(".mxd"), field
#             arcpy.mapping.UpdateLayer(df, lyr1, symbpath, True)
#             if symbology.lower() == "percent_change":
#                 expres = "str(int(round(float(["+field+"])*100,0))) + '%'"
#             elif symbology.lower() == "diff_lc":
#                 expres = "str(int(round(float(["+field+"])*100,0)))"
#             lyr1.symbology.valueField = field
#             if labels1:
#                 if lyr1.supports("LABELCLASSES"):
#                     lyr1.showLabels = True
#                 # print "Layer name: " + lyr1.name
#                     for lblClass in lyr1.labelClasses:
#                         lblClass.expression = expres
#                         lblClass.SQLQuery = field +" <> -9999"
#                         lblClass.showClassLabels = True
#             else:
#                 lyr1.showLabels = False

#             arcpy.mapping.UpdateLayer(df, lyr2, symbpath, True)
#             lyr2.symbology.valueField = field

#             if labels2:
#                 if lyr2.supports("LABELCLASSES"):
#                     lyr2.showLabels = True
#                 # print "Layer name: " + lyr2.name
#                     for lblClass in lyr2.labelClasses:
#                         lblClass.expression = expres
#                         lblClass.SQLQuery = field +" <> -9999"
#                         lblClass.showClassLabels = True
#             else:
#                 lyr2.showLabels = False

#             arcpy.RefreshActiveView()
#             if prefix:
#                 outpath = 'C:/Mapping_Project/Out/'+ prefix +'_' + os.path.basename(mxd).rstrip('.mxd') +'_' + field +'.jpg'
#                 print "Making a map at:", outpath
#             else:
#                 outpath = 'C:/Mapping_Project/Out/'+ os.path.basename(mxd).rstrip('.mxd') +'_' + field + '.jpg'
#                 "Making a map at:", outpath
#             arcpy.mapping.ExportToJPEG(mxdobj, outpath, resolution=mapresolution)


# ###############################################################################


# #################NOT WORKING########################
# def map_create4(mxds,shapefile,shpsubregioncol, mapcols, labelfields, symbology, prefix = False):
#     """This function will create maps for all mxds specified and all fields in the mapcols list. The symbology options = 'Percent_Change' and 'Diff_LC'. This function allows specification of different label fields for the mapcols labels. ie use mapcols as difference in loss cost, but label the max and min percent change column. The mapcols and labelfields lists must be ordered in the same order so that the first value of mapcols will get labelled with the first value in labelfields. This function will zoom to the different layer attributes specified in the shpsubregioncol field. Currently it's set to only do countries 'be', 'de', and 'uk'"""
#     i= 0
#     for col in mapcols:
#         mapcols[i] = col[:10]
#         i += 1
#     i = 0
#     for col in labelfields:
#         labelfields[i] = col[:10]
#         i += 1

#     if isinstance(mxds, str):
#         newmxd = []
#         newmxd.append(mxds)
#         mxds = newmxd
#     if isinstance(mapcols, str):
#         newmapcols = []
#         newmapcols.append(mapcols)
#         mapcols = newmapcols
#     if isinstance(labelfields, str):
#         newlabelfields = []
#         newlabelfields.append(mapcols)
#         labelfieldsfields = newlabelfields

#     mapresolution = 300 #300 is common.

#     if symbology.lower() == "percent_change":
#         symbpath = arcpy.mapping.Layer("C:/Mapping_Project/MXDs/Symbology/PercentChange.lyr")
#     elif symbology.lower() == "diff_lc":
#         symbpath = arcpy.mapping.Layer('C:/Mapping_Project/MXDs/Symbology/DifferenceinLossCost.lyr')
#     elif symbology [-4:] == '.lyr':
#         symbpath = arcpy.mapping.Layer(symbology)
#     else:
#         print "You need to choose a symbology type: 'Percent_Change','Diff_LC', or a layerfile path"
#         return

#     rows = arcpy.SearchCursor(shapefile)
#     adminIDs = []
#     for row in rows:
#         val = row.getValue(shpsubregioncol)
#         if val not in adminIDs:
#             adminIDs.append(val)
#     del rows
#     for mxd in mxds:
#         mxdobj = arcpy.mapping.MapDocument(mxd)
#         df = arcpy.mapping.ListDataFrames(mxdobj)[0] #leave as default for these maps(will it change for other perils????)
#         for lyr in arcpy.mapping.ListLayers(mxdobj):
#             if lyr.name == "EUFL_RL15_Zips_Cover":
#                 lyr2 = lyr
#             elif lyr.name == "EUFL_RL15_Zips_Cover2":
#                 lyr3 = lyr
#         for lyr in arcpy.mapping.ListLayers(mxdobj):
#             if lyr.name == os.path.basename(shapefile).replace(".shp",""):
#                 lyr.symbologyType == "GRADUATED_COLORS"
#                 for field, label in zip(mapcols, labelfields):
#                     field = field [:10]
#                     label = label [:10]
#                     arcpy.mapping.UpdateLayer(df, lyr, symbpath, True)
#                     lyr.symbology.valueField = field
#                     expres = "str(int(round(float(["+label+"]) *100,0))) + '%'"
#                     print expres
#                     if lyr.supports("LABELCLASSES"):
#                         print "here"
#                         lyr.showLabels = True
#                         for lblClass in lyr.labelClasses:
#                             lblClass.expression = expres
#                             lblClass.SQLQuery = field +" <> -9999"
#                             lblClass.showClassLabels = True

#                     for adminID in adminIDs:
#                         if adminID[:2] in ['BE','UK','GM']:
#                             adminID = str(adminID)

#                             query1 = '"'+ shpsubregioncol + '" = ' + "'" + adminID + "'"
#                             query2 = '"'+ shpsubregioncol + '" <> ' + "'" + adminID + "'"
#                             query3 = '"'+ shpsubregioncol + '" <> ' + "'" + adminID + "'"
#                             print shpsubregioncol, adminID, query1
#                             lyr.definitionQuery =  query1
#                             lyr2.definitionQuery = query2
#                             lyr3.definitionQuery = query3

#                             ext = lyr.getSelectedExtent(True)
#                             df.extent = ext
#                             # df.panToExtent(lyr.getSelectedExtent())
#                             # df.zoomToSelectedFeatures()
#                             arcpy.RefreshActiveView()
#                             if prefix:
#                                 outpath = 'C:/Mapping_Project/Out/'+ prefix +'_' + os.path.basename(mxd).rstrip('.mxd') +'_' + field +'.jpg'
#                                 print "Making a map at:", outpath
#                             else:
#                                 outpath = 'C:/Mapping_Project/Out/'+ os.path.basename(mxd).rstrip('.mxd') +'_' + field + '.jpg'
#                                 "Making a map at:", outpath
#                             arcpy.mapping.ExportToJPEG(mxdobj, outpath, resolution=mapresolution)
