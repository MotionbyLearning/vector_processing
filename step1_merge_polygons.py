import geopandas as gpd
import pandas as pd
import rioxarray
from pathlib import Path

# Data directory
dir_dataset = Path("/mnt/c/Users/OuKu/Developments/MobyLe/vector_processing/datasets/")


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

    # Writing results to geojson
    # GeoDataFrame's ".to_file()" cannot handle list fields, so we are mannualy writing the json
    # The geojson file can be loaded into QGIS direclty
    # The drawback is hat geojson is very big, we can also see other possibilities
    json_str = brp.to_json(indent=4)
    with open('results.geojson', "w") as f:
        f.write(json_str)


