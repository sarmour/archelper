"""This script will create TIV maps."""
import imp
# import os
# import arcpy
import csv
# import operator
import arcpy

mapping_files = imp.load_source('mapping_files',r'c:\archelper\archelper\mapping_files.py')

csvfile = r"C:\archelper\scripts\Dev\test.csv"
shpfile = r"C:\Mapping_Project\MXDs\Symbology\SymbSource\EUWS2011_CRESTAwJoinCol.shp"
shpfiletable = r"C:\mapping_project\EUFL_PAT_Data.gdb\EUFL_RL15_Zips"
csvjoinindex = 0
shapefilejoincol = "JOIN"
csvstartfield = 1
print mapping_files.shp_getcols(shpfile)

cols = ['CRESTA_ID', 'NUM_CRESTA', 'COUNTRY', 'RAW_CRESTA', 'COUNTRY1','GR_AAL', 'GR_STDDEV', 'RP2_GU', 'RP5_GU', 'RP10_GU', 'RP25_GU', 'RP50_GU', 'RP100_GU', 'RP200_GU', 'RP250_GU', 'RP500_GU', 'RP1000_GU', 'RP5000_GU', 'RP10000_GU', 'RP2_GR', 'RP5_GR', 'RP10_GR', 'RP25_GR', 'RP50_GR', 'RP100_GR', 'RP200_GR', 'RP250_GR', 'RP500_GR', 'RP1000_GR', 'RP5000_GR', 'RP10000_GR', 'TIV_int']
mapping_files.shp_removecols(shpfile, cols)
