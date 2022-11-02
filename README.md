# vector_processing

### Installation

```sh
conda env create -f envrionment.yml
```

### Expected data structure

```sh
.
├── README.md
├── datasets
│   ├── knmi
│   │   ├── 20221019
│   │   │   ├── etmgeg_257_wijkaanzee.txt
│   │   │   ├── etmgeg_270_leeuwarden.txt
│   │   │   ├── etmgeg_279_hoogveen.txt
│   │   │   ├── etmgeg_344_rotterdam.txt
│   │   │   └── etmgeg_348_cabauw.txt
│   │   ├── knmi_stations.txt
│   │   └── knmistations.csv
│   └── pdok
│       ├── BRO_ModelBodemkaart.gpkg
│       ├── aan
│       │   ├── AAN_20200302.cpg
│       │   ├── AAN_20200302.dbf
│       │   ├── AAN_20200302.prj
│       │   ├── AAN_20200302.sbn
│       │   ├── AAN_20200302.sbx
│       │   ├── AAN_20200302.shp
│       │   └── AAN_20200302.shx
│       ├── brpgewaspercelen_definitief_2021.gpkg
│       ├── ghg-mediaan.tif
│       ├── glg-mediaan.tif
│       └── waterbeheergebiedenimwa
│           ├── afvoergebiedaanvoergebied.gpkg
│           ├── peilafwijkinggebied.gpkg
│           ├── peilbesluitgebied.gpkg
│           └── peilgebied.gpkg
├── envrionment.yml
├── exmaple_results
│   └── assendelft
│       ├── assendelft_attributes_wgs48.cpg
│       ├── assendelft_attributes_wgs48.dbf
│       ├── assendelft_attributes_wgs48.prj
│       ├── assendelft_attributes_wgs48.shp
│       └── assendelft_attributes_wgs48.shx
├── step0_make_aoi.py
├── step1_merge_polygons.py
├── step2_zonal_stats.py
└── step3_find_closets_station.py
```

Note that `datasets/knmi/knmistations.csv` is manually processed for accessing the station coords. It can be retrieved from this repo.

The other data files can be retrieved from the server.


### Execution

The processing is put into 4 python files. They can be executed sequentially.

In Summary:
- Step 0: create a AoI polygon based on the example result. In relality user can define there own AoI
- Step 1: Polygon merging
- Step 2: Zonal stats
- Step 3: query neareast station

Run, e.g. step 0
```
python3 step0_merge_polygons.py
```
After running three steps, the result shp will be crop field polgons within AoI, with all enriched fields.
### Known issues

1. list is not supported by shp fields, but some spatial query has multi results.

2. NaN values in Zonal stats step for some polygons. Possibly caused by when vectorizing the crop fields, some pixels contains multiple polygons. Can be solved by oversampling ref raster.

3. Some weather station have same coords. Now we simply choose the first one.

4. Some parcels cross two or more voronoid polgons, i.e. they have two closest stations. Now we simply choose the first entry as closest. If more precision is required, we can calculate the overlap area an use the largest one as closeast. See [this example](https://gis.stackexchange.com/questions/389675/spatially-joining-only-features-by-largest-overlap-with-sjoin-in-geopandas).

5. To scale up this process, one can consider to separate brp pacels in chunks and use [dask bag](https://docs.dask.org/en/stable/bag.html) for parallel processing.




