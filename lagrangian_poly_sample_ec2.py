#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  5 14:11:34 2024

@author: laserglaciers
"""
import os
import json
import geopandas as gpd
from shapely.geometry import Point
from shapely.geometry import Polygon
import pandas as pd
import numpy as np
import xarray as xr
import rioxarray as rxr
import geoviews as gv
import geoviews.feature as gf
import hvplot.pandas
import s3fs
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from multiprocessing import Pool, cpu_count
import dask
from dask.distributed import Client, progress, LocalCluster
import dask.array as da
import geopandas as gpd

# %%

# THIS IS FROM EMMA's TUTORIAL https://github.com/e-marshall/itslivetools/blob/main/itslivetools/access.py
def find_granule_by_point(input_point, label='single_point'):
    '''returns url for the granule (zarr datacube) containing a specified point. point must be passed in epsg:4326
    '''
    catalog = gpd.read_file('https://its-live-data.s3.amazonaws.com/datacubes/catalog_v02.json')

    #make shapely point of input point
    p = gpd.GeoSeries([Point(input_point[0], input_point[1])],crs='EPSG:4326')
    #make gdf of point
    gdf = gdf = gpd.GeoDataFrame({'label': f'{label}', 
                                  'geometry':p})

    #find row of granule 
    granule = catalog.sjoin(gdf, how='inner')

    url = granule['zarr_url'].values[0]
    return url
    
def read_in_s3(http_url, chunks='auto'):
    ''' does some string formatting from zarr url and returns xarray dataset
    '''

    s3_url = http_url.replace('http','s3')
    s3_url = s3_url.replace('.s3.amazonaws.com','')

    datacube = xr.open_dataset(s3_url, engine='zarr',
                               storage_options={'anon':True},
                               chunks=chunks,
                              # lock=False
                              )

    # datacube = rxr.open_rasterio(s3_url, engine='zarr',
    #                            storage_options={'anon':True},
    #                            chunks=chunks)
    
    return datacube

# %%
catalog = gpd.read_file('https://its-live-data.s3.amazonaws.com/datacubes/catalog_v02.json') # ITS_LIVE data catalog where all the paths are defined
path = './merged_geoms/EQI_merged.gpkg'
eqi_poly = gpd.read_file(path)
eqi_centroid = eqi_poly.centroid.to_crs(crs='EPSG:4326')
eqi_centroid = gpd.GeoDataFrame(geometry=eqi_centroid,crs=4326)
granule = catalog.sjoin(eqi_centroid, how='inner')
url = granule['zarr_url'].values[0]

eqi_vels = read_in_s3(url)
eqi_vels = eqi_vels.chunk({"mid_date": len(eqi_vels.mid_date)}) # setting the mid_date chunksize to the time dimensions helps A LOT
eqi_vels = eqi_vels.sortby('mid_date')
eqi_vels.rio.write_crs('EPSG:3413',inplace=True)

# %%
term_polys_path = './merged_geoms/EQI_merged.gpkg'
term_polys = gpd.read_file(term_polys_path)

# %%

eqi_dates = eqi_vels.mid_date.dt.date.data # get the mid_dates
term_dates_pd = term_polys['date'].dt.date.values # get the polygon dates
matched_idx = np.where(np.isin(eqi_dates,term_dates_pd))[0] # returns the indices of the matched dates so we can just use an isel (integer select) on the data cube
eqi_vels = eqi_vels.isel(mid_date=matched_idx) # use isel to grab the data we want

# %%
days = eqi_vels.date_dt.compute() # get the dt_array
days = days.data.astype('timedelta64[D]') # convert to days using .astype
day_filter = np.timedelta64(100, 'D') # the day separation we filter by
matched_date_dt_idx = np.where(days<=day_filter)[0] # get this indices 
eqi_vels = eqi_vels.isel(mid_date=matched_date_dt_idx) # use isel to grab the data we want

# %%

def rio_clip(dataset,gdf,date_list,crs):
    velocity = []
    area = []
    for date in date_list:
        geom_values = gdf[gdf['date'] == pd.to_datetime(date.date())].geometry.values
        dataset_sample_clip = dataset.v.sel(mid_date=date).rio.clip(geom_values,crs,drop=True,invert=False,all_touched=True)
        mean_arr = dataset_sample_clip.mean(dim=["x", "y"],skipna=True)
        area_count = dataset_sample_clip.count(dim=["x", "y"]) #,skipna=True) This should not count NaNs
        
        velocity.append(mean_arr)
        area.append(area_count)
        
    return area, velocity

# %%
date_list = pd.to_datetime(eqi_vels.mid_date) #creates a list which we will split up to divide the parallelized work 

split_size = 50
date_lists = [date_list[x:x+split_size] for x in range(0, len(date_list), split_size)]

# %%
values = term_polys[term_polys['date'] == pd.to_datetime(date_lists[1][0].date())].geometry.values
# clip = eqi_vels.v.sel(mid_date=date_lists[1][0]).rio.clip(values,crs,drop=True,invert=False,all_touched=True)
term_polys.to_crs(crs="EPSG:3413",inplace=True)

args = []
crs = term_polys.crs
for date_list in date_lists:
    args.append((eqi_vels,term_polys,date_list,crs))
    
# %%
with Pool(processes=cpu_count()-4) as pool:
    result = pool.starmap(rio_clip, args)
    
# %%
computed_pixel_count = []
for i in range(0,len(result)):
    computed = dask.compute(*result[i][0])
    computed_pixel_count.append(computed)
    
computed_mean_vel = []
for i in range(0,len(result)):
    computed_vel = dask.compute(*result[i][1])
    computed_mean_vel.append(computed_vel)


# %%

computed_pixel_count_explode = [item for t in computed_pixel_count for item in t]
computed_vel_explode = [item for t in computed_mean_vel for item in t]

pixel_count = xr.concat(computed_pixel_count_explode,"mid_date").rename('area_count') # this creates one big data array
v_mean = xr.concat(computed_vel_explode,"mid_date").rename('v_mean') # this creates one big data array

area_vel_merge = xr.merge([pixel_count,v_mean])
term_polys['area'] = term_polys.area
mid_date_arr = area_vel_merge.mid_date.dt.date.data
term_poly_dates = term_polys.date.dt.date

term_poly_area = term_polys[['date','area']]
term_poly_area.set_index(['date'],inplace=True)
term_poly_area = term_poly_area.loc[mid_date_arr]
term_poly_area['mid_date'] = area_vel_merge.mid_date.data
term_poly_area.set_index(['mid_date'],inplace=True)

term_poly_area_xr_dataset = term_poly_area.to_xarray()
pixel_size = eqi_vels.rio.transform()[0]
area_vel_merge['poly_area'] = term_poly_area_xr_dataset.area
area_vel_merge['pixel_area'] = area_vel_merge.area_count * (pixel_size **2)
area_vel_merge['pixel_overlap'] = area_vel_merge.pixel_area/area_vel_merge.poly_area
area_vel_merge.to_dataframe().to_csv('./eqi_df.csv')

