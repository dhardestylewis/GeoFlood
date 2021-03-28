import numpy as np
from time import perf_counter
from pygeonet_rasterio import *
from pygeonet_plot import *
import geopandas as gpd
import rasterio
from rasterio import features
# from numba import njit
import sys
import os

def main():
    geofloodHomeDir = sys.argv[1]
    projectName = sys.argv[2]
    DEM_name = sys.argv[3]
    geofloodOutputsDir = os.path.join(geofloodHomeDir,"GeoOutputs","GIS",projectName)
    geofloodInputsDir = os.path.join(geofloodHomeDir,"GeoInputs","GIS",projectName)
    shapefileDataDir = os.path.join(geofloodInputsDir,"Flowline.shp")
    skeletonDataDir = os.path.join(geofloodOutputsDir,DEM_name) 
    skeletonFile = skeletonDataDir + '_skeleton.tif'
    metaDataDir = os.path.join(geofloodOutputsDir,DEM_name) 
    metaFile = metaDataDir + '_slp.tif'
    
    # Read Shapefile as GeoPandas DataFrame
    NHDPlusMR_shp = gpd.read_file(shapefileDataDir)

    # Assign value to GeoPandas DataFrame where the channel occurs
    NHDPlusMR_shp['value'] = 1 # Choose any arbitrary value

    # Subset the DataFrame to just the geometry and value columns
    NHDPlusMR_shp = NHDPlusMR_shp[['geometry','value']]

    # Extract metadata from original tif
    meta_raster = read_dem_from_geotiff(os.path.basename(metaFile),geofloodOutputsDir)
    meta_raster = rasterio.open(metaFile)
    meta = meta_raster.meta.copy()
    meta.update(compress='lzw')
    # print(meta)

    # Assign GeoSpatial raster data
    with rasterio.open(skeletonFile,'w+',**meta) as out:
        out_arr = out.read(1)
        out_transform = out.transform
        # print(out_arr)
    shapes = ((geom,val) for geom,val in zip(NHDPlusMR_shp.geometry,NHDPlusMR_shp.value))
    NHDPlusMR_raster = features.rasterize(shapes=shapes,fill=0,out=out_arr,transform=out_transform)

    NHDPlusMR_raster = NHDPlusMR_raster.astype(np.uint8)
    meta.update(dtype=np.uint8)
    meta.update(nodata='255')
    NHDPlusMR_raster[np.logical_and(
        meta_raster.read(1) != meta_raster.nodata,
        NHDPlusMR_raster != 1
    )] = 0

    # Write outputs
    OutputFileName = DEM_name + '_path.tif'
    OutputFilePath = os.path.join(geofloodOutputsDir,OutputFileName) 
    #write_geotif_skeleton(NHDPlusMR_raster,geofloodOutputsDir,OutputFileName)
    with rasterio.open(OutputFilePath,'w',**meta) as out:
        out.write(NHDPlusMR_raster, 1)

if __name__ == '__main__':
    t0 = perf_counter()
    main()
    t1 = perf_counter()
    print(("time taken to complete shapefile to binary raster:", t1-t0, "seconds"))

