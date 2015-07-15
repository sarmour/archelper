import imp
import arcpy
import operator
import itertools

mapping_files = imp.load_source('mapping_files',r'c:\archelper\archelper\mapping_files.py')

def shp_maxmin_byfield(shapefile, shapejoincol, aggregation_column, maxmin_cols):
    newcols = []
    for col in maxmin_cols:
        newcols.append("L_" + col[:8])
    # mapping_files.shp_addcols(shapefile, newcols, "STRING")
    rows = arcpy.SearchCursor(shapefile)
    shpvallist = []
    i = 0
    for row in rows:
        adminval = row.getValue(aggregation_column)
        postcode = row.getValue(shapejoincol)
        val = row.getValue('PC_Haz')
        shpvallist.append([adminval, postcode, val])

    for row in shpvallist:
        row[2] = row[2].replace('-9999','')

    shpvallist.sort(key = operator.itemgetter(0,2))
    print shpvallist[:10]
    mylist = []
    for k,g in itertools.groupby(shpvallist, operator.itemgetter(0)):
        vals = sorted(g, key = lambda x: x[2])
        minval = vals[0]
        maxval = vals[-1]
        mylist.append((('min', minval),('max',maxval)))
    print mylist[:10]
    # prev = shpvallist[0][0]
    # minpost = shpvallist[0][1]
    # minval = shpvallist[0][2]

# for x, y, g in itertools.groupby(shpvallist, key = )


shpfile = "C:\Mapping_Project\Shapefiles\EUFL_RL15_Zips.shp"
shpjoincol = "JOIN"
perchangecols = ['PC_Haz', 'PC_Vuln', 'PC_PLA_Wind', 'PC_Overall']
labels = shp_maxmin_byfield(shpfile, shpjoincol, 'Admin1ID', perchangecols)
