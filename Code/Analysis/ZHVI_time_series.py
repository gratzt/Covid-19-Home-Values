# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 13:43:47 2023

@author: trevo
"""
import pandas as pd
import datetime
from matplotlib import pyplot as plt

clust = pd.read_csv(r'..\..\..\CSE 6242 Project Data\pca_kmeans_impmean_cluster.csv')
clust = clust.drop_duplicates('ZCTA5CE10')
clust = clust[['ZCTA5CE10', 'cluster']]
clust['cluster'] = clust['cluster'].astype(str)
#############
# Features
feat = pd.read_csv(r'..\..\..\CSE 6242 Project Data\Imputed Data\features2019_impmedian_normclust.csv')
feat = feat.drop_duplicates('ZIP')
feat = feat.rename(columns={'ZIP': 'ZCTA5CE10'})
################
# Zillow Data
zillow = pd.read_excel(r'..\..\..\CSE 6242 Project Data\Raw Data with Profiles\Zillow\Zip_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.xlsx')
zillow = zillow.rename(columns={'RegionName': 'ZCTA5CE10'})
# Convert datetime columns to strings
zillow.columns = [i if type(i) != datetime.datetime else i.strftime('%m/%d/%Y')
                  for i in zillow.columns]

ys = list(zillow.columns[213:])

tsdf = pd.merge(zillow, clust, on='ZCTA5CE10')
tsdf = tsdf[['cluster']+ys].copy()

allzips = tsdf[ys].median().reset_index()
allzips['cluster'] = 'all'
allzips = allzips.rename(columns={'index': 'month',
                                  0: 'zhvi'})

clustermed = tsdf.groupby('cluster').median().reset_index()
clustermed = clustermed.transpose()
clustermed = clustermed.reset_index()
clustermed.columns = ['month', 'c0', 'c1', 'c2']
clustermed = clustermed.iloc[1:,]

c0df = clustermed[['month', 'c0']].copy()
c0df = c0df.rename(columns={'c0': 'zhvi'})
c0df['cluster'] = '0'

c1df = clustermed[['month', 'c1']].copy()
c1df = c1df.rename(columns={'c1': 'zhvi'})
c1df['cluster'] = '1'

c2df = clustermed[['month', 'c2']].copy()
c2df = c2df.rename(columns={'c2': 'zhvi'})
c2df['cluster'] = '2'

stack = pd.concat([allzips, c0df, c1df, c2df])

outpath = r'..\..\..\CSE 6242 Project Data\\' + f'Median_ZHVI_Month_Cluster.csv'
stack.to_csv(outpath)

##############################################################################
# Plot by cluster
df = pd.read_csv(r'C:\Users\trevo\OneDrive\Documents\Georgia Tech\Courses\CSE6242\Project\DVA-Project-Repo\CSE 6242 Project Data\Median_ZHVI_Month_Cluster.csv')
df['month'] = pd.to_datetime(df['month'])

fig, ax = plt.subplots()
fig.set_size_inches(18.5, 10.5)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.set_ylabel(f"Median Zillow Home Value Index",  fontsize=16)
for c in ['all', '0', '1', '2']:
    cdf = df.loc[df['cluster'] == c,].copy()
    x = cdf['month']
        
    ax.plot(x, cdf['zhvi'], label = f'Cluster: {c}')
    plt.axvline(datetime.datetime(2020, 2, 29),
                color = 'black', linestyle ='--')
    plt.axvline(datetime.datetime(2022, 2, 28),
                color = 'black', linestyle ='--')
    
plt.text(datetime.datetime(2020, 2, 22), 400000, 'Last Month Prior to\nLockdowns',
        horizontalalignment='right',  fontsize=16)
plt.text(datetime.datetime(2022, 2, 21), 400000, 'Last Month Prior to\nFederal Fund Rate Hikes',
         horizontalalignment='right',  fontsize=16)
    
ax.legend(frameon=False,  fontsize=14) 
ax.tick_params(axis='both', which='major', labelsize=14)
ax.tick_params(axis='both', which='minor', labelsize=14)