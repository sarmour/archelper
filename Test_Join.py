"""This script will create TIV maps."""
import imp
import os

internal_files = imp.load_source('internal_files', r'C:\archelper\archelper\internal_files.py')
mapping_files = imp.load_source('mapping_files',r'c:\archelper\archelper\mapping_files.py')

csvfile = "C:\workspace/130916_Aviva_2014Rnwl_UKFL_v13_EDM.csv"
shpfile = "C:\Mapping_Project\Shapefiles\EUFL_RL15_Zips.shp"

cols = mapping_files.shp_getcols(shpfile)
print cols
mapping_files.shp_removecols(shpfile, ['TIV_USD'])
# mapping_files.shp_joincsv(csvfile, shpfile,  'JOIN', 1, 3)
