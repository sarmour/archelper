"""This script will create TIV maps."""
import imp
import os

internal_files = imp.load_source('internal_files', r'C:\archelper\archelper\internal_files.py')
mapping_files = imp.load_source('mapping_files',r'c:\archelper\archelper\mapping_files.py')


shpfile = "C:\Mapping_Project\Shapefiles\EUFL_RL15_Zips.shp"
shpjoincol = "JOIN"

csvfile = "C:\Mapping_Project\CSVs\TestPC_2.csv"
# folderpath = "C:\workspace"
# csvfiles = mapping_files.get_csvlist(folderpath)
# print csvfiles

# csvcols = mapping_files.csv_getcols(csvfile)
# print csvcols
# shpcols = mapping_files.shp_getcols(shpfile)
# print shpcols

mappingcols = ['LC_Haz', 'LC_Vuln', 'LC_PLA_Wind', 'LC_Overall']
perchangecols = ['PC_Haz', 'PC_Vuln', 'PC_PLA_Wind', 'PC_Overall']
allcols = list(mappingcols) #for deleting data after mapping process

# for csvfile in csvfiles: ##start loop for entire script here
# mapping_files.shp_joincsv(csvfile, shpfile,  shpjoincol, 0, 1)
filename = os.path.basename(csvfile).rstrip('.csv')

mxds = mapping_files.mxd_getlist()
print mxds

####################CREATE THE EUROPE MAPS############################
# eu_mxd = ['C:/Mapping_Project/MXDs\\EUFL_PC_Europe.mxd']
# mapping_files.map_create1(eu_mxd, shpfile, mappingcols, 'diff_lc', prefix = filename)


####################CREATE THE COUNTRY MAPS##########################
# countrymxds = ['C:/Mapping_Project/MXDs\\EUFL_PC_Belgium.mxd', 'C:/Mapping_Project/MXDs\\EUFL_PC_Germany.mxd', 'C:/Mapping_Project/MXDs\\EUFL_PC_UK.mxd']

# labels = mapping_files.shp_maxmin_byfield(shpfile, shpjoincol, 'Admin1ID', perchangecols, percent_change = True)

# mapping_files.map_create2(countrymxds,shpfile,mappingcols, labels, "diff_lc", filename)

# for val in labels:
#     allcols.append(val)

####################CREATE THE SUB-COUNTRY MAPS######################

# subcountrymxds =
# labels = mapping_files.shp_maxmin_byfield(shpfile, shpjoincol, 'CNY_CRESTA', perchangecols, percent_change = True)


mapping_files.map_creat4(mxds, shapefile,'CNY_CRESTA',mappingcols, labels, "diff_lc", filename)






####################REMOvE COLS ADDED TO SHPFILE##############################
mapping_files.shp_removecols(shpfile, allcols)
