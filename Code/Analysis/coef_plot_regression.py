# -*- coding: utf-8 -*-
"""
Created on Fri Apr  7 10:59:50 2023

@author: trevo
"""

import geopandas as gpd
import pandas as pd
from pysal.model import spreg
import datetime
import pysal.model.spreg.diagnostics as D
from matplotlib import pyplot as plt
from pysal.lib import weights
import seaborn
import numpy as np
from pysal.explore import esda
import scipy

today = datetime.date.today()


# import sys
# old_stdout = sys.stdout
# logpath = r'..\..\LogsOutput\\' + f'coeffient_plot_log_{today}.log'
# log_file = open(logpath,"w")
# sys.stdout = log_file

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

################
# Zip Shape
zdf = gpd.read_file(r'..\..\..\Data\Geographic\zipcode\tl_2019_us_zcta510\tl_2019_us_zcta510.shp')
zdf['ZCTA5CE10'] = zdf['ZCTA5CE10'].astype(int)

##############################################################################
# Prep Xs

housecontrols = ['units_median_room', 'per_none_bed', 'per_2_bed', 'per_3_bed',
                     'per_4_bed', 'per_5plus_bed', 'per_built_2010_2013',
                     'per_built_2000_2009', 'per_built_1990_1999', 
                     'per_built_1980_1989', 'per_built_1970_1979', 
                     'per_built_1960_1969', 'per_built_1950_1959',
                     'per_built_1940_1949', 'per_built_1939earlier']

variable_names = ['Per_AIAN', 'Per_Asian','Per_Black', 'Per_Hispanic',
                      'Per_NHPI', 'Per_OtherRace', 'Per_TwoPlusRace',
                      'stutch_q2', 'stutch_q3', 'stutch_q4',
                      'suburb', 'town', 'rural', 'per_bach_plus', 'per_broadband',
                      'MedianHouseholdIncome_10K']


def prepX(df, housecontrols=housecontrols, variable_names=variable_names):
    stratiodum = pd.get_dummies(pd.qcut(df['sch_Elementary_stud_to_tch'], q=4))
    stratiodum.columns = ['stutch_q1', 'stutch_q2', 'stutch_q3', 'stutch_q4' ]
    #Leaveone out
    stratiodum =stratiodum[['stutch_q2', 'stutch_q3', 'stutch_q4' ]]
    
    popqrts =  pd.get_dummies(pd.qcut(df['TotalPop'], q=4))
    popqrts.columns = ['pop_q1', 'pop_q2', 'pop_q3', 'pop_q4' ]
    popqrts = popqrts[['pop_q2', 'pop_q3', 'pop_q4' ]]
    
    
    df = pd.concat([df, stratiodum], axis=1)
    df = pd.concat([df, popqrts], axis=1)

    df['Per_Black'] = 100*df['Per_Black']    
    df['Per_Hispanic'] = 100*df['Per_Hispanic']    

    df['Per_AIAN'] = 100*df['Pop_AIAN']/df['TotalPop']
    df['Per_Asian'] = 100*df['Pop_Asian']/df['TotalPop']
    df['Per_NHPI'] = 100*df['Pop_NHPI']/df['TotalPop']
    df['Per_OtherRace'] = 100*df['Pop_OtherRace']/df['TotalPop']
    df['Per_TwoPlusRace'] = 100*df['Pop_TwoPlusRace']/df['TotalPop']
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
    # Base is one bedroom
    df['per_none_bed'] = df['units_none_bedroom']/ df['total_housing_units']
    df['per_2_bed'] = df['units_2_bedroom']/ df['total_housing_units']
    df['per_3_bed'] = df['units_3_bedroom']/ df['total_housing_units']
    df['per_4_bed'] = df['units_4_bedroom']/ df['total_housing_units']
    df['per_5plus_bed'] = df['units_5plus_bedroom']/ df['total_housing_units']
    
    # Age
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

    
    analytic = df[['ZCTA5CE10'] + variable_names + housecontrols].copy()
    analytic = analytic.dropna()
    return analytic

feat2019 = prepX(df=feat)
adf = pd.merge(zdf, feat2019,  on ='ZCTA5CE10')


#############################
# Calaculte Coeffieencts


def calccoefs():
    ols = []
    coefdf = pd.DataFrame()    
    vardf = pd.DataFrame(['Constant'] + variable_names + housecontrols + ['W'] )
    
    # No observations of these.
    vnametemp = variable_names.copy()

    for y in ys:
        print(y)
        tempy = zillow[['ZCTA5CE10', y]].copy()
        tempy['log_y'] = np.log(tempy[y])
        tempy = tempy.dropna()
        tempdf = pd.merge(adf, tempy,  on ='ZCTA5CE10')
        # Filter to Cluster if it isn't all of them
            
        
        w = weights.KNN.from_dataframe(tempdf, k=5)
        w.transform = "R"
        
        # Verify Autocorrelation in each regression.
        # m1 = spreg.OLS(
        #             # Dependent variable
        #             tempdf[['log_y']].values,
        #             # Independent variables
        #             tempdf[variable_names + housecontrols].values,
        #             # Dependent variable name
        #             name_y=y,
        #             # Independent variable name
        #             name_x=variable_names + housecontrols,
        #         )
        # moran_I_residuals = esda.moran.Moran(m1.u, w)
        # ols.append((moran_I_residuals.I, moran_I_residuals.p_norm))
        
        # Perform Spatial Lag Regression
        m1 = spreg.GM_Lag(
                    # Dependent variable
                    tempdf[['log_y']].values,
                    # Independent variables
                    tempdf[vnametemp + housecontrols].values,
                    # Spatial weights matrix
                    w=w,
                    # Dependent variable name
                    name_y=y,
                    # Independent variable name
                    name_x=vnametemp + housecontrols,
                )
        
        # Store Results
        vardf = pd.DataFrame(['Constant'] + vnametemp + housecontrols + ['W'] )
        betas = pd.DataFrame(m1.betas)
        se = pd.DataFrame(D.se_betas(m1))
        
        # Betas
        df = pd.concat([vardf, betas], axis=1, ignore_index=True)
        df.columns=['name', 'beta']
        df['id'] = 1
        df = df.pivot(columns='name', values='beta', index='id').reset_index()
        df = df.drop(columns='id')
        df['month'] = y
        
        # Se
        dfse = pd.concat([vardf, se], axis=1, ignore_index=True)
        dfse.columns=['name', 'beta']
        dfse['name'] = dfse['name'] + '_se'
        dfse['id'] = 1
        dfse = dfse.pivot(columns='name', values='beta', index='id').reset_index()
        dfse = dfse.drop(columns='id')
    
        dfse['month'] = y
        
        row = pd.merge(df, dfse, on = 'month')
        coefdf=pd.concat([coefdf, row])
        
    coefdf['month'] = pd.to_datetime(coefdf['month']) 

    return coefdf, ols

#################################################
# Build Coefficient Dataframe    
coefdf, ols_all = calccoefs()
 
tran_names = []
for v in variable_names:
    coefdf['trans_'+v] = 100*(np.exp(coefdf[v]) - 1)
    tran_names.append('trans_'+v)

outdf = coefdf[['month'] + tran_names].copy()
outpath = r'..\..\..\Data\\' + f'Coefficients_{today}.csv'
outdf.to_csv(outpath)

##############################################################################
# Main Figure
##############################################################################


# Urbanicity
fig, ax = plt.subplots()
fig.set_size_inches(18.5, 10.5)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.set_ylabel(f"Percent Change",  fontsize=28)
for c in [('trans_suburb', 'Suburban'), ('trans_town', 'Town'), ('trans_rural', 'Rural')]:
    x = coefdf['month']
        
    ax.plot(x, coefdf[c[0]], label = f'Urbanicity: {c[1]}', linewidth = 3)
    plt.axvline(datetime.datetime(2020, 2, 29),
                color = 'black', linestyle ='--')
    plt.axvline(datetime.datetime(2022, 2, 28),
                color = 'black', linestyle ='--')
    
plt.text(datetime.datetime(2020, 2, 22), -3, 'Lockdowns',
        horizontalalignment='right',  fontsize=26)
plt.text(datetime.datetime(2022, 2, 21), -3, 'Federal Fund\nRate Hikes',
          horizontalalignment='right',  fontsize=26)
    
ax.legend(frameon=False,  fontsize=24) 
ax.tick_params(axis='both', which='major', labelsize=24)
ax.tick_params(axis='both', which='minor', labelsize=24)
  
savepath = r'..\..\LogsOutput\CoefPlots\Report_Urbaniciyt.svg'
plt.savefig(savepath)
plt.close()