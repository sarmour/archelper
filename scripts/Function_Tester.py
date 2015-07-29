"""This script will create TIV maps."""
import imp
import os

internal_files = imp.load_source('internal_files', r'C:\archelper\archelper\internal_files.py')
mapping_files = imp.load_source('mapping_files',r'c:\archelper\archelper\mapping_files.py')


shpfile = "C:\Mapping_Project\Shapefiles\EUFL_RL15_Zips.shp"

shpcols = mapping_files.shp_getcols(shpfile)
print shpcols
