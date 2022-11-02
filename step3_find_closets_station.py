import geopandas as gpd
import itertools
from pathlib import Path
from shapely.geometry import Point
from geovoronoi import voronoi_regions_from_coords, points_to_coords

# Data directory
dir_dataset = Path("./datasets/")

# Data directory
f_knmi_stations = Path("./datasets/knmi/knmistations.csv")

if __name__ == "__main__":

    # Load AoI for Voronoid boundary
    aoi = gpd.read_file(dir_dataset / 'aoi.shp')
    aoi = aoi.to_crs(28992)
    aoi_with_buffer = aoi['geometry'].buffer(50000) # grow a 50kmm buffer

    # Load stations and add geometry
    knmi_stations = gpd.read_file(f_knmi_stations)
    points = [
        Point((float(lat), float(lon)))
        for lat, lon in zip(
            knmi_stations["POS_OL"].values, knmi_stations["POS_NB"].values
        )
    ]  # assuming lon and lat to be "NB" and OL
    knmi_stations['geometry'] = points
    knmi_stations = knmi_stations.set_crs(4326) # Assuming WGS84

    # Convert to RD
    knmi_stations = knmi_stations.to_crs(28992)

    # Take only points within the AoI
    knmi_stations = knmi_stations.clip(aoi_with_buffer)

    # Drop duplicate coords. ToDo: other solutions?
    knmi_stations = knmi_stations.drop_duplicates('geometry')

    # Calculate Voronoi Regions
    coords = points_to_coords(knmi_stations.geometry)
    poly_shapes, pts = voronoi_regions_from_coords(coords, aoi_with_buffer[0]) # There are duplicates in "pts" because of duplicate coords

    # Make a GDF with Voronoi and corresponding STN
    voronoi = gpd.GeoDataFrame(geometry=list(poly_shapes.values()))
    voronoi = voronoi.set_crs(28992)
    pts_index = list(itertools.chain(*list(pts.values()))) # ToDo: imporve this complicated syntax
    voronoi['STN'] = knmi_stations.iloc[pts_index]['STN'].values

    # Load results of previous step
    brp = gpd.read_file('./results_step2.shp')

    # Search for the closest STN, append searching results to brp
    # This is done by selecting the first entry. An improvement can be applied if more precision is required 
    brp = brp.sjoin(voronoi[['STN', 'geometry']], how='left')
    brp = brp.rename(columns={'STN': 'near_STN'}).drop(columns=['index_right'])
    brp.iloc[~brp.index.duplicated()] # Drop duplicated index

    # Rearrange column order, make 'geometry' the last col
    cols = brp.columns.to_list()
    cols.remove('geometry')
    cols.append('geometry')
    brp = brp[cols]

    # convert back to wgs84
    brp = brp.to_crs(4326)
    
    # Use the pyogrio engine since we have list in the fields
    # Lists will be forced to str. ToDo: solve this problem
    brp.to_file("results_step3.shp", engine="pyogrio")
