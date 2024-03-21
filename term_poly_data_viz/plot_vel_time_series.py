#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 21 16:07:42 2024

@author: laserglaciers
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os


root_path = '../csv_outputs/'
os.chdir(root_path)
df_list = [df for df in os.listdir(root_path) if df.endswith('csv')]

for file in df_list:
    
    df = pd.read_csv(file, index_col=['mid_date'])
    df.index = pd.to_datetime(df.index)
    name = file[:3]
    
    fig, ax = plt.subplots()
    df = df[df['pixel_overlap']>0.01]
    df = df[df['v_mean']>100]
    df = df[df['v_mean']<17500]
    # df.v_mean.plot(ax=ax)
    ax.plot(df.index,df.v_mean)

    ax.xaxis.set_major_locator(mdates.YearLocator(5))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))  
    ax.set_title(f'{name.upper()}')
    
    op = '../term_poly_data_viz/'
    plt.savefig(f'{op}/{name.upper()}_time_series.png', dpi=300)
    