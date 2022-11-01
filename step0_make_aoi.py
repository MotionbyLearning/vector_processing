import geopandas as gpd
import pandas as pd
import rioxarray
from pathlib import Path

# Target result, used to define AoI
file_target = Path(
    "/mnt/c/Users/OuKu/Developments/MobyLe/vector_processing/exmaple_results/assendelft/assendelft_attributes_wgs48.shp"
)

# Data directory
dir_dataset = Path("/mnt/c/Users/OuKu/Developments/MobyLe/vector_processing/datasets/")


if __name__ == "__main__":

    # Make an AoI ploygon according to the convex hull of the target results
    # Only need to do it once, for testing
    # In reality this will be an manually created polygon
    poly_target = gpd.read_file(file_target)
    cx = poly_target.unary_union.convex_hull
    poly_aoi = gpd.GeoDataFrame(geometry=[cx], crs=poly_target.crs)
    poly_aoi.to_file(dir_dataset / 'aoi.shp')

    
