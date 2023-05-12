# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 07:57:16 2023

@author: Trevor Gratz trevormgratz@gmail.com

This file take the Common Core Data, subsets it to schools of interest, and
merges it to the EDGE data. Once the EDGE data merged in, each zip code in the
Tiger Lines data is matched to its nearest elementalry, middle, and high school

"""

import geopandas as gpd
import pandas as pd
import os
from shapely.ops import nearest_points
from shapely.geometry import Point
from math import radians
from numpy import cos, sin, arcsin, sqrt
import time
##############################################################################
# Load Data
dfdir = pd.read_csv(r'..\..\..\Data\Raw Data with Profiles\NCES\commoncore\commoncore\directory_ccd_sch_029_1819_w_1a_091019.csv',
                    encoding='cp1252')
edgedir = pd.read_excel(r'..\..\..\Data\Geographic\Education\EDGE_GEOCODE_PUBLICSCH_1819.xlsx')

dftl = gpd.read_file(r'..\..\..\Data\Geographic\zipcode\tl_2019_us_zcta510\tl_2019_us_zcta510.shp')

##############################################################################
# Prep

def prep_sch(dfdir = dfdir, edgedir = edgedir):
    '''
    This function takes the Common Core Directory Data and subsets it to 
    "regular" elementary, middle, and high schools. It merges in the EDGE data
    of the school coordinates and returns a geodata frame.
    '''
    # Keep "Regular School" Types
    dfdir = dfdir.loc[dfdir['SCH_TYPE'] == 1, ]
    # Keep Elementary, Middle, and High Schools
    dfdir = dfdir.loc[dfdir['LEVEL'].isin(["Elementary", "Middle", "High"]), ]
    # Remove Inactive/Closed Schools
    dfdir = dfdir.loc[~dfdir['UPDATED_STATUS_TEXT'].isin(["Closed", "Future", 
                                                          "Inactive"]), ]
    # Perfect 1:1 match
    edgedir = edgedir[['NCESSCH', 'LAT', 'LON']]
    dfdir = dfdir[['NCESSCH', 'LEVEL']]
    schs = pd.merge(dfdir, edgedir, on = ['NCESSCH'],
                    how='inner')
    
    # Convert to GeoData frame with cordinates
    geo_sch = gpd.GeoDataFrame(schs, geometry=gpd.points_from_xy(schs.LON,
                                                                 schs.LAT),
                               crs = 'WGS84')
    geo_sch = geo_sch.rename(columns = {'LON':'SCH_LON',
                                        'LAT':'SCH_LAT'})
    return geo_sch


dfsch = prep_sch(dfdir = dfdir, edgedir = edgedir)
dftl = dftl.to_crs('WGS84')
tl_center = gpd.GeoDataFrame(dftl, geometry=gpd.points_from_xy(dftl.centroid.x,
                                                               dftl.centroid.y))
tl_center['ZIP_LON'] = tl_center.centroid.x
tl_center['ZIP_LAT'] = tl_center.centroid.y

##############################################################################
# Find closest school [by level] to each zip code


colsave = ['NCESSCH', 'SCH_LON', 'SCH_LAT']

# Calculates distance between two points based on their cordinates
# Used specifically in the match_zip_sch function below as a apply
# lambda function
def haversine(row):
    sch_lat = row['SCH_LAT']
    sch_lon = row['SCH_LON']
    zip_lat = row['ZIP_LAT']
    zip_lon = row['ZIP_LON']
    sch_lat, sch_lon, zip_lat, zip_lon = (
        map(radians, [sch_lat, sch_lon, zip_lat, zip_lon]))
    dlat = zip_lat - sch_lat
    dlon = zip_lon - sch_lon
    a = sin(dlat/2)**2 + cos(sch_lat) * cos(zip_lat) * sin(dlon/2)**2
    c = 2 * arcsin(sqrt(a))
    miles = (6367 * c) * 0.621371 
    return miles


def match_zip_sch(level = 'All', colsave=colsave):
    '''

    Parameters
    ----------
    level : String
        DESCRIPTION. Subsets the school data to Elementary, Middle, or 
                     High school. Options = ["High", "Middle", "Elementary",
                                             "All"]
        
    colsave : TYPE, List of Strings
        DESCRIPTION. The default is colsave. Choose the columns from the school
        data to include in the output dataset.

    Returns
    -------
    TYPE: Dataset
        DESCRIPTION. A single row per each zip code that matches the nearest
                     school ID to it.

    '''
    
    # Subset to school level
    if level in ["High", "Middle", "Elementary"]:
        temp = dfsch.loc[dfsch['LEVEL'] == level, ].copy()
        pts_sch = temp.geometry.unary_union
    else:
         temp = dfsch.copy()
         pts_sch = temp.geometry.unary_union

    # Find Nearest Point
    def near(point, pts=pts_sch):
        nearest = temp.geometry == nearest_points(point, pts)[1]
        return temp.loc[temp.index[nearest], colsave]

    store = gpd.GeoDataFrame(columns= colsave + ['ZCTA5CE10', 'ZIP_LON', 'ZIP_LAT'])
    
    # Loop through all zip codes
    t0 = time.time()
    for i in range(len(tl_center)):
       
        # How far have we come?!?!
        if i%100 == 0:
            print(i)
            
        toadd = near(point = tl_center.loc[i, 'geometry'])
        toadd['ZCTA5CE10'] = tl_center.loc[i, 'ZCTA5CE10']
        toadd['ZIP_LON'] = tl_center.loc[i, 'ZIP_LON']
        toadd['ZIP_LAT'] = tl_center.loc[i, 'ZIP_LAT']
    
        store = store.append(toadd, ignore_index=True)
    
    # Calculate Distance between zip code and nearest school
    store['distance'] = store.apply(lambda row: haversine(row), axis=1)
    store['level'] = level
    t1 = time.time()
    print(t1-t0)
    return store

elem = match_zip_sch(level="Elementary")
elem.to_csv(r'..\..\..\Data\Intermediate\elem_zip_school_crosswalk.csv')

middle = match_zip_sch(level="Middle")
middle.to_csv(r'..\..\..\Data\Intermediate\middle_zip_school_crosswalk.csv')

high = match_zip_sch(level="High")
high.to_csv(r'..\..\..\Data\Intermediate\high_zip_school_crosswalk.csv')

outdf = pd.concat([elem, middle, high])
outdf.to_csv(r'..\..\..\Data\Clean Data\zip_school_crosswalk.csv')