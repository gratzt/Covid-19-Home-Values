# Covid-19-Home-Values

## Introduction 
According to numerous media outlets substantial changes in the housing market were brought on by the  COVID-19 pandemic (1, 2, 3). And a vast body of research backs up these claims (4, 5, 6). In response to near zero interest rates home sale values rose sharpley. Not only did sales values increase, but the dynamics of COVID-19 induced changes fundamentally altered the housing market; COVID altered which homes in which markets and locations saw the biggest increases in sales value. 

Markets located further away from city centers saw the largest increases to home sales values (7, 8, 9, 10, 5). Liu and Su (2021) regress a variety of outcomes against pre-and post indicators for lockdowns and variables of interest. They find that relative to city centers, there is an increased demand for housing in suburban areas, less dense areas, and that these changes are likely driven by individuals able to telework. However, these models did not incorporate spatial autocorrelation. Lee and Huang (2022) follow up on these findings with a spatial autoregressive model and add nuance to the discussion. Areas located further from downtown saw higher online viewings of homes and increases in median sales prices, but did not see statistically significantly more sales. Not only do they confirm Liu and Su’s findings on sales price, but the magnitude of the spatial autoregressive model is markedly larger than a traditional ordinary least squares model.

However, many of the underlying mechanisms driving increases to sale value in these suburban and exurban locations have changed. The development and distribution of COVID-19 vaccines, in conjunction with advances in therapeutics have led to a decline in spread and the lethality of infections, which in turn have lessened the need for social distancing. While a substantial proportion of the workforce continues to work remotely, especially relative to pre-pandemic times, workplaces have begun calling workers back into the office. And, finally, the historically low interest rates observed during the heat of the pandemic are now the highest they have been in the past decade. Despite these shifting dynamics all work to date has estimated a single relationship between the urbanity and sales prices. In other words, we do not know the trajectory of the relationship between sales prices and urbanicity.

Given these recent changes, in this brief I update previous research examining the relationship between home-sale prices and the geographic locations relative to city centers. Specifically, I seek to answer two primary research questions: 1) what is the temporal nature of the relationship between urbanicity and housing prices, and 2) how have these relationships changed in the past 12 months, a period of time hitherto unstudied.

Using a metric that incorporates commute times, I find that home-prices in suburban, town, and rural locations relative to urban areas did increase in response to the pandemic. Moreover, the relative gains in home-sale prices are, in the near-term at least, sticky. Home-sales climbed in these non-urban settings during the period of time between lockdowns and stabilized remarkably quickly after Federal Funds rates began to rise. 

## Data

Data was collected from three different organizations: the U.S. Census Bureau, the U.S. Department of Agriculture (USDA), and Zillow. Features shown to be associated with home-prices were retrieved from the Census Bureau’s 2019 American Communities Survey (ACS) 5-year estimates API at the zip code tabulation area. The 2019 ACS data were used because they constitute the last full year of data prior to COVID-19. Because this research examines which types of neighborhoods experienced differential trajectories during COVID-19, I used the last full year prior to COVID because it is likely that COVID-19 may change the composition of neighborhoods.

The USDA Rural-Urban Commuting Area data include ordinal categorical indicators for urbanity based on the 2010 census. Zip codes are classified into categories 1-10 based on their population density, urbanization, and commute times. Categories 1-3 are considered urban, 4-6 suburban, 7-9 towns, and 10 are rural. For home sale prices, I used the monthly Zillow Home Value Index (ZHVI)  from January 2017 through February 2023. All data were collected at the zip code tabulation area and were able to be directly merged to the 2019 TIGER/Lines shapefiles for zip codes.

## Methods

Modeling the relationship between housing prices and features is challenging because neighborhoods in close proximity often influence the housing prices of each other (11). To address autocorrelation, this relationship is modeled using a spatial autoregressive model depicted below in Equation 1:

Equation 1:

$$ ln(y_t) = \rho W y_t + X \beta + \epsilon_t $$

In Equation 1 $ln(y_t)$ is a vector of the natural log transformed ZHVI in month t. $\rho$ is the spatial autoregressive coefficient which captures the extent to which the ZHVI of a zip code’s neighbors influence the price in the given zip code (7), and W is the spatial weights matrix. The spatial weights matrix was constructed using a five nearest neighbors approach with row standardization. The five nearest neighbors for the spatial weights was chosen because the median zip code has five queen contiguity neighbors. X is a covariate matrix of features from 2019 i.e. the last year prior to COVID-19. The features in X include a set of neighborhood characteristics: urbanicity, race/ethnicity, median income, percent of the population above 25, percent of the population with a bachelor’s degree or above, the percent of the population with a broadband connection, as well as a set of housing characteristics including the median number of rooms, the composition of housing units by the number of bedrooms, and the age composition of housing units. Equation one is estimated using a two-staged spatial lag model and is estimated for each month between January 2017 and February 2023 (12). 

## Results and Conclusions

Figure 1 below depicts the coefficients from Equation 1 for suburban, town, and rural zip code indicators with the base category being urban zip codes from regressions run on every month of the series. Since the ZHVI has been log transformed, coefficients should be interpreted as percent changes in the ZHVI of the variable of interest relative to the base category, urban zip codes. The two vertical lines indicate the last month prior to pandemic lockdowns, February 2020, and the last month prior to Federal Fund rate hikes, February 2022.
	
All categories, suburban, towns, and rural zip codes, have ZHVI that are at a minimum 3% less in value that urban zip codes, all else equal. At the same time all categories were appreciating ZHVI gains prior to the pandemic relative to urban zip codes. However, consistent with prior literature, after the start of lockdowns and by the beginning of 2021 or earlier there exists a rapid increase in ZHVI for all three categories. For example, the ZHVI for suburban zip codes was 4.3% lower than urban zip codes at the start of the pandemic (February, 2020), but only 2.9% lower on the eve of Federal Fund rate increases. However, after the Federal Funds rate was raised in March of 2022 the steep ascent of suburban, town, and rural zip codes’ ZHVI relative to urban zip codes plateaus. The relative gains made by these categories remain remarkably stable throughout the rest of the year. 

### Figure 1: Percent Change in the Zillow Home Value Index By Urbanicity

![alt text](https://github.com/gratzt/Covid-19-Home-Values/blob/main/LogsOutput/CoefPlots/UrbanicityCoefficients.png)


These results clearly confirm prior findings of the relationship between the changes to home-prices based on urbanicity. They also help pinpoint when in the pandemic prices started to change, XX for rural locations and YY for town and suburban locations. 

More importantly, they extend the analysis to a period of time after which many of the hypothesized drivers of these increases had changed. By February 2022 weekly mortality from COVID-19 had dropped from a peak of 23,629 in January of 2021 to 3,480 in the first week of February 2023, potentially lessening the desire to social distance in less dense and more geographically remote areas. At the same time, historically low interest rates were rising in response to inflation. The share of people working from home has declined from a high of 69% in May of 2020 to 45% in September of 2021 (13), and is likely lower today. Despite these changes the relative gains in home prices suburban, town, and rural locations made when compared to urban locations persist. To be clear, their steep ascent has plateaued, but there has not been a market correction to bring them back in line with their pre-pandemic levels. In the medium to near-term it appears that the gains made during the pandemic will stay.  

If increased sales values reflect an increased and potentially persistent demand for housing located further from city centers paired with an elastic supply of housing, then this finding has broad implications for urban planners. It could indicate future population shifts from city centers to suburban and exurban locations. Residents may expect the services typically afforded to them by living in a dense urban setting in areas that may be less able or have less experience providing them. At the same time, there may be less demand for these same services in urban settings. Future work is needed to determine the extent to which increased sales-values translate into increased populations living and working in these non-urban settings, and for untangling the implications of this shift for urban planners.

## References

1.   Beier, Hannah. “In Covid-19 Housing Market, the Middle Class Is Getting Priced Out.” The Wall Street Journal, Dow Jones & Company, 22 Feb. 2022, https://www.wsj.com/articles/in-covid-19-housing-market-the-middle-class-is-getting-priced-out-11644246000. 
3.  Kirby, Jen. “America's Looming Housing Catastrophe, Explained.” Vox, Vox, 8 July 2020, https://www.vox.com/21301823/rent-coronavirus-covid-19-housing-eviction-crisis. 
4.  Olick, Diana. “Mortgage Rates Set New Record Low, Falling below 3% as Concerns Rise about Coronavirus Second Wave.” CNBC, CNBC, 13 June 2020, https://www.cnbc.com/2020/06/11/mortgage-rates-set-new-record-low-fall-below-3percent-on-coronavirus-fears.html. 
5.  Beracha, Eli, et al. "On the Relation between Innovation and Housing Prices–A Metro Level Analysis of the US Market." The Journal of Real Estate Finance and Economics (2022): 1-27.
6.  Ramani, Arjun, and Nicholas Bloom. The Donut effect of COVID-19 on cities. No. w28876. National Bureau of Economic Research, 2021.
7.  Zhao, Yunhui. "US housing market during COVID-19: aggregate and distributional evidence." (2020).
8.  Gupta, Arpit, et al. "Flattening the curve: pandemic-induced revaluation of urban real estate." Journal of Financial Economics 146.2 (2022): 594-636.
9.  Lee, Jim, and Yuxia Huang. "Covid-19 impact on US housing markets: evidence from spatial regression models." Spatial Economic Analysis 17.3 (2022): 395-415.
10.  D'Lima, Walter, Luis Arturo Lopez, and Archana Pradhan. "COVID‐19 and housing market effects: Evidence from US shutdown orders." Real Estate Economics 50.2 (2022): 303-339.
11.  Liu, Sitian, and Yichen Su. "The impact of the COVID-19 pandemic on the demand for density: Evidence from the US housing market." Economics letters 207 (2021): 110010.
12. Brady M, Irwin E. Accounting for spatial effects in economic models of land use: recent developments and challenges ahead. Environmental and Resource Economics. 2011 Mar;48:487-509.
13. Anselin L. Spatial econometrics: methods and models. Springer Science & Business Media; 1988 Aug 
14. Saad , L., & Wigert, B. (2022, November 29). Remote work persisting and trending permanent. Gallup.com. https://news.gallup.com/poll/355907/remote-work-persisting-trending-permanent.aspx 


