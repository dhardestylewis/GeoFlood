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
    geofloodOutputsDir = os.path.join(geofloodHomeDir,"Outputs","GIS",projectName)
    geofloodInputsDir = os.path.join(geofloodHomeDir,"Inputs","GIS",projectName)
    shapefileDataDir = os.path.join(geofloodInputsDir,"Flowline.shp")
    pmGrassGisfileName = os.path.join(geofloodOutputsDir,"PM_filtered_grassgis.tif")
    skeletonDataDir = os.path.join(geofloodOutputsDir,DEM_name) 
    skeletonFile = skeletonDataDir + '_skeleton.tif'
    
    # Read Shapefile as GeoPandas DataFrame
    NHDPlusMR_shp = gpd.read_file(shapefileDataDir)

    # Assign value to GeoPandas DataFrame where the channel occurs
    NHDPlusMR_shp['value'] = 1 # Choose any arbitrary value

    # Subset the DataFrame to just the geometry and value columns
    NHDPlusMR_shp = NHDPlusMR_shp[['geometry','value']]

    # Extract metadata from pygeonet_skeleton_defintion.py _skeleton.tif
    filteredDemArray = read_geotif_filteredDEM(pmGrassGisfileName)
    skeleton_raster = rasterio.open(skeletonFile)
    meta = skeleton_raster.meta.copy()
    meta.update(compress='lzw')
    # print(meta)

    # Assign GeoSpatial raster data
    with rasterio.open(skeletonFile,'w+',**meta) as out:
        out_arr = out.read(1)
        # print(out_arr)
        shapes = ((geom,val) for geom,val in zip(NHDPlusMR_shp.geometry,NHDPlusMR_shp.value))
        NHDPlusMR_raster = features.rasterize(shapes=shapes,fill=1,out=out_arr,transform=out.transform)

    NHDPlusMR_raster = NHDPlusMR_raster.astype(np.uint8)

    # Write outputs
    OutputFileName = DEM_name + '_path.tif'
    write_geotif_skeleton(NHDPlusMR_raster,geofloodOutputsDir,OutputFileName)

if __name__ == '__main__':
    t0 = perf_counter()
    main()
    t1 = perf_counter()
    print(("time taken to complete shapefile to binary raster:", t1-t0, "seconds"))

