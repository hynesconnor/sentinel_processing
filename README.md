# Querying and Processing Sentinel-2 Satellite Imagery Using SentinelAPI
Using the [Copernicus Open Access Hub](https://scihub.copernicus.eu/) with the [Sentinel Python API](https://sentinelsat.readthedocs.io/en/master/api_overview.html) to source and process satellite rasters for zonal statistics.

Below is an example of an RGB GeoTIFF layer produced by the program. This layer can be loaded into any GIS applications such as ArcGIS and QGIS. 

<p align="center">
<img src="/mkdwn/rgb.png" alt="Satellite Imagery - Greater Seattle"/>
</p>

## Installation and Use

Download and unzip the latest release [here](https://github.com/hynesconnor/sentinel_processing/releases). Unzip into location of your choice.

**IMPORTANT**: Specifications on the Python versions used and the packages installed can be found in `requirements.txt`.

## Querying Sentinel-2 Bands

1. Navigate to the Copernicus Open Access Hub and create an account: https://scihub.copernicus.eu/dhus/#/self-registration

2.  Your username and password will be used to access the SentinelAPI within the script

3. Open `sentinel_query.py` and enter your credentials as the `USER` and `PASS` constant variables.  

4. Customize search parameters `COUNTRY`, `YEAR_SEARCH`, and  `CLOUD_COVER` to search predefined country locations or perform a custom latitude/longitude search for any location by setting the boolean `CUSTOM` to `True`. 

5. Run the script. The average file size is around 900MB and downloads range from 2-14 minutes.

6. Downloaded imagery can be located in your working directory at `../data/image`

## Processing Sentinel Bands for RGB/NDVI/NDWI Layers

1. Open `image_processing.py` and adjust the `FOLDER` constant variable to the name of the satellite data in `../data/image`. ex. `FOLDER = 'sentinelUS'`.

2. Run the script.

3. The following files have been written:
    - RGB .tif file will be output to `../data/processed/rgb`.
    - NDVI .tif file will be output to `../data/processed/ndvi`.
    - NDWI .tif file will be output to `../data/processed/ndwi`.

4. The mean vegitation and water density of the rasters are also printed to the console.

## In Practice. . . 

Below are two examples of NDVI and NDWI layers produced by the image processesing steps. The layers are produced using Sentinel-2 data of the greater Seattle area. These layers can be loaded into GIS applications such as ArcGIS or QGIS.   

NDVI                       | NDWI
:-------------------------:|:---------------------------:
![](/mkdwn/ndvi_color.png) | ![](/mkdwn/ndwi_color2.png)