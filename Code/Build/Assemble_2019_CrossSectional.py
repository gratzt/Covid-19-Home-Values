# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 07:57:35 2023

@author: Trevor Gratz, trevormgratz@gmail.com

This combines the Data Profile tables from the five year estimates of American
Communities Survey data (2019), with Common Core data from the 2018-19 school
year, and Rural Urban Commuting Area codes. All data are mapped to a zip code.
The final output is a single observation per zip code.  

"""

import pandas as pd
import os
import numpy as np 

##############################################################################
## Load Data
##############################################################################

# Paths
scriptpath = os.path.dirname(os.path.abspath(__file__))
rucapath = os.path.join(scriptpath, 
                    r'..\..\..\Data\Raw Data with Profiles\RUCA\RUCA2010zipcode.xlsx')

ccdpath = os.path.join(scriptpath, 
                    r'..\..\..\Data\Clean Data\clean_common_core.csv')

ccdzippath = os.path.join(scriptpath, 
                          r'..\..\..\Data\Clean Data\zip_school_crosswalk.csv')

acspath = os.path.join(scriptpath, 
                       r'..\..\..\Data\Intermediate\acs_data.csv')


outpath = os.path.join(scriptpath, 
                       r'..\..\..\Data\Clean Data\features2019.csv')
outpickle = os.path.join(scriptpath, 
                       r'..\..\..\Data\Clean Data\features2019.pkl')

# Load
ruca = pd.read_excel(rucapath, sheet_name='Data')
ccd = pd.read_csv(ccdpath)
ccdzip = pd.read_csv(ccdzippath)
acsdf = pd.read_csv(acspath)

##############################################################################
## Cleaning Functions

def mergeschool(ccd, ccdzip):
    '''
    This functions takes the 2019 common core data and merges it to a crosswalk
    that includes zip codes. First it pivots merges the ccd and crosswalk data
    then it pivotes the data from a zip code - school - school level dataset to a 
    wide zip code grain dataset.
    '''
    
    # Appears some schools co-locate (Go from 99862 observations to 99432)
    ccdzip = ccdzip.drop_duplicates(subset=['ZCTA5CE10', 'ZIP_LON', 'ZIP_LAT', 'level'])
    
    # Prep and Merge
    ccd = ccd.rename(columns={'LEVEL': 'level'})
    ccd = ccd.drop(columns=['Unnamed: 0'])
    sch = pd.merge(ccdzip, ccd, on=['NCESSCH', 'level'],
                   how='left')
   
    # Pivot
    sch_wide = pd.pivot(index = ['ZCTA5CE10', 'ZIP_LON', 'ZIP_LAT'],
                                columns = 'level',
                                values = [v for v in ccd.columns
                                           if v not in ['level', 'year']],
                                data = sch)
    sch_wide = sch_wide.reset_index()
    
    # Unstack Columns
    sch_wide.columns = ['sch_'+ i[1] + '_' +i[0] for i in sch_wide.columns]
    sch_wide = sch_wide.rename(columns={'sch__ZCTA5CE10': 'ZCTA5CE10',
                                        'sch__ZIP_LON': 'ZIP_LON',
                                        'sch__ZIP_LAT': 'ZIP_LAT'})
    return sch_wide


def cleandp(dp):
    dp = dp.rename(columns={'zip code tabulation area': 'ZCTA5CE10'})
    dp = dp.drop(columns=['Unnamed: 0', 'NAME'])
    return dp


def cleandf(df):

    # Standardize missing value representation.
    # division by zero 
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    
    # ACS occasional has negative values, which should be recorded as missing
    # values for these variables. Flatten ACS variable lists
    acsvars = [i for i in acsdf.columns
               if i not in ['ZCTA5CE10', 'state']]
    
    for a in acsvars:
        df.loc[df[a] < 0, a] = np.nan
    
    # Reparameterize data for ease of interpretation
    df['Per_Black'] = 100*df['Per_Black']    
    df['Per_Hispanic'] = 100*df['Per_Hispanic']    

    df['Per_AIAN'] = 100*df['Pop_AIAN']/df['TotalPop']
    df['Per_Asian'] = 100*df['Pop_Asian']/df['TotalPop']
    df['Per_NHPI'] = 100*df['Pop_NHPI']/df['TotalPop']
    df['Per_OtherRace'] = 100*df['Pop_OtherRace']/df['TotalPop']
    df['Per_TwoPlusRace'] = 100*df['Pop_TwoPlusRace']/df['TotalPop']
    df['Per_White'] = 100*df['Pop_White']/df['TotalPop']

    df['urban'] = df['RUCA1'].isin([1,2,3]).astype(int)
    df['suburb'] = df['RUCA1'].isin([4, 5, 6]).astype(int)
    df['town'] = df['RUCA1'].isin([7, 8, 9]).astype(int)
    df['rural'] = df['RUCA1'].isin([10]).astype(int)
    df['per_bach_plus'] = 100*(df['Pop25_plus_with_bachelors'] + df['Pop25_plus_with_gradprof'])/df['Pop25_plus']
    df['per_broadband'] = 100*df['With_broadband']/df['total_occupied_housing_units']
    df['per_employed'] = 100*df['Pop_in_LaborForce']/ df['Pop_16plus']
    df['MedianHouseholdIncome_10K'] = df['MedianHouseholdIncome']/10000
   
    
    # Removed due to potential collinarity with urbanicity
    
    
    # Bedrooms
    df['per_none_bed'] = df['units_none_bedroom']/ df['total_housing_units']
    df['per_1_bed'] = df['units_1_room']/ df['total_housing_units']
    df['per_2_bed'] = df['units_2_bedroom']/ df['total_housing_units']
    df['per_3_bed'] = df['units_3_bedroom']/ df['total_housing_units']
    df['per_4_bed'] = df['units_4_bedroom']/ df['total_housing_units']
    df['per_5plus_bed'] = df['units_5plus_bedroom']/ df['total_housing_units']
    
    # Age
    df['per_built_2014plus'] = df['yr_built_2014plus']/ df['total_housing_units']
    df['per_built_2010_2013'] = df['yr_built_2010_2013']/ df['total_housing_units']
    df['per_built_2000_2009'] = df['yr_built_2000_2009']/ df['total_housing_units']
    df['per_built_1990_1999'] = df['yr_built_1990_1999']/ df['total_housing_units']
    df['per_built_1980_1989'] = df['yr_built_1980_1989']/ df['total_housing_units']
    df['per_built_1970_1979'] = df['yr_built_1970_1979']/ df['total_housing_units']
    df['per_built_1960_1969'] = df['yr_built_1960_1969']/ df['total_housing_units']
    df['per_built_1950_1959'] = df['yr_built_1950_1959']/ df['total_housing_units']
    df['per_built_1940_1949'] = df['yr_built_1940_1949']/ df['total_housing_units']
    df['per_built_1939earlier'] = df['yr_built_1939earlier']/ df['total_housing_units']
        
    return df

#############################################################################
# Apply Functions and  Merge
#############################################################################
acsdf = cleandp(acsdf)
df = mergeschool(ccd, ccdzip)
ruca = ruca.rename(columns={'ZIP_CODE': 'ZCTA5CE10'})
ruca = ruca[['ZCTA5CE10', 'RUCA1', 'RUCA2']]


df = pd.merge(df, ruca, on = 'ZCTA5CE10', how = 'left')
# Unfortunatly zip codes are updated, so we will not have perfect matches
# to the shape files that represent 2010. Nevertheless, we match 99% of 
# 2010 zip codes and 97.5 of 2021 - need to update with 20198 data.
df = pd.merge(df, acsdf, on = 'ZCTA5CE10', how = 'inner')
    
df = cleandf(df)

    
df.to_csv(outpath)
df.to_csv(outpickle)

