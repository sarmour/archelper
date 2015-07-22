import imp
import arcpy
import operator
import itertools
import csv

mapping_files = imp.load_source('mapping_files',r'c:\archelper\archelper\mapping_files.py')


def shp_maxmin_byfield(shapefile, shapejoincol, aggregation_column, maxmin_cols):
    newcols = []
    for col in maxmin_cols:
        newcols.append("L_" + col[:8])
# mapping_files.shp_addcols(shapefile, newcols, "STRING")
    rows = arcpy.UpdateCursor(shapefile)
    shpvallist = []
    i = 0
    for row in rows:
        adminval = row.getValue(aggregation_column)
        postcode = str(row.getValue(shapejoincol))
        val = float(row.getValue('PC_Haz'))
        shpvallist.append([adminval, postcode, val])
    del row, rows
    shpvallist.sort(key = operator.itemgetter(0,2))
    ##print shpvallist[:10]
    #mylist = []
    mydict = {}

    templist = []

    for k,g in itertools.groupby(shpvallist, operator.itemgetter(0)):
        vals = list(g)

        if len(vals) == 0:
            continue
        elif len(vals) == 1:
            if float(vals[0][2]) == -9999:
                continue
            maxval = minval = vals[0]
        else:
            for i, item in enumerate(vals):
                if vals[i][2] == -9999:
                    # print item
                    vals.remove(item) ####This part isnt working
            vals = sorted(vals, key = lambda x: x[2])
            minval = vals[0]
            maxval = vals[-1]
        mydict[k]= {'maxpost':maxval[1],'maxchange':maxval[2],'minpost':minval[1],'minchange':minval[2]}

    rows = arcpy.UpdateCursor(shapefile)
    for row in rows:
        adminval = row.getValue(aggregation_column)
        postcode = row.getValue(shapejoincol)
        if postcode == mydict[adminval]['maxpost']:
                row.setValue(str('L_PC_Haz'),float(mydict[adminval]['maxchange']))
                rows.updateRow(row)
        elif postcode == mydict[adminval]['minpost']:
                row.setValue(str('L_PC_Haz'),float(mydict[adminval]['minchange']))
                rows.updateRow(row)
            # print postcode
            # print [adminval, mydict[adminval]['maxpost'], mydict[adminval]['minpost']]
    del row, rows

    with open('C:/workspace/code_debugger.csv', 'w') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        for item in templist:
            wr.writerow(item)

shpfile = "C:\Mapping_Project\Shapefiles\EUFL_RL15_Zips.shp"
shpjoincol = "JOIN"
perchangecols = ['PC_Haz', 'PC_Vuln', 'PC_PLA_Wind', 'PC_Overall']
labels = shp_maxmin_byfield(shpfile, shpjoincol, 'Admin1ID', perchangecols)
