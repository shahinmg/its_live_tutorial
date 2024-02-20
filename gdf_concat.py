#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 17:40:43 2024

@author: laserglaciers
"""

import geopandas as gpd
import os

glacier_names = ['KUJ', 'AVA','KAN','EQI']

for name in glacier_names:
    shp_file_path = f'/media/laserglaciers/upernavik/its_live_tutorial/{name}_polygons/'
    os.chdir(shp_file_path)
    gdfs_dates = [(gpd.read_file(fn), gpd.pd.to_datetime(fn[:10].replace('_','-'))) for fn in sorted(os.listdir(shp_file_path)) if fn.endswith('shp')] # 
    
    gdfs, dates = zip(*gdfs_dates)
    
    rdf = gpd.GeoDataFrame(gpd.pd.concat(gdfs, ignore_index=True), crs=gdfs[0].crs)
    rdf['date'] = dates
    rdf.drop(columns=['col1'], inplace=True)
    rdf.to_crs(crs=None,epsg=3413,inplace=True)
    
    op = '/media/laserglaciers/upernavik/its_live_tutorial/merged_geoms/'
    rdf.to_file(f'{op}{name}_merged.gpkg',driver='GPKG',crs="EPSG:3413")