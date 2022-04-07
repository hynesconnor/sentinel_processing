#imports
import os
import rasterio
import glob

# constants
CWD = os.getcwd()
OUTPUT_DIR = '/data/processed/'
J_DRIVER = 'JP2OpenJPEG' # driver to process jp2 files
G_DRIVER = 'Gtiff' # driver to process geotiff files

# parameters to be adjusted
BAND_COUNT = 3 # used to control the number of bands being written. (rgb default = 3)
FOLDER = 'sentinelLV' # satellite folder, change to desired satellite data within the image folder

# creates array of band names, returns band names and path to bands
def get_file_names():
    img_folder = CWD + '/data/image/' + FOLDER + '/GRANULE/'
    IMG_DIR = img_folder + os.listdir(img_folder)[0] + '/IMG_DATA/'
    band_names = glob.glob(IMG_DIR + '*.jp2') # all files with .jp2 file extension
    
    return band_names, IMG_DIR

# reads downloaded satellite bands, returns array of rgb bands
# band_names: array of satellite bands, IMG_DIR: path to satellite bands
def band_process(band_names, IMG_DIR):
    repeat = list(range(1, 4)) # range can be adjusted to select different bands. Default: (2, 3, 4):(blue, green, red)
    bands = []
    for x in repeat:
        bands.append(rasterio.open(band_names[x], driver = J_DRIVER)) # + IMG_DIR

    return bands

# image processing, writes RGB bands to a singular TIFF file that can be imported to ArcGIS
# bands: array of opened satellite bands
def band_write(bands):
    trueColor = rasterio.open(CWD + OUTPUT_DIR + 'rgb/' + FOLDER + '_rgb.tif',
                             'w',
                             driver = G_DRIVER,
                             height = bands[0].height,
                             width = bands[0].width,
                             count = BAND_COUNT, # 12
                             crs = bands[0].crs,
                             dtype = bands[0].dtypes[0],
                             transform = bands[0].transform)
    
    desc = BAND_COUNT # int controlling iteration
    
    # for each band, write band to .tif file
    for i in bands:
        trueColor.write(i.read(1), desc)
        desc = desc - 1
        
    trueColor.close()

def rgb():
    band_names, IMG_DIR = get_file_names()
    bands = band_process(band_names, IMG_DIR)
    band_write(bands)
    print("Completed.")

rgb()

# This section processes the satellite bands using zonal analysis to detect greenspace.

# imports
import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
np.seterr(invalid='ignore') # ignores nan values in satellite bands

# opens bands used to zonal analysis
band_names, IMG_DIR = get_file_names() 
b2 = rasterio.open(band_names[1]) # BLUE
b3 = rasterio.open(band_names[2]) # GREEN
b4 = rasterio.open(band_names[3]) # RED
b8 = rasterio.open(band_names[7]) # NIR
    
# calculates NDVI (Normalized Difference Vegetation Index), returns ndvi as numpy dataframe
def ndvi_calc():
    red = b4.read()
    nir = b8.read()

    ndvi = np.zeros(red.shape, dtype = rasterio.float64)
    ndvi = (nir.astype(float) - red.astype(float)) / (nir + red) # (b8 - b4) / (b8 + b4)
    
    return ndvi

# calculates NDWI (Normalized Difference Water Index), returns ndwi as numpy dataframe
def ndwi_calc():
    green = b3.read()
    nir = b8.read()

    ndwi = np.zeros(green.shape, dtype = rasterio.float64)
    ndwi = (nir.astype(float) - green.astype(float)) / (nir + green) # (b8 - b4) / (b8 + b4
    
    return ndwi

# exports normalized difference index to .tif
# data: ndvi or ndwi data, folder: location to write .tif, name: name of .tif file
def export_normalized_diff(data, folder, name):    
    export_loc = CWD + '/data/processed/' + folder + name
    with rasterio.open(export_loc, 'w',
                        driver = G_DRIVER,
                        height = b4.height,
                        width = b4.width,
                        count = 1,  
                        crs = b4.crs,
                        dtype = rasterio.float64,
                        transform = b4.transform) as table:
        table.write(data)
        
# reports and writes ndvi statistics
def ndvi():
    ndvi = ndvi_calc()
    export_normalized_diff(ndvi, 'ndvi/', FOLDER + '_ndvi.tif')
    print('Mean vegitation density of raster: ' + np.nanmean(ndvi[0]).astype(str))
    print('Completed.')

# reports and writes ndwi statistics 
def ndwi():
    ndwi = ndwi_calc()
    export_normalized_diff(ndwi, 'ndwi/', FOLDER + '_ndwi.tif')
    #print('Mean water density of raster: ' + np.nanmean(ndwi[0]).astype(str))
    print('Completed.')
    
ndvi()
ndwi()

'''
# histogram of ndvi values, useful for visualizing the range of values
flat_raster = np.ma.compressed('#') # direct flat_raster to ndvi.tif file

fig = plt.figure(figsize=(8,11))
ax = fig.add_subplot(1,1,1)

ax.hist(flat_raster, 10, normed=0, histtype='bar',
    align='mid')
'''
