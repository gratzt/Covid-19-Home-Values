# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 13:43:47 2023

@author: trevo
"""
import pandas as pd
import datetime
from matplotlib import pyplot as plt


#############
# Features
feat = pd.read_csv(r'..\..\..\Data\Clean Data\features2019.csv')

################
# Zillow Data
zillow = pd.read_excel(r'..\..\..\Data\Raw Data with Profiles\Zillow\Zip_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.xlsx')
zillow = zillow.rename(columns={'RegionName': 'ZCTA5CE10'})
# Convert datetime columns to strings
zillow.columns = [i if type(i) != datetime.datetime else i.strftime('%m/%d/%Y')
                  for i in zillow.columns]

ys = list(zillow.columns[213:])

tsdf = zillow.copy()

allzips = tsdf[ys].median().reset_index()
allzips['cluster'] = 'all'
allzips = allzips.rename(columns={'index': 'month',
                                  0: 'zhvi'})


outpath = r'..\..\..\Data\\' + f'Median_ZHVI_Month.csv'
allzips.to_csv(outpath)

