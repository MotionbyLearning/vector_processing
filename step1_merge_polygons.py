import geopandas as gpd
import pandas as pd
from pathlib import Path

# Data directory
dir_dataset = Path("./datasets/")


if __name__ == "__main__":

    # Load AoI, get bounding box for reading
    aoi = gpd.read_file(dir_dataset / 'aoi.shp')
    aoi = aoi.to_crs(crs=28992) # reporject to RD
    bbox = aoi.bounds.iloc[0].to_list() # get bounding box

    # Load data within the AoI bouding box, then crop to the AoI
    # The bounding box filter only loads data that "intersects" with the bounding box
    # BRP
    f_brp = dir_dataset/'pdok'/'brpgewaspercelen_definitief_2021.gpkg'
    brp = gpd.read_file(f_brp, bbox=bbox)
    brp = brp.clip(aoi)

    # BRO
    f_bro = dir_dataset/'pdok'/'BRO_ModelBodemkaart.gpkg'
    bro = gpd.read_file(f_bro, bbox=bbox)
    bro = bro.clip(aoi)

    # peilgebied
    f_peilgebied = dir_dataset/'pdok'/'waterbeheergebiedenimwa'/'peilgebied.gpkg'
    peilgebied = gpd.read_file(f_peilgebied, bbox=bbox)
    peilgebied = peilgebied.clip(aoi)

    # Query BRO bodemkaart: get maparea_id and soilcode
    query_bro = brp.sjoin(bro[['maparea_id', 'soilcode', 'geometry']], how='left')
    res=[]
    for col in ['maparea_id', 'soilcode']: # ToDo: is there a way to use column index instead of loop?
        query_col = query_bro.groupby(query_bro.index)[col].apply(lambda x: list(x))
        res.append(query_col)
    query_bro = pd.concat(res,axis=1)

    # Query peilgebied: get guid
    query_peilgebied = brp.sjoin(peilgebied[['guid', 'geometry']], how='left')
    query_peilgebied = query_peilgebied.groupby(query_peilgebied.index)['guid'].apply(lambda x: list(x))
    
    # Add query results to brp
    brp = pd.concat([brp, query_bro, query_peilgebied], axis=1)

    # Rearrange column order, make 'geometry' the last col
    cols = brp.columns.to_list()
    cols.remove('geometry')
    cols.append('geometry')
    brp = brp[cols]

    # Use the pyogrio engine since we have list in the fields
    # Lists will be forced to str. ToDo: solve this problem
    brp.to_file("results_step1.shp", engine="pyogrio")


