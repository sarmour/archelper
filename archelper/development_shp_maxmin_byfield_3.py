import imp
import arcpy
import operator
import itertools
import csv

mapping_files = imp.load_source('mapping_files',r'c:\archelper\archelper\mapping_files.py')

def shp_maxmin_byfield(shapefile, shapejoincol, aggregation_column, maxmin_cols):
    """ This function will add fields to the shapefile and calculate the max and min values associated with the aggregation_column. The new columns will be labelled with 'L_' and the first 8 characters of the maxmin_cols. This function returns the column names. This code assumes the maxmin_cols are numeric. -9999 is treated as No Data."""

    newcols = []
    for col in maxmin_cols:
        newcols.append("L_" + col[:8])
    mapping_files.shp_addcols(shapefile, newcols, "STRING")

    for col in maxmin_cols:
        col =  col[:10]
        rows = arcpy.UpdateCursor(shapefile)
        shpvallist = []
        i = 0
        for row in rows:
            adminval = row.getValue(aggregation_column)
            maxminkey = str(row.getValue(shapejoincol))
            val = float(row.getValue(col))
            shpvallist.append([adminval, maxminkey, val])
        del row, rows
        mydict = {}
        shpvallist.sort(key = operator.itemgetter(0,2)) #must sort to use itertools.groupby
        for k,g in itertools.groupby(shpvallist, operator.itemgetter(0)):
            vals = list(g)
            if len(vals) == 0:
                continue
            elif len(vals) == 1:
                if float(vals[0][2]) == -9999:
                    continue
                maxval = minval = vals[0]
            else:
                vals = [y for y in vals if y[2] <> -9999]
                vals = sorted(vals, key = lambda x: x[2])
                try:
                    minval = vals[0]
                    maxval = vals[-1]
                except:
                    print vals
            mydict[k]= {'maxpost':maxval[1],'maxchange':maxval[2],'minpost':minval[1],'minchange':minval[2]}
            del minval, maxval
        rows = arcpy.UpdateCursor(shapefile)
        for row in rows:
            adminval = row.getValue(aggregation_column)
            maxminkey = row.getValue(shapejoincol)
            if maxminkey == mydict[adminval]['maxpost']:
                    row.setValue(str('L_' + col[:8]),float(mydict[adminval]['maxchange']))
                    rows.updateRow(row)
            elif maxminkey == mydict[adminval]['minpost']:
                    row.setValue(str('L_' + col[:8]),float(mydict[adminval]['minchange']))
                    rows.updateRow(row)
        del row, rows


shpfile = "C:\Mapping_Project\Shapefiles\EUFL_RL15_Zips.shp"
shpjoincol = "JOIN"
perchangecols = ['PC_Haz', 'PC_Vuln', 'PC_PLA_Wind', 'PC_Overall']
labels = shp_maxmin_byfield(shpfile, shpjoincol, 'Admin1ID', perchangecols)
