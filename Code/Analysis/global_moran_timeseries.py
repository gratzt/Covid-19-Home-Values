# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 13:16:55 2023

@author: Trevor Gratz tgratz6@gatech.edu

Zillow data has 2 - 1.5K values depending on the month. Try the following 
variations for computing Moran Globals

1) Dropping Rows with missing values
2) Imputing 

"""

import geopandas as gpd
import pandas as pd
from pysal.lib import weights
from pysal.viz import splot
from pysal.explore import esda
import datetime
import numpy as np
from matplotlib import pyplot as plt

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# Shape File
zdf = gpd.read_file(r'..\..\..\CSE 6242 Project Data\Geographic\zipcode\tl_2019_us_zcta510\tl_2019_us_zcta510.shp')
zdf['ZCTA5CE10'] = zdf['ZCTA5CE10'].astype(int)

##################
# Imputed Dataset
##################

zillow = pd.read_csv(r'..\..\..\CSE 6242 Project Data\Imputed Data\zhvi_filled.csv')
zillow = zillow.rename(columns={'ZIP': 'ZCTA5CE10'})
zillow = zillow.drop_duplicates('ZCTA5CE10')

# Convert datetime columns to strings
zillow.columns = [i if type(i) != datetime.datetime else i.strftime('%m/%d/%Y')
                  for i in zillow.columns]

# Subset Zillow data to last decade
zdec = zillow[zillow.columns[:9].append(zillow.columns[165:])].copy()
zdec = zdec.rename(columns={'ZIP': 'ZCTA5CE10'})
impdf = pd.merge(zdf, zdec, on ='ZCTA5CE10')

#######################
# Listwise deletion
#######################
zillow = pd.read_excel(r'..\..\..\CSE 6242 Project Data\Raw Data with Profiles\Zillow\Zip_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.xlsx')
zillow = zillow.rename(columns={'RegionName': 'ZCTA5CE10'})
# Convert datetime columns to strings
zillow.columns = [i if type(i) != datetime.datetime else i.strftime('%m/%d/%Y')
                  for i in zillow.columns]

# Subset Zillow data to last decade
zdec = zillow[zillow.columns[:9].append(zillow.columns[165:])].copy()

zdec = zdec.rename(columns={'ZIP': 'ZCTA5CE10'})
deldf = pd.merge(zdf, zdec, on ='ZCTA5CE10')


def moranI_timeseries(df, imputed=False):
    '''
    Forward filling and backfilling on Zillow Home Value Index potentially
    introduces large estimation errors in the Moran statistics. This function
    allows the user to compute Moran's on each month using only complete data
    from that month, or to use imputed data.

    '''
    if imputed == True:
        w = weights.KNN.from_dataframe(df, k=5)
        w.transform = "R"
        zillowmonths = df.columns[19:-4]
    else:
        zillowmonths = df.columns[18:]
    moranlist = []
   
    for m in zillowmonths:
        print(m)
        if imputed == False:
             temp = df.loc[~df[m].isna(),].copy()
             w = weights.KNN.from_dataframe(temp, k=5)
             w.transform = "R"
             moran = esda.moran.Moran(temp[m], w)
        else:
            moran = esda.moran.Moran(df[m], w)
        
        lci = moran.I - 1.96*moran.seI_norm
        hci = moran.I + 1.96*moran.seI_norm
        moranlist.append({'month': m,
                          'moran': moran.I,
                          'moran_p': moran.p_norm,
                          'moran_se':moran.seI_norm,
                          'moran_hci': hci,
                          'moran_lci': lci})
    
    morandf = pd.DataFrame(moranlist)
    morandf['month'] = pd.to_datetime(morandf['month'])
    return morandf


moran_imputed = moranI_timeseries(df=impdf, imputed=True)
moran_listdel = moranI_timeseries(df=deldf, imputed=False)

##############################################################################
# Plots
##############################################################################

# Imputed
fig, ax = plt.subplots()
x = moran_imputed['month']
ax.plot(x, moran_imputed['moran'])
ax.fill_between(
    x, moran_imputed['moran_lci'], moran_imputed['moran_hci'], color='b', alpha=.15)
ax.set_ylim(ymin=0.5)
ax.set_title("Moran's I in the Zillow Home Value Index")
fig.autofmt_xdate(rotation=45)

# Listwise Deletion
fig, ax = plt.subplots()
x = moran_listdel['month']
ax.plot(x, moran_listdel['moran'])
ax.fill_between(
    x, moran_listdel['moran_lci'], moran_listdel['moran_hci'], color='b', alpha=.15)
ax.set_ylim(ymin=0.7)
ax.set_title("Moran's I in the Zillow Home Value Index")
fig.autofmt_xdate(rotation=45)

# The Rise in Global Moran values from 2013 until 2019 could be explained by
# fewere missing data. The number missings don't really change much in 2019 and
# 2020, then in 2021 they start to drop. The drop in missing values would 
# push the global moran higher as closer observations are being compared. 
# However, that is not what we see.

for i in deldf.columns[18:]:
    nna = deldf[i].isna().sum()
    print(f'Month: {i}, Missing: {nna}')