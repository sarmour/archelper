import imp

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
# print shpcols

# mapping_files.shp_removecols(shpfile, ['LC_Haz','LC_Vuln','LC_PLA_Win','LC_Overall','PC_Haz','PC_Vuln','PC_PLA_Wind','PC_Overall','L_PC_Haz','L_PC_Vuln','L_PC_PLA_W','L_PC_Overa'])


for csvfile in csvfiles:
    mapping_files.shp_joincsv(csvfile, shpfile,  'JOIN', 4, 6)

    mappingcol = ['TIV_USD']

    mxds = mapping_files.mxd_getlist()
    print mxds

    lyrfile = "C:\Mapping_Project\MXDs\Symbology\TIV_Symb_Millions.lyr"
    mapping_files.map_create1(mxds, shpfile, mappingcol, lyrfile, labels = False)
