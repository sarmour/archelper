"""This script will create TIV maps."""
import imp
# import os
# import arcpy
import csv
import operator
import arcpy

mapping_files = imp.load_source('mapping_files',r'c:\archelper\archelper\mapping_files.py')

csvfile = r"C:\archelper\scripts\Dev\test.csv"
shpfile = r"C:\archelper\scripts\Dev\test.shp"
csvjoinindex = 0
shapefilejoincol = "JOIN"
csvstartfield = 1






print csv_checkmissingshpvals(csvfile, 0,  shpfile, shapefilejoincol)
