# -*- coding: utf-8 -*-
"""
Created on Wed May 11 10:07:27 2022

@author: Trevor Gratz trevormgratz@gmail.com

This function makes api calls to the American Community Survey's Data 
Profile tables. You can find out more information about the variables
availalbe in the data profiles at the link below.

https://api.census.gov/data/2020/acs/acs5/profile/variables.html

NOTE: The zip code geography doesn't allow for subsetting in its current form.
      If you plan on making many calls, you will need a Census API key.

"""

def dppull(geography='county', year='2020', acsversion='5', variables=[],
           state=['*'], county =['*'], place =['*'], tract=['*'], table='',
            cen_key=''):
    '''
    This function makes api calls to the American Community Survey's Data 
    Profile tables. You can find out more information about the variables
    availalbe in the data profiles at the link below.
    
    https://api.census.gov/data/2020/acs/acs5/profile/variables.html
    

    Parameters
    ----------
    geography : TYPE string
        DESCRIPTION. Determines what level to grab the data at, options are
                    'state', 'county', 'tract', and 'zip'. 
                    The default is 'county'. Zips cannot be subsetted by state
                    or county.
    year : TYPE, string
        DESCRIPTION. What ACS year of the dataset to grab The default is '2020'
    acsversion : TYPE, optional
        DESCRIPTION. Options are 5 or 1. The default is '5'.
    variable : TYPE, list of strings
        DESCRIPTION. This allows the user to select individual or multiple
                     data profile variables. Of the form DP0X_XXXXX.
                     The default is [''].
    state : TYPE List of strings, optional
        DESCRIPTION. A list of fips state codes. The default is ['*'].
    county : TYPE List of strings , optional
        DESCRIPTION. A list of fips county codes. The default is ['*'].
    place : TYPE List of strings , optional
        DESCRIPTION. A list of fips place codes. The default is ['*'].
    tract : TYPE List of strings, optional
        DESCRIPTION. List of fips tract codes. The default is ['*'].
    table : TYPE string, optional
        DESCRIPTION. The default is ''. Allows the user to pull the entire
        data profile for one of the four data profiles. Acceptable values are
        'DP02', 'DP03', 'DP04', 'DP05'.
    cen_key: TYPE string, optional
        DESCRIPTION.  The default is ''. This is a user specific Census API key.
        The API lets the user make a number of calls before requiring an API,
        hence this is an optional argument.

    Returns
    -------
    rawdata : Pandas dataframe containing data.
    apicall : The call made to the ACS

    Examples
    -------
    a1, call = dppull(geography='state', year='2020', acsversion='5',
                      variables=['DP04_0005E'])
    a2, call = dppull(geography='county', year='2020', acsversion='5',
                      variables=['DP04_0005E'])
    a3, call = dppull(geography='county', year='2020', acsversion='5',
                      variables=['DP04_0005E'],
                county=['053'], state = ['53'])

    a4, call = dppull(geography='county', year='2020', acsversion='5',
                variables = ['DP02_0001E', 'DP04_0005E'], county='*',
                state = '53')

    a5, call = dppull(geography='county', year='2020', acsversion='5',
                      county=['*'], state = ['53', '41'],
                      variables = ['DP02_0001E', 'DP04_0005E'])

    # Pulling the whole table
    a6, call = dppull(geography='county', year='2020', acsversion='5',
                      county='053', state = '53', table ='DP03')

    '''
    import requests as req
    import io
    import pandas as pd

    state = ','.join(state)
    county = ','.join(county)
    place = ','.join(place)
    tract = ','.join(tract)

    if len(variables) != 0:
        variables = ','.join(variables).upper()
    elif len(table) == 0:
        raise ValueError('Variables or a full table name must be provided')

    # Data Profile is handled differntly than other ACS API
    profile = r'/profile'

    # Currently supports pulling states, counties, tracts, and zip codes 
    # (Main geos for Data Profiles)
    
    if geography == 'state':
        geo = f'for=state:{state}'

    elif geography == 'county':
        geo = f'for=county:{county}&in=state:{state}'

    elif geography == 'place':
        geo = f'for=place:{place}&in=state:{state}'
        
    elif geography == 'tract':
        geo = f'for=tract:{tract}&in=state:{state}&in=county:{county}'
    elif geography == 'zip':
        geo = r'for=zip%20code%20tabulation%20area:*'

    # Call differs for grabbing the whole table or specific variables
    if len(table) == 0:
        apicall = f'https://api.census.gov/data/{year}/acs/acs{acsversion}{profile}?get=NAME,{variables}&{geo}'
    else:
        apicall = f'https://api.census.gov/data/{year}/acs/acs{acsversion}{profile}?get=group({table})&{geo}'

    # Try three times in case there is a browser connection issue
    counter = 0
    success = False
    while ((counter < 3) & (success == False)):
        try:
            if cen_key != '':
                apicall = apicall + f'&key={cen_key}'
            r = req.get(apicall)
            rawdata = pd.read_json(io.StringIO(r.content.decode('utf-8')))
            rawdata.columns = rawdata.iloc[0]
            rawdata = rawdata.drop(index=0)
            success = True
        except:
            counter += 1

    
    if success == False:
         print('No luck, try entering the API Call to the browser')
         return 'no data error', apicall
     
    return rawdata, apicall
