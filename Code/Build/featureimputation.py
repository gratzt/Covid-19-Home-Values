# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 11:31:11 2023

@author: trevo

Following: https://machinelearningmastery.com/stacking-ensemble-machine-learning-with-python/
    https://bmcmedinformdecismak.biomedcentral.com/articles/10.1186/s12911-022-01752-6
    https://journalofbigdata.springeropen.com/articles/10.1186/s40537-021-00516-9

"""
import pandas as pd
from sklearn.linear_model import LinearRegression, ElasticNet
from sklearn.neural_network  import MLPRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.ensemble import StackingRegressor
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RepeatedKFold, GridSearchCV
from sklearn.impute import SimpleImputer
# compare ensemble to each standalone models for regression
from numpy import mean
from numpy import std
from matplotlib import pyplot
import numpy as np

# Features
feat = pd.read_csv(r'..\..\..\Data\Clean Data\features2019.csv')

################

housecontrols = ['units_median_room', 'per_none_bed', 'per_2_bed', 'per_3_bed',
                     'per_4_bed', 'per_5plus_bed', 'per_built_2010_2013',
                     'per_built_2000_2009', 'per_built_1990_1999', 
                     'per_built_1980_1989', 'per_built_1970_1979', 
                     'per_built_1960_1969', 'per_built_1950_1959',
                     'per_built_1940_1949', 'per_built_1939earlier']

variable_names = ['Per_AIAN', 'Per_Asian','Per_Black', 'Per_Hispanic',
                      'Per_NHPI', 'Per_OtherRace', 'Per_TwoPlusRace',
                      'suburb', 'town', 'rural', 'per_bach_plus', 'per_broadband',
                      'MedianHouseholdIncome_10K']

allvars = variable_names + housecontrols
########################
# Standardize variables
# Create Imputed Standardized variables
sort_vdata = []
for v in allvars:
    mval = feat[v].mean()
    stdval = feat[v].std()
    feat['trans_' + v] = (feat[v] - mval)/stdval
    sort_vdata.append((v, mval, stdval))

imp_mean = SimpleImputer(missing_values=np.nan, strategy='mean')    
    
########################
# Loop through variables starting with those with the fewest missing values

nmiss = []
for v in allvars:
    nmiss.append((v, feat[v].isna().sum()))
    
miss_list = sorted(nmiss, key=lambda x: (x[1], x[0]))

############################

# get a stacking ensemble of models
def get_stacking():
     # define the base models
     level0 = list()
     level0.append(('LinReg', LinearRegression()))
     level0.append(('KNN', KNeighborsRegressor()))
     level0.append(('RF', RandomForestRegressor()))
     level0.append(('svm', SVR()))
     # define meta learner model
     level1 = SVR()
     # define the stacking ensemble
     model = StackingRegressor(estimators=level0, final_estimator=level1, cv=5)
     return model

def get_models(stackonly=False):
    if stackonly == False:
         models = dict()
         models['LinReg'] = LinearRegression()
         models['KNN'] = KNeighborsRegressor()
         models['RF'] = RandomForestRegressor()
         models['svm'] = SVR()
         models['stacking'] = get_stacking()
    else:
        models = dict()
        models['stacking'] = get_stacking()
        
    return models

# evaluate a given model using cross-validation
def evaluate_model(model, X, y):
     cv = RepeatedKFold(n_splits=10, n_repeats=3, random_state=1)
     scores = cross_val_score(model, X, y, scoring='neg_mean_absolute_error', cv=cv, n_jobs=-1, error_score='raise')
     return scores







# Step 1: Keep Only Non-missing observations
# Step 2: Develop stacked regression
# Step 3: Use Simple Imputer on full data
# Step 4: Use model from Step 2 to impute response
# Step 5: Replace missing values in both the 'response' variables and the
#         'imputed' variables
    









tempdf = feat[allvars + ['trans_' + i for i in allvars]].copy()
tempdf = tempdf.dropna()
# For testing code
tempdf = tempdf.iloc[0:500,]

temp = variable_names[0:-1] + housecontrols    
X = tempdf[['trans_' + i  for i in temp]]
y = tempdf[variable_names[-1:]] 




level0 = list()
level0.append(('LinReg', LinearRegression()))
level0.append(('KNN', KNeighborsRegressor()))
level0.append(('RF', RandomForestRegressor()))
level0.append(('svm', SVR()))
     # define meta learner model
level1 = LinearRegression()
# define the stacking ensemble
model = StackingRegressor(estimators=level0, final_estimator=level1, cv=5)
model.fit(X,y.values.ravel())
test=model.predict(feat)


# params = {'RF__max_features': ['sqrt', 'log2'],
#           'KNN__n_neighbors': [1, 3, 4 ,5, 6, 7, 10, 100],
#           'KNN__weights': ['uniform', 'distance'],
#           'svm__kernel': ['rbf']
#           }

# grid = GridSearchCV(estimator=model, 
#                     param_grid=params,
#                     cv=5)
# grid.fit(X, y.values.ravel())

# res = pd.DataFrame(grid.cv_results_)

# model.fit(X, y)






# Loop through the variables in order of least missing


models = get_models()
# evaluate the models and store results
results, names = list(), list()
for name, model in models.items():
     scores = evaluate_model(model, X, y.values.ravel())
     results.append(scores)
     names.append(name)
     print('>%s %.3f (%.3f)' % (name, mean(scores), std(scores)))
pyplot.boxplot(results, labels=names, showmeans=True)
pyplot.show()