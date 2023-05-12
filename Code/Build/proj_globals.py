# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 07:37:17 2023

"""

 
# See the variable definitions at the following URL   
# https://api.census.gov/data/2019/acs/acs5/profile/variables.html

acs5_2019_dict = {
                # Social Characteristics
                    # Normalize by total population or households 
                'DP02_0059E': 'Pop25_plus',
                'DP02_0064E': 'Pop25_plus_with_associates',
                'DP02_0065E': 'Pop25_plus_with_bachelors',
                'DP02_0066E': 'Pop25_plus_with_gradprof',
                'DP02_0067E': 'Pop25_plus_with_hsdiplo',
                'DP02_0088E': 'Native_birth', 
                'DP02_0094E': 'Foreign_birth',
                'DP02_0152E': 'With_a_computer',
                'DP02_0153E': 'With_broadband',

                # Economic Characteristics
                    # Normalize by population 16 plus or 16 plus and in labor
                    # force
                'DP03_0001E': 'Pop_16plus',
                'DP03_0002E': 'Pop_in_LaborForce',
                'DP03_0033E': 'industry_agri',
                'DP03_0034E': 'industry_construction',
                'DP03_0035E': 'industry_manufacturing',
                'DP03_0036E': 'industry_wholesaletrade',
                'DP03_0037E': 'industry_retailtrade',
                'DP03_0038E': 'industry_transportation_warehousing',
                'DP03_0039E': 'industry_informaiton',
                'DP03_0040E': 'industry_finance_insurance_realestate',
                'DP03_0041E': 'industry_professional_scientific',
                'DP03_0042E': 'industry_education_healthcare',
                'DP03_0043E': 'industry_arts_entertainment',
                'DP03_0044E': 'industry_other_services',
                'DP03_0045E': 'industry_public_admin',
                'DP03_0052E': 'HouseholdIncome_10kless',
                'DP03_0053E': 'HouseholdIncome_10k_15k',
                'DP03_0054E': 'HouseholdIncome_15k_25k',
                'DP03_0055E': 'HouseholdIncome_25k_35k',
                'DP03_0056E': 'HouseholdIncome_35k_50k',
                'DP03_0057E': 'HouseholdIncome_50k_75k',
                'DP03_0058E': 'HouseholdIncome_75k_100k',
                'DP03_0059E': 'HouseholdIncome_100k_150k',
                'DP03_0060E': 'HouseholdIncome_150k_200k',
                'DP03_0061E': 'HouseholdIncome_200kplus',
                'DP03_0062E': 'MedianHouseholdIncome',
                'DP03_0063E': 'MeanHouseholdIncome',

                # Housing Characteristics
                    # Normalize by total housing units or toal occupied
                    # housing units
                'DP04_0001E': 'total_housing_units', 
                'DP04_0002E': 'total_occupied_housing_units',
                'DP04_0005E': 'RentalVacancyRate',
                'DP04_0007E': 'one_unit_detached',
                'DP04_0008E': 'one_unit_attached',
                'DP04_0009E': 'two_units',
                'DP04_0010E': 'threeFour_units',
                'DP04_0011E': 'fiveNine_units',
                'DP04_0012E': 'tenNinteen_units',
                'DP04_0013E': 'twentyplus_units',
                'DP04_0014E': 'mobilehome_units',
                'DP04_0015E': 'boatrvvan',
                'DP04_0017E': 'yr_built_2014plus',
                'DP04_0018E': 'yr_built_2010_2013',
                'DP04_0019E': 'yr_built_2000_2009',
                'DP04_0020E': 'yr_built_1990_1999',
                'DP04_0021E': 'yr_built_1980_1989',
                'DP04_0022E': 'yr_built_1970_1979',
                'DP04_0023E': 'yr_built_1960_1969',
                'DP04_0024E': 'yr_built_1950_1959',
                'DP04_0025E': 'yr_built_1940_1949',
                'DP04_0026E': 'yr_built_1939earlier',
                'DP04_0028E': 'units_1_room',
                'DP04_0029E': 'units_2_room',
                'DP04_0030E': 'units_3_room',
                'DP04_0031E': 'units_4_room',
                'DP04_0032E': 'units_5_room',
                'DP04_0033E': 'units_6_room',
                'DP04_0034E': 'units_7_room',
                'DP04_0035E': 'units_8_room',
                'DP04_0036E': 'units_9plus_room',
                'DP04_0037E': 'units_median_room',
                'DP04_0039E': 'units_none_bedroom',
                'DP04_0040E': 'units_1_bedroom',
                'DP04_0041E': 'units_2_bedroom',
                'DP04_0042E': 'units_3_bedroom',
                'DP04_0043E': 'units_4_bedroom',
                'DP04_0044E': 'units_5plus_bedroom',
                'DP04_0046E': 'owner_occupied',
                'DP04_0047E': 'renter_occupied',
                'DP04_0051E': 'moved_in_2017plus',
                'DP04_0052E': 'moved_in_2015_2016',
                'DP04_0053E': 'moved_in_2010_2014',
                'DP04_0054E': 'moved_in_2000_2009',
                'DP04_0055E': 'moved_in_1990_1999',
                'DP04_0056E': 'moved_in_1989earlier',
                'DP04_0063E': 'heating_gas',
                'DP04_0064E': 'heating_bottletanklpgas',
                'DP04_0065E': 'heating_electricity',
                'DP04_0066E': 'heating_fueloil',
                'DP04_0067E': 'heating_coal',
                'DP04_0068E': 'heating_wood',
                'DP04_0069E': 'heating_solar',
                'DP04_0070E': 'heating_other',
                'DP04_0071E': 'heating_nofuel',
                'DP04_0073E': 'lacking_complete_plumbing',
                'DP04_0074E': 'lacking_complete_kitchen',
                'DP04_0075E': 'no_telephone_service_available',
                'DP04_0081E': 'homevalue_50kless',
                'DP04_0082E': 'homevalue_50k_100k',
                'DP04_0083E': 'homevalue_100k_150k',
                'DP04_0084E': 'homevalue_150k_200k',
                'DP04_0085E': 'homevalue_200k_300k',
                'DP04_0086E': 'homevalue_300k_500k',
                'DP04_0087E': 'homevalue_500k_1000k',
                'DP04_0088E': 'homevalue_1000kplus',
                'DP04_0089E': 'homevalue_median',
                'DP04_0114E': 'ownerhousingcost_30_35per_income', # 30% plus is considered cost burdened by housing
                'DP04_0115E': 'ownerhousingcost_35plusper_income',  # 30% plus is considered cost burdened by housing
                'DP04_0123E': 'nomort_ownerhousingcost_30_35per_income',
                'DP04_0124E': 'nomort_ownerhousingcost_35plusper_income',
                'DP04_0141E': 'renthousingcost_30_35per_income', 
                'DP04_0142E': 'renthousingcost_35plusper_income',
                # Demograpnic Characteristics
                    # Normalize by total pop
                'DP05_0001E': 'TotalPop',
                'DP05_0008E': 'Pop_15_19',
                'DP05_0009E': 'Pop_20_24',
                'DP05_0019E': 'Pop_under18',
                'DP05_0024E': 'Pop_65plus',
                'DP05_0071E': 'Pop_Hispanic',
                'DP05_0077E': 'Pop_White',
                'DP05_0078E': 'Pop_Black',
                'DP05_0079E': 'Pop_AIAN', # American Indian Alaskan Native
                'DP05_0080E': 'Pop_Asian',
                'DP05_0081E': 'Pop_NHPI', # Native Hawaiian or other Pac Islander
                'DP05_0082E': 'Pop_OtherRace',
                'DP05_0083E': 'Pop_TwoPlusRace',

                    }
