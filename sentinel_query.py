# imports
import os
import sys
from urllib import request
from datetime import date
import pandas as pd
import json
import zipfile
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt

# constants
CWD = os.getcwd()
URL = 'https://developers.google.com/public-data/docs/canonical/countries_csv'
COU_DIR = '/data/country/'
IMG_DIR = '/data/image/'
USER = '' # enter username
PASS = '' # enter password
DATE_END = date.today()

# adjustable search parameters
COUNTRY = 'US' # abbreviation of country. options here: 'https://developers.google.com/public-data/docs/canonical/countries_csv'
YEAR_SEARCH = 1 # how many previous years to query
CLOUD_COVER = [0, 10] # acceptable amount of cloud cover [start, end] (percentage)

# custom lat/long search
CUSTOM = False # False: no custom search, True: custom search
LAT, LONG = 0, 0 # custom latitude and longitude
CUS_NAME = '' # location name, used for directory naming

# creates necessary file directory for script.
def create_directory():
    if not os.path.exists(CWD + '/data'):
        cur_folder = CWD + '/data/'
        os.makedirs(cur_folder)
        main_dirs = ['country', 'image', 'processed']
        proc_dirs = ['ndvi', 'ndwi', 'rgb']
        for i in main_dirs:
            os.makedirs(cur_folder + i)
        for i in proc_dirs:
            os.makedirs(cur_folder + 'processed/' + i)

# requests country data from google, returns dataframe of country data.
# URL: web address of country data
def getCountry(URL):
    webpage = request.urlopen(URL)
    country_data = pd.read_html(webpage)[0]
    return country_data

# get desired country from user input, returns lat/long and country name
# countries: dataframe of country data
def countryData(countries):
    country_ab = COUNTRY
    row = countries[countries.country == country_ab]
    lat, long, cou_name = row.latitude.values[0], row.longitude.values[0], row.country.values[0]
    return(lat, long, cou_name)

# creates geojson from desired lat/long, used for footprint of API query, returns geojson filepath
# countries: dataframe of country data
def createGeoJson(countries):
    # if custom search, use custom location parameters
    if CUSTOM:
        lat, long, cou_name = LAT, LONG, CUS_NAME
    else:
        # get country information
        lat, long, cou_name = countryData(countries)
    
    # construct geojson file with lat/long to be used as footprint
    data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point", 
                    "coordinates": [long, lat]
                }
            }
        ]
    }
    
    # filepath where .geojson will be saved
    filepath = CWD + COU_DIR + cou_name + '.geojson'
    
    # writes geojson file to directory
    with open(filepath, "w", encoding = 'utf-8') as f:
        json.dump(data, f, ensure_ascii = False, indent = 4)
    f.close()
    
    return filepath
    
# checks if satellite data for location has already been downloaded. If so, aborts execution
# name: title of location queried, compared against existing files
def check_library(name):
    dirs = os.listdir(CWD + IMG_DIR) # dataframe of IMG file directory
    
    # for each file in directory, check for matching file names 
    for i in dirs:
        if ('sentinel' + name) == i:  
            sys.exit('Satellite data for this location already exists. Check image directory and adjust parameters.')

# connects to sentinelAPI with credentials, returns api
def sentinel_contact():
    api = SentinelAPI(USER, PASS, 'https://apihub.copernicus.eu/apihub')
    
    return api

# determines how many years to query based on YEAR_SEARCH variable, returns start date
def getStartDate():
    DATE_START = DATE_END - pd.DateOffset(years = YEAR_SEARCH)
    
    return DATE_START

# reads geojson footprint, requests based on search parameters, returns sorted dataframe of products
# filepath: path to geojson footrpint, api: api connection to sentinel servers
def sentinel_product(filepath, api):
    # reads geojson
    footprint = geojson_to_wkt(read_geojson(filepath))
    
    # receives valid satellite data based on search parameters 
    products = api.query(footprint,
                         date = (getStartDate(), DATE_END),
                         platformname = 'Sentinel-2',
                         cloudcoverpercentage = CLOUD_COVER)

    # stores data in sorted dataframe, most recent data first
    products_df = api.to_dataframe(products).sort_values(by = ['summary'], ascending = False)

    return products_df

# uses product dataframe parameter to download first satellite imagery, returns title of file
# products_df: sorted df of satellite data, api: api connection to sentinel servers
def sentinel_download(products_df, api):
    # title/prod_id can be changed to download any file from product_df, including multiple. Adjust [0] value.
    title = products_df.iloc[0]['title'] 
    prod_id = products_df.iloc[0]['uuid']

    api.download(prod_id, CWD + IMG_DIR)
    
    return title

# unpacks downloaded file using title parameter, removes zipped version, renames file
# title: title of newly downloaded file
def unpack(title):
    dl_filepath = CWD + IMG_DIR + title + '.zip'
    
    # unpacking zip
    with zipfile.ZipFile(dl_filepath, 'r') as zip_ref:
        zip_ref.extractall(CWD + IMG_DIR)
        
    os.remove(dl_filepath) # remove zip 
    dl_filepath = CWD + IMG_DIR + title + '.SAFE' # unzip filepath
    
    # renaming file
    if CUSTOM:
        filename = 'sentinel' + CUS_NAME
    else:
        filename = 'sentinel' + COUNTRY
    dl_rename = CWD + IMG_DIR + filename
    os.rename(dl_filepath, dl_rename)

def main():
    create_directory()
    # execution for default search
    if CUSTOM is False:
        countries = getCountry(URL)
        filepath = createGeoJson(countries)
        check_library(COUNTRY)
        api = sentinel_contact()
        products_df = sentinel_product(filepath, api)
        title = sentinel_download(products_df, api)
        unpack(title)
        print("Complete.")
    # execution for custom search
    else:
        filepath = createGeoJson(0)
        api = sentinel_contact()
        check_library(CUS_NAME)
        products_df = sentinel_product(filepath, api)
        title = sentinel_download(products_df, api)
        unpack(title)
        print("Complete.")
        
main()
