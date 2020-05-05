# -*- coding: utf-8 -*-
"""
Created on Sun May  3 11:29:11 2020

@author: johan
"""
import pandas as pd
#import pandas_datareader.data as web

### OpenCovid ###
dfdata = pd.read_csv('New\data.csv')
dfmobility = pd.read_csv('New\mobility.csv')
dfweather = pd.read_csv('New\weather.csv')
dfresponse = pd.read_csv('New\Response.csv')


### Import Mappings ###
dfmap = pd.read_excel('Global Dataset.xlsx')
dfmapUK = pd.read_excel('Map UK.xlsx')

mapUKNutsNHS = {
'East Of England' : ['East of England'],
'London' : ['London'],
'Midlands' : ['West Midlands (England)','East Midlands (England)'],
'North East And Yorkshire' : ['North East (England)','Yorkshire and The Humber'],
'North West' : ['North West (England)'],
'South East' : ['South East (England)'],
'South West' : ['South West (England)']}

    #Get NUTS2 level for each NHS region
for x in mapUKNutsNHS:
    mapUKNutsNHS[x]=list(dfmapUK[dfmapUK['NUTS118NM'].isin(mapUKNutsNHS[x])]['NUTS218NM'].unique())

### Import Deaths ###
dfGermany = pd.read_excel("Deaths/Germany Cases.xlsx")
dfItaly = pd.read_excel("Deaths/Italy Cases.xlsx",sheet_name="Tabelle2")
dfBelgium = pd.read_excel("Deaths/Belgium Cases.xlsx")
dfFrance = pd.read_csv("Deaths/France Cases.csv")
dfSpain = pd.read_csv("Deaths/Spain Cases.csv")
dfSweden = pd.read_csv("Deaths/Sweden Cases.csv", sep=";")
dfUK = pd.read_excel("Deaths/UK Cases.xlsx",sheet_name="Data")
dfGlobal = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv")

dfHospitalBeds = pd.read_excel('Eurostat Data/Eurostat Hospital Beds.xlsx',sheet_name='Data')
dfGDP = pd.read_csv('Eurostat Data\Eurostat GDP/nama_10r_3gdp_1_Data.csv', encoding = "ISO-8859-1")
dfHouseholds = pd.read_csv('Eurostat Data/Eurostat Households/lfst_r_lfsd2hh_1_Data.csv', encoding = "ISO-8859-1")
dfPopulation = pd.read_csv('Eurostat Data/Eurostat Population/demo_r_pjangrp3_1_Data.csv', encoding = "ISO-8859-1")
dfPopulationDensity = pd.read_csv('Eurostat Data/Eurostat Density/demo_r_d3dens_1_Data.csv', encoding = "ISO-8859-1")

dfGlobalMobility = pd.read_csv('Global_Mobility_Report.csv')

#####Clean Data#####
#Germany#
    #Melt into right format    
dfGermany_final=dfGermany.melt(id_vars='Vortag')
    #Rename index
dfGermany_final.columns = ['date', 'region', 'deaths']
dfGermany_final = dfGermany_final.replace({'–':0})
dfGermany_final['country'] = 'Germany'

#Italy
    #Melt into right format
dfItaly_final=dfItaly.melt(id_vars='date')
    #Sum until this date
dfItaly_final['value']=dfItaly_final.groupby('variable').cumsum()
    #Rename
dfItaly_final.columns = ['date', 'region', 'deaths']
dfItaly_final['country']= 'Italy'

#France
    #Remove everything except regions and only OpenCovid (As they have all the deceased data)
dfFrance_final = dfFrance[dfFrance['granularite']=='region']
dfFrance_final = dfFrance_final[dfFrance_final['source_nom']=='OpenCOVID19-fr']
dfFrance_final = dfFrance_final[['date','maille_nom','deces']]
dfFrance_final.columns = ['date', 'region', 'deaths']
dfFrance_final['date'] = pd.to_datetime(dfFrance_final.date)
dfFrance_final['country']= 'France'

#Belgium
    #Sum all entries together for region and specific date
dfBelgium_final = dfBelgium.groupby(['DATE','REGION']).sum().reset_index()
dfBelgium_final['DEATHS'] = dfBelgium_final.groupby('REGION').cumsum()
dfBelgium_final.columns = ['date', 'region', 'deaths']
dfBelgium_final['country']= 'Belgium'

#Spain
    #Delete all unused columns, totals and rename
dfSpain_final = dfSpain[['fecha','CCAA','total']]
dfSpain_final = dfSpain_final[dfSpain_final['CCAA']!='Total']
dfSpain_final.columns = ['date', 'region', 'deaths']
dfSpain_final['date'] = pd.to_datetime(dfSpain_final.date)
dfSpain_final['country']= 'Spain'

#UK
    #Melt into right format
dfUK_final=dfUK.melt(id_vars='NHS England Region').dropna()
    #Sum until this date
dfUK_final['value']=dfUK_final.groupby('NHS England Region').cumsum()
    #Rename
dfUK_final.columns = ['region', 'date', 'deaths']
dfUK_final['country']= 'UK'

#Sweden
    #Drop not needed Columns
dfSweden_final = dfSweden.drop(['Region', 'Population', 'Lat','Long','Today', 'Region_Total', 'FHM_Today', 'Diff', 'Region_Deaths',
       'FHM_Deaths_Today', 'At_Hospital', 'At_ICU', 'Hospital_Total',
       'ICU_Capacity_2017', 'FHM_ICU_Est'], axis=1)
    #Drop last two rows that are cumulative
dfSweden_final = dfSweden_final[dfSweden_final['Display_Name'].notna()]
    #Melt into right format
dfSweden_final = dfSweden_final.melt(id_vars='Display_Name').fillna(0)
    #Sum until this date
dfSweden_final['value']=dfSweden_final.groupby('Display_Name').cumsum()
dfSweden_final['country']= 'Sweden'

#Portugal
    #Get data from Opencovid
dfPortugal_final = dfdata[dfdata['CountryName']=='Portugal'].dropna()
dfPortugal_final = dfPortugal_final[['Date','RegionName','Deaths','CountryName']]
dfPortugal_final.columns = ['date','region','deaths','country']
dfPortugal_final['date'] = pd.to_datetime(dfPortugal_final.date)

#Population Numbers
    #Problem with Points (633.383.938) as string -> not identified
dfPopulation_final = dfPopulation
dfPopulation_final['Value'] = pd.to_numeric((dfPopulation_final['Value'].str.replace('.','')).str.replace(':',''))
    #Delete male and female numbers
dfPopulation_final = dfPopulation_final[dfPopulation_final['SEX']=='Insgesamt']
    #Delete unnecessary columns and empty rows
dfPopulation_final = dfPopulation_final[['TIME','GEO','Value']].dropna()
    #Only Keep latest entry of every region
dfPopulation_final = dfPopulation_final.sort_values('TIME',ascending=False).drop_duplicates(subset=['GEO'])
dfPopulation_final.columns = ['Year_Population','region','Population']


#Population Density
    #Problem with Points (633.383,789) as string -> not identified
dfPopulationDensity_final = dfPopulationDensity
dfPopulationDensity_final['Value'] = pd.to_numeric(((dfPopulationDensity_final['Value'].str.replace('.','')).str.replace(',','.')).str.replace(':',''))
    #Delete unnecessary columns and empty rows
dfPopulationDensity_final = dfPopulationDensity_final[['TIME','GEO','Value']].dropna()
    #Only Keep latest entry of every region
dfPopulationDensity_final = dfPopulationDensity_final.sort_values('TIME',ascending=False).drop_duplicates(subset=['GEO'])
dfPopulationDensity_final.columns = ['Year_PopulationDensity','region','PopulationDensity']

#GDP
    #Problem with Points (633.383,789) as string -> not identified
dfGDP_final = dfGDP
dfGDP_final['Value'] = pd.to_numeric(((dfGDP_final['Value'].str.replace('.','')).str.replace(',','.')).str.replace(':',''))
    #Delete unnecessary columns and empty rows
dfGDP_final = dfGDP_final[['TIME','GEO','Value']].dropna()
    #Only Keep latest entry of every region
dfGDP_final = dfGDP_final.sort_values('TIME',ascending=False).drop_duplicates(subset=['GEO'])
dfGDP_final.columns = ['Year_GDP','region','GDP']

#Households
    #Problem with Points (633.383,789) as string -> not identified
dfHouseholds_final = dfHouseholds
dfHouseholds_final['Value'] = pd.to_numeric((dfHouseholds_final['Value'].str.replace(',','')).str.replace(':',''))
    #Delete unnecessary columns and empty rows
dfHouseholds_final = dfHouseholds_final[['TIME','GEO','Value']].dropna()
    #Only Keep latest entry of every region
dfHouseholds_final = dfHouseholds_final.sort_values('TIME',ascending=False).drop_duplicates(subset=['GEO'])
dfHouseholds_final.columns = ['Year_Households','region','Households']

#Hospital Beds





abc = np.unique(np.concatenate((dfmap['Name1'].fillna('n/a'), dfmap['Name2'].fillna('n/a'))))
dfdata_final = dfdata[dfdata['RegionName'].isin(abc)]

dfGDP[dfGDP['GEO'].isin(abc)]['GEO'].unique()