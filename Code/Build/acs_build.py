# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 07:43:27 2023

@author: Trevor Gratz, trevormgratz@gmal.com

This file pulls in all 2019 5-year American Community Survey variables specified in the 
'proj_globals' folder, does some minimal cleaning, and saves them in the
acs_data.csv file.
"""

import pandas as pd
import numpy as np
from ACS_DataProfile_APIPull import dppull
from proj_globals import acs5_2019_dict
import os

outpath = r'..\..\..\Data\Intermediate\acs_data.csv'

# Add Key before running
cen_key = ''

# Data Profile Data
def clean_dataprofile(dpvars = acs5_2019_dict):
    # For Variable list
    # https://api.census.gov/data/2019/acs/acs5/profile/variables.html
    
  
    # There is a cut off on the number of variables (8) you can select. For a
    # single dataset creation, just loop over them one at time.
    dpdf = pd.DataFrame(columns=['NAME', 'state',
                                 'zip code tabulation area'])
    for key, value in dpvars.items():
        print(key)
        temp, call = dppull(geography='zip', year='2019', acsversion='5',
                            county=['*'], state = ['*'],
                            variables = [key], cen_key=cen_key)
        temp[key] = temp[key].astype(float) 
        dpdf = pd.merge(dpdf, temp, on=['NAME', 'state',
                                        'zip code tabulation area'],
                        how='outer')
    
    
    # Some basic manipulations
    dpdf['AssociatesHigher'] = ((dpdf['DP02_0064E'] + dpdf['DP02_0065E'] +
                                 dpdf['DP02_0066E']) / dpdf['DP02_0059E'])
    
    dpdf['Per_HSDip'] = (dpdf['DP02_0067E'] / dpdf['DP02_0059E'])
    
    dpdf['Per_CostBurdened'] = ((dpdf['DP04_0114E'] + dpdf['DP04_0115E'] +
                                 dpdf['DP04_0123E'] + dpdf['DP04_0124E'] +
                                 dpdf['DP04_0141E'] + dpdf['DP04_0142E'])
                                / dpdf['DP04_0002E'])
    
    dpdf['Per_ForeignBorn'] = dpdf['DP02_0094E'] / dpdf['DP02_0088E']
    dpdf['Per_Under18']     = dpdf['DP05_0019E'] / dpdf['DP05_0001E']
    dpdf['Per_Over65']      = dpdf['DP05_0024E'] / dpdf['DP05_0001E']
    dpdf['Per_Hispanic']    = dpdf['DP05_0071E'] / dpdf['DP05_0001E']
    dpdf['Per_Black']       = dpdf['DP05_0078E'] / dpdf['DP05_0001E']
    
    dpdf['Per_15_25age']    = ((dpdf['DP05_0008E'] + dpdf['DP05_0009E'])
                               / dpdf['DP05_0001E'])
    
    # Human readable variables....
    dpdf = dpdf.rename(columns=dpvars)
    
    # One obs
    dpdf.loc[dpdf['MedianHouseholdIncome'] < 0, 'MedianHouseholdIncome'] = np.nan
    return dpdf

dpdf = clean_dataprofile()

dpdf.to_csv(outpath)