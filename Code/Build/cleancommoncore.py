# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 12:47:50 2023

@author: Trevor Gratz trevormgratz@gmail.com

This file loads the 2018-2019 Common Core Data, cleans it, and merges it into
one flat file. 
"""
import pandas as pd

##############################################################################
# Load Data

df_dir = pd.read_csv(r'..\..\..\Data\Raw Data with Profiles\NCES\commoncore\commoncore\directory_ccd_sch_029_1819_w_1a_091019.csv',
                    encoding='cp1252')

df_mem=pd.read_csv(r'..\..\..\Data\Raw Data with Profiles\NCES\commoncore\commoncore\membership_ccd_SCH_052_1819_l_1a_091019.csv',
                encoding='cp1252')

df_lunch = pd.read_csv(r'..\..\..\Data\Raw Data with Profiles\NCES\commoncore\commoncore\lunch_ccd_sch_033_1819_l_1a_091019.csv',
                    encoding='cp1252')

df_staff = pd.read_csv(r'..\..\..\Data\Raw Data with Profiles\NCES\commoncore\commoncore\staff_ccd_sch_059_1819_l_1a_091019.csv',
                    encoding='cp1252')

df_schar = pd.read_csv(r'..\..\..\Data\Raw Data with Profiles\NCES\commoncore\commoncore\schoolchar_ccd_sch_129_1819_w_1a_091019.csv',
                    encoding='cp1252')
##############################################################################
# Clean Directory


def cleandirectory(df, year):
    df['year'] = year
    df = df.loc[df['SCH_TYPE'] == 1, ]
    # Keep Elementary, Middle, and High Schools
    df = df.loc[df['LEVEL'].isin(["Elementary", "Middle", "High"]), ]
    # Remove Inactive/Closed Schools
    df = df.loc[~df['UPDATED_STATUS_TEXT'].isin(["Closed", "Future",
                                                 "Inactive"]), ]
    df = df[['NCESSCH', 'LEVEL']]
    return df

##############################################################################
# Clean Gender


def cleanGender(df, year):
    df['year'] = year

    
    if 'RACE_ETHNICITY' in df.columns:
        df.rename(columns={'RACE_ETHNICITY': 'RACE'}, inplace=True)
                         
    # Grab Total Enrollment 
    tedf = df.copy()
    todrop = ~((tedf['GRADE'] == 'No Category Codes') &
               (tedf['RACE'] == 'No Category Codes') &
               (tedf['SEX'] == 'No Category Codes') &
               (tedf['TOTAL_INDICATOR'] == 'Derived - Education Unit Total minus Adult Education Count'))
    tedf.drop(index=tedf.index[todrop], inplace=True)
    tedf.rename(columns={'STUDENT_COUNT': 'School_Total_Enrollment'}, inplace=True)
    todrop = [ i for i in tedf.columns if i not in ['NCESSCH', 'School_Total_Enrollment']]
    tedf.drop(columns=todrop, inplace=True)
    
    # Get Gender Specific Enrollment           
    todrop = ((df['GRADE'] == 'No Category Codes') |
              (df['GRADE'] == 'Adult Education')   |
              (df['GRADE'] == 'Ungraded')          |
              (df['RACE'] == 'No Category Codes')  |
              (df['SEX'] == 'No Category Codes')   |    
              (df['SEX'] == 'Not Specified'))
    df.drop(index=df.index[todrop], inplace=True)
    df = df[['NCESSCH', 'year', 'SEX', 'STUDENT_COUNT']].groupby(['NCESSCH', 'year', 'SEX']).sum()
    df = df.unstack('SEX')            
    df.columns = df.columns.get_level_values(1) + '_count'
    df.reset_index(inplace=True)
    # Check Gender_totalenrollment against other enrollment counts
    df['gender_totalenrollment'] = df['Female_count'] + df['Male_count']
    df['per_female'] = 100 * (df['Female_count'] / df['gender_totalenrollment'])
    df['per_male'] = 100 * (df['Male_count'] / df['gender_totalenrollment'])
    df.drop(columns=['Female_count', 'Male_count'], inplace=True)
    df = pd.merge(df, tedf, on='NCESSCH', how='inner')
    return df

##############################################################################
# Clean Race and Ethnicity 


def cleanRace(df, year):
    df['year'] = year
    
    if 'RACE_ETHNICITY' in df.columns:
        df = df.rename(columns={'RACE_ETHNICITY': 'RACE'})  
        
    todrop = ((df['GRADE'] != 'No Category Codes')  | 
              (df['RACE'] == 'No Category Codes')   |
              (df['RACE'] == 'Not Specified')       |
              (df['SEX'] == 'No Category Codes'))

    df.drop(index=df.index[todrop], inplace=True)
    df = df[['NCESSCH', 'year', 'RACE', 'STUDENT_COUNT']].groupby(['NCESSCH', 'year', 'RACE']).sum()
    df = df.unstack('RACE')
    df.columns = df.columns.get_level_values(1) + '_count'
    df = df.reset_index()
    df['race_totalenrollment'] = df[['American Indian or Alaska Native_count',
                                     'Asian_count', 'Black or African American_count',
                                     'Hispanic/Latino_count',
                                     'Native Hawaiian or Other Pacific Islander_count',
                                     'Two or more races_count', 'White_count']].sum(axis=1) 
    
    df['per_nativeamerican'] = 100*(df['American Indian or Alaska Native_count']/ df['race_totalenrollment'])
    df['per_asian'] = 100*(df['Asian_count']/ df['race_totalenrollment'])
    df['per_black'] = 100*(df['Black or African American_count']/ df['race_totalenrollment'])
    df['per_hispanic'] = 100*(df['Hispanic/Latino_count']/ df['race_totalenrollment'])
    df['per_nhpi'] = 100*(df['Native Hawaiian or Other Pacific Islander_count']/ df['race_totalenrollment'])
    df['per_multiracial'] = 100*(df['Two or more races_count']/ df['race_totalenrollment'])
    df['per_white'] = 100*(df['White_count']/ df['race_totalenrollment'])
    
    df.drop(columns=['American Indian or Alaska Native_count',
                     'Asian_count', 'Black or African American_count',
                     'Hispanic/Latino_count',
                     'Native Hawaiian or Other Pacific Islander_count',
                     'Two or more races_count', 'White_count',], inplace=True)
    return df

##############################################################################
# Clean Lunch Program


def cleanFRPL(df, year):
    df['year'] = year
    
    # Get Direct Certification to merge in later
    dc = df.loc[df["DATA_GROUP"]=='Direct Certification',].copy()
    dc = dc[['NCESSCH', 'STUDENT_COUNT']]
    dc = dc.rename(columns={'STUDENT_COUNT': 'Direct_Certified_Count'})
    
    # Total FRPL - Note Delaware, Tennessee, and Massachusetts
    # only report direct certification, not FRPL.
    todrop = df.index[df['LUNCH_PROGRAM'] != "No Category Codes"]
    df.drop(index=todrop, inplace=True)
    tokeep = ['NCESSCH' ,'year', 'STUDENT_COUNT']
    todrop = [i for i in df.columns if i not in tokeep]
    df.drop(columns=todrop, inplace=True)
    df = df.rename(columns={'STUDENT_COUNT': 'FRPL_Count'})
    df = pd.merge(df, dc, how='left', on ='NCESSCH')
    return df

##############################################################################
# Bring Data Together
##############################################################################

cl_dir = cleandirectory(df=df_dir, year= 2019)
cl_gen = cleanGender(df=df_mem.copy(), year= 2019)
cl_rac = cleanRace(df=df_mem.copy(), year= 2019)
cl_frl = cleanFRPL(df=df_lunch, year= 2019)
cl_stf = df_staff[['NCESSCH', 'TEACHERS']].copy()

cln_sch = pd.merge(cl_dir, cl_gen, on='NCESSCH', how='left')
cln_sch = pd.merge(cln_sch, cl_rac, on=['NCESSCH', 'year'], how='left')
cln_sch = pd.merge(cln_sch, cl_frl, on=['NCESSCH', 'year'], how='left')
cln_sch = pd.merge(cln_sch, cl_stf, on=['NCESSCH'], how='left')

cln_sch['stud_to_tch'] = cln_sch['School_Total_Enrollment'] / cln_sch['TEACHERS']
cln_sch.to_csv(r'..\..\..\Data\Clean Data\clean_common_core.csv')


# Explore Direct Certification vs FRPL 
# lunch["DATA_GROUP"].unique()

# view = lunch.groupby(['ST', 'DATA_GROUP'], as_index=False)['STUDENT_COUNT'].count()
# view = view.pivot(index='ST',
#                    columns='DATA_GROUP',
#                    values='STUDENT_COUNT')
# view['ratio'] = view['Free and Reduced-price Lunch Table']/view['Direct Certification']