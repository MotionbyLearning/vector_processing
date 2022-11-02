from cProfile import label
import geopandas as gpd
import pandas as pd
import rioxarray
from pathlib import Path
import numpy as np
from rasterio import features
import xarray as xr
from xrspatial import zonal_stats

# Data directory
dir_dataset = Path("/mnt/c/Users/OuKu/Developments/MobyLe/vector_processing/datasets/")

# List of tiff files
f_glg = dir_dataset/'pdok'/'glg-mediaan.tif'
f_ghg = dir_dataset/'pdok'/'ghg-mediaan.tif'
tiff_list = [f_glg, f_ghg]
col_label_list = ['glg_mean', 'ghg_mean']

if __name__ == "__main__":

    # Load results of previous step
    brp = gpd.read_file('./results_step1.shp')

    # Zonal statistics
    for file, col_label in zip(tiff_list, col_label_list):
        # load tiff
        tiff = rioxarray.open_rasterio(file)
        tiff= tiff[0,:,:]

        # rasterize the polygon
        list_geom = [[geo, id] for geo, id in zip(brp['geometry'].to_list(), brp.index.to_list())] # get geometry with id
        brp_rasterized = features.rasterize(list_geom, out_shape=tiff.shape, fill=0, transform=tiff.rio.transform())
        brp_rasterized_xarr = xr.DataArray(brp_rasterized)

        # compute zonal stats glg
        stats = zonal_stats(brp_rasterized_xarr, tiff, stats_funcs=['mean'], nodata_values=np.nan)
        stats = stats.set_index('zone').reindex(range(brp.shape[0]))
        stats = stats.rename(columns={'mean': col_label})

        brp = pd.concat([brp, stats], axis=1)

    # Rearrange column order, make 'geometry' the last col
    cols = brp.columns.to_list()
    cols.remove('geometry')
    cols.append('geometry')
    brp = brp[cols]

    # Use the pyogrio engine since we have list in the fields
    # Lists will be forced to str. ToDo: solve this problem
    brp.to_file("results_step2.shp", engine="pyogrio")