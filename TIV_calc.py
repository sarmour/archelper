"""This script will create TIV maps."""
import imp
import os

internal_files = imp.load_source('internal_files', r'C:\archelper\archelper\internal_files.py')
mapping_files = imp.load_source('mapping_files',r'c:\archelper\archelper\mapping_files.py')



# csvfile = "C:\workspace/130916_Aviva_2014Rnwl_UKFL_v13_EDM.csv"
shpfile = "C:\Mapping_Project\Shapefiles\EUFL_RL15_Zips.shp"

folderpath = "C:\workspace"
csvfiles = mapping_files.get_csvlist(folderpath)
print csvfiles
# csvcols = mapping_files.csv_getcols(csvfile)
# print csvcols
# shpcols = mapping_files.shp_getcols(shpfile)
# print shpcols'

# removecols = ['portnum','portname','CountryRMS','join_col','peril','TIV_USD']
# mapping_files.shp_removecols(shpfile, removecols)


for csvfile in csvfiles:
    print csvfile
    mapping_files.shp_joincsv(csvfile, shpfile,  'JOIN', 1, 3)

    mappingcol = ['TIV_USD']

    mxds = mapping_files.mxd_getlist()
    print mxds
    prefix = os.path.basename(csvfile).rstrip('.csv')
    print prefix
    lyrfile = "C:\Mapping_Project\MXDs\Symbology\TIV_Symb_Millions.lyr"
    mapping_files.map_create1(mxds, shpfile, mappingcol, lyrfile,'', prefix)
