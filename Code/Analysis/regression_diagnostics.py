# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 08:08:46 2023

@author: Trevor Gratz trevormgratz@gmail.com

This file combines features from the American Communities Survey, the
Rural-Urban Commuting Areas, and the Zillow Home Value Index (ZHVI), and runs
regressions to predict the ZHVI. Residual versus fitted plots are used to help
determine the best model specification.

"""

import geopandas as gpd
import pandas as pd
from pysal.model import spreg
import datetime

from matplotlib import pyplot as plt
from pysal.lib import weights
import seaborn
import numpy as np
from pysal.explore import esda
import sys

today = datetime.date.today()
old_stdout = sys.stdout
logpath = r'..\..\LogsOutput\\' + f'regressionlog_{today}.log'
log_file = open(logpath,"w")
sys.stdout = log_file


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

# Try a few different months
# Months chosen because they were
#  A) the same month each year and
#  B)  '02/29/2020' was the last full month prior to lock downs, 
#      '02/28/2022' was the last full month prior to Federal Funds rate hikes
#      '02/28/2023' was the last observation in the series at time of writing.
ys = zillow[['ZCTA5CE10', '02/29/2020', '02/28/2022', '02/28/2023']].copy()
ys = ys.dropna()
# Explore different parameterizations of the y's 
ys['per_change_1'] = ys['02/28/2022']/ys['02/29/2020']
ys['per_change_2'] = ys['02/28/2023']/ys['02/29/2020']

################
# Zipcode Shapefile
zdf = gpd.read_file(r'..\..\..\Data\Geographic\zipcode\tl_2019_us_zcta510\tl_2019_us_zcta510.shp')
zdf['ZCTA5CE10'] = zdf['ZCTA5CE10'].astype(int)

################
## Analytic

adf = pd.merge(zdf, ys,  on ='ZCTA5CE10')
# Lose 52 zillow obs here
adf = pd.merge(adf, feat,  on ='ZCTA5CE10')
# Lose 8 Zillow obs


##############################################################################
# Prep Xs
def prepX(df):
    # Convert Student-to-Teacher ratios to quartiles.
    stratiodum = pd.get_dummies(pd.qcut(df['sch_Elementary_stud_to_tch'], q=4))
    stratiodum.columns = ['stutch_q1', 'stutch_q2', 'stutch_q3', 'stutch_q4' ]
    #Leave-one out
    stratiodum =stratiodum[['stutch_q2', 'stutch_q3', 'stutch_q4' ]]
    
    # Convert Total Population to quartiles.    
    popqrts =  pd.get_dummies(pd.qcut(df['TotalPop'], q=4))
    popqrts.columns = ['pop_q1', 'pop_q2', 'pop_q3', 'pop_q4' ]
    popqrts = popqrts[['pop_q2', 'pop_q3', 'pop_q4' ]]
    
    
    df = pd.concat([df, stratiodum], axis=1)
    df = pd.concat([df, popqrts], axis=1)
    
    # Generate Percent by Race/Ethnicity
    df['Per_AIAN'] = df['Pop_AIAN']/df['TotalPop']
    df['Per_Asian'] = df['Pop_Asian']/df['TotalPop']
    df['Per_NHPI'] = df['Pop_NHPI']/df['TotalPop']
    df['Per_OtherRace'] = df['Pop_OtherRace']/df['TotalPop']
    df['Per_TwoPlusRace'] = df['Pop_TwoPlusRace']/df['TotalPop']
    
    # Bin the 12 categorical rural-urban commuting areas according to USDA
    # categories.
    df['urban'] = df['RUCA1'].isin([1,2,3]).astype(int)
    df['suburb'] = df['RUCA1'].isin([4, 5, 6]).astype(int)
    df['town'] = df['RUCA1'].isin([7, 8, 9]).astype(int)
    df['rural'] = df['RUCA1'].isin([10]).astype(int)
    
    # Miscelanous
    df['per_bach_plus'] = (df['Pop25_plus_with_bachelors'] + df['Pop25_plus_with_gradprof'])/df['Pop25_plus']
    df['per_broadband'] = df['With_broadband']/df['total_occupied_housing_units']
    df['per_employed'] = df['Pop_in_LaborForce']/ df['Pop_16plus']
    df['MedianHouseholdIncome_10K'] = df['MedianHouseholdIncome']/10000
    
    variable_names = ['Per_AIAN', 'Per_Asian','Per_Black', 'Per_Hispanic',
                      'Per_NHPI', 'Per_OtherRace', 'Per_TwoPlusRace',
                      'stutch_q2', 'stutch_q3', 'stutch_q4',
                      'suburb', 'town', 'rural', 'per_bach_plus', 'per_broadband',
                      'MedianHouseholdIncome_10K']
    
    # Percent of households by bedrooms
    # Base is one bedroom
    df['per_none_bed'] = df['units_none_bedroom']/ df['total_housing_units']
    df['per_2_bed'] = df['units_2_bedroom']/ df['total_housing_units']
    df['per_3_bed'] = df['units_3_bedroom']/ df['total_housing_units']
    df['per_4_bed'] = df['units_4_bedroom']/ df['total_housing_units']
    df['per_5plus_bed'] = df['units_5plus_bedroom']/ df['total_housing_units']
    
    # Percent of houses by year built
    # Base is 2014 or later
    df['per_built_2010_2013'] = df['yr_built_2010_2013']/ df['total_housing_units']
    df['per_built_2000_2009'] = df['yr_built_2000_2009']/ df['total_housing_units']
    df['per_built_1990_1999'] = df['yr_built_1990_1999']/ df['total_housing_units']
    df['per_built_1980_1989'] = df['yr_built_1980_1989']/ df['total_housing_units']
    df['per_built_1970_1979'] = df['yr_built_1970_1979']/ df['total_housing_units']
    df['per_built_1960_1969'] = df['yr_built_1960_1969']/ df['total_housing_units']
    df['per_built_1950_1959'] = df['yr_built_1950_1959']/ df['total_housing_units']
    df['per_built_1940_1949'] = df['yr_built_1940_1949']/ df['total_housing_units']
    df['per_built_1939earlier'] = df['yr_built_1939earlier']/ df['total_housing_units']
    
    housecontrols = ['units_median_room', 'per_none_bed', 'per_2_bed', 'per_3_bed',
                     'per_4_bed', 'per_5plus_bed', 'per_built_2010_2013',
                     'per_built_2000_2009', 'per_built_1990_1999', 
                     'per_built_1980_1989', 'per_built_1970_1979', 
                     'per_built_1960_1969', 'per_built_1950_1959',
                     'per_built_1940_1949', 'per_built_1939earlier']
    
    
    df['ln_per_change_1'] = np.log(df['per_change_1'])
    df['ln_per_change_2'] = np.log(df['per_change_2'])

    df['ln_02/29/2020'] = np.log(df['02/29/2020'])
    df['ln_02/28/2022'] = np.log(df['02/28/2022'])
    df['ln_02/28/2023'] = np.log(df['02/28/2023'])
    
    # Try combinations of: 
    #    A) Percent change
    #    B) Log Percent Change
    #    C) Log of ZHVI (not percent change)
    yvars = ['per_change_1', 'per_change_2', 'ln_per_change_1',
             'ln_per_change_2', '02/29/2020', '02/28/2022', '02/28/2023',
             'ln_02/29/2020', 'ln_02/28/2022', 'ln_02/28/2023']
    
    analytic = df[yvars + variable_names + housecontrols + ['geometry']].copy()
    analytic = analytic.dropna()
    return analytic, variable_names, housecontrols

analytic, variable_names, housecontrols = prepX(df=adf)

#############################
# Choose Weights matrix
w = weights.KNN.from_dataframe(analytic, k=5)
w.transform = "R"

##############################################################################
## Diagnostic Functions
##############################################################################
def gethat(xmat):
    # H = X (X_t X)-1 X_t
    # Used for computation of standardized residuals
    xmat = xmat.to_numpy()
    txmat = np.matrix.transpose(xmat)
    mid =  np.linalg.inv(np.matmul(txmat, xmat))
    left = np.matmul(xmat, mid)
    hat = np.matmul(left, txmat )
    h_i = np.diagonal(hat)
    return hat, h_i

def getresids(df, m, y, h_ii):
    # Use after getting the h_ii values (i.e. run gethat)
    df['residual'] = m.u
    df['fitted'] =  df[y] - df['residual']
    df['h_ii'] = h_ii
    rse = (m.sig2)**(1/2)
    df['std_resid'] = df['residual'] / (rse * ((1-df['h_ii'])**(1/2)))
    return df

def moranresidplot(df, outpath):
    # Plot residuals against the lag residuals (i.e. the neighbors average
    # residuals).Patterns in plots would indicate autocorrelation.
    moran_I_residuals = round(esda.moran.Moran(df['std_resid'], w).I,2)
    
    lag_residual = weights.spatial_lag.lag_spatial(w, df['std_resid'])
    ax = seaborn.regplot(
        x=df['std_resid'],
        y=lag_residual.flatten(),
        line_kws=dict(color="orangered"),
        ci=None,
    )
    ax.spines[['right', 'top']].set_visible(False)
    ax.set_xlabel("Model Residuals - $u$")
    ax.set_ylabel("Spatial Lag of Model Residuals - $W u$");
    ax.set_title(f"Residual Global Moran's I: {moran_I_residuals}")
    plt.savefig(outpath)
    plt.close()
    
##############################################################################
## OLS Regressions
##############################################################################

# Try the 3*2*2 combinations of models. Here 'temporallag' means we include
# the '02/28/2020' y value in regressions of later observations. This is 
# similar to a value-added model from the education literature.
yvars = ['02/28/2022', 'per_change_1', 'temporallag']
transforms = ['None', 'log']
controls = [variable_names, variable_names + housecontrols]

for y in yvars:
    ytemp = y
    for c in controls:
        for t in transforms:
            
            tempvars = c.copy()
            
            if len(tempvars) > 25:
                outmessage = 'with housing controls'
            else:
                outmessage = 'without housing controls'

            
            if y == 'temporallag':
                outmessage = outmessage + ' and temporal lag'
                if t=='None':
                    tempvars.append('02/29/2020')
                    ytemp = '02/28/2022'
                    
                else:
                    tempvars.append('ln_02/29/2020')
                    ytemp = 'ln_02/28/2022'
                    ytemp = ytemp.replace('ln_ln_', 'ln_')
            else:
                if t!='None':
                    ytemp = 'ln_'+y
                    ytemp = ytemp.replace('ln_ln_', 'ln_')

            m1 = spreg.OLS(
                # Dependent variable
                analytic[[ytemp]].values,
                # Independent variables
                analytic[tempvars].values,
                # Dependent variable name
                name_y=y,
                # Independent variable name
                name_x=tempvars,
            )
            outmessage = ytemp +" "+ outmessage
            print('\n\n-------------------------------------------------------')
            print(outmessage)
            print('-------------------------------------------------------\n')
            print(m1.summary)
            ##################################################################
            # Diagnostics
            hat, hii = gethat(xmat=analytic[tempvars])
            tempdf = getresids(df = analytic.copy(), m=m1, y = ytemp, h_ii = hii)
            outmessage=outmessage.replace(r'/', '_')
            # Standardized Residual Vs Fitted
            plt.scatter(tempdf['fitted'], tempdf['std_resid'])
            plt.title(f'Std Residuals Vs Fitted: {outmessage}')
            plt.xlabel("Fitted")
            plt.ylabel("Standardized Residuals")
            savepath = r'..\..\LogsOutput\Diagnostics\\' + f'residfitted_{outmessage}.png'
            plt.savefig(savepath)
            plt.close()
            # Moran Plot
            moranout = r'..\..\LogsOutput\Diagnostics\\' + f'moranplot_{outmessage}.png'
            moranresidplot(df=tempdf, outpath=moranout)

##############################################################################
# Spatial Regressions 
##############################################################################

# Similar to above, but with Spatial Lag models.

yvars = ['per_change_1', 'temporallag']
transforms = ['None', 'log']
controls = [variable_names, variable_names + housecontrols]

for y in yvars:
    ytemp = y
    for c in controls:
        for t in transforms:
            
           
            tempvars = c.copy()
            
            if len(tempvars) > 25:
                outmessage = 'with housing controls'
            else:
                outmessage = 'without housing controls'

            
            if y == 'temporallag':
                outmessage = outmessage + ' and temporal lag'
                if t=='None':
                    tempvars.append('02/29/2020')
                    ytemp = '02/28/2022'
                    
                else:
                    tempvars.append('ln_02/29/2020')
                    ytemp = 'ln_02/28/2022'
                    ytemp = ytemp.replace('ln_ln_', 'ln_')
            else:
                if t!='None':
                    ytemp = 'ln_'+y
                    ytemp = ytemp.replace('ln_ln_', 'ln_')

            m1 = spreg.GM_Lag(
                # Dependent variable
                analytic[[ytemp]].values,
                # Independent variables
                analytic[tempvars].values,
                # Spatial weights matrix
                w=w,
                # Dependent variable name
                name_y=y,
                # Independent variable name
                name_x=tempvars,
            )

            
            outmessage = 'Spatial Reg '+ytemp +" "+ outmessage
            print('\n\n-------------------------------------------------------')
            print(outmessage)
            print('-------------------------------------------------------\n')
            print(m1.summary)
            ##################################################################
            # Diagnostics
            hat, hii = gethat(xmat=analytic[tempvars])
            tempdf = getresids(df = analytic.copy(), m=m1, y = ytemp, h_ii = hii)
            outmessage=outmessage.replace(r'/', '_')
            # Standardized Residual Vs Fitted
            plt.scatter(tempdf['fitted'], tempdf['residual'])
            plt.title(f'Residuals Vs Fitted: {outmessage}')
            plt.xlabel("Fitted")
            plt.ylabel("Residuals")
            savepath = r'..\..\LogsOutput\Diagnostics\\' + f'residfitted_{outmessage}.png'
            plt.savefig(savepath)
            plt.close()

###############################################################################
# Best performing model - Log transformed ZHVI without a lagged ZHVI included.

m1 = spreg.GM_Lag(
    # Dependent variable
    analytic[['ln_02/28/2022']].values,
    # Independent variables
    analytic[variable_names + housecontrols].values,
    # Spatial weights matrix
    w=w,
    # Dependent variable name
    name_y='ln_02/28/2022',
    # Independent variable name
    name_x=variable_names + housecontrols,
)

hat, hii = gethat(xmat=analytic[variable_names + housecontrols])
tempdf = getresids(df = analytic.copy(), m=m1, y = 'ln_02/28/2022', h_ii = hii)
# Standardized Residual Vs Fitted
plt.scatter(tempdf['fitted'], tempdf['residual'])
plt.title(f'Spatial Lag: Residuals Vs Fitted: Log ZHVI with Housing Controls')
plt.xlabel("Fitted")
plt.ylabel("Residuals")
savepath = r'..\..\LogsOutput\Diagnostics\\' + f'residfitted_patial Lag Residuals Vs Fitted Log ZHVI with Housing Controls.png'
plt.savefig(savepath)
plt.close()

moranout = r'..\..\LogsOutput\Diagnostics\\' + f'moranplot_residfitted_patial Lag Residuals Vs Fitted Log ZHVI with Housing Controls.png'
moranresidplot(df=tempdf, outpath=moranout)
