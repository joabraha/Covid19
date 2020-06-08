"""
Created on Sun May  3 11:29:11 2020

@author: johan
"""
from statsmodels.formula.api import ols
import pandas as pd
import numpy as np
from linearmodels import PanelOLS

# import pandas_datareader.data as web
import plotly.express as px
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output

### UK specific function ###
def UKaggregate(mapping, df, sumavg, datapoint, date):
    listval = []
    for x in mapping:
        if sumavg == "sum":
            listval.append(df[df["regionNUTS"].isin(mapping[x])][datapoint].sum())
        else:
            listval.append(df[df["regionNUTS"].isin(mapping[x])][datapoint].mean())
    listmapping = list(mapping)
    dfreturn = {
        "regionNUTS": listmapping,
        "Year_" + datapoint: [date] * 7,
        datapoint: listval,
    }
    return pd.DataFrame(dfreturn)


def GoogMobaggregate(mapping, df, country, countrycode):
    df["region_aggregate"] = np.nan
    for x in mapping:
        df.loc[df["sub_region_1"].isin(mapping[x]), "region_aggregate"] = x
    dfaverages = df.groupby(["date", "region_aggregate"]).agg(
        {
            "retail_and_recreation_percent_change_from_baseline": "mean",
            "grocery_and_pharmacy_percent_change_from_baseline": "mean",
            "parks_percent_change_from_baseline": "mean",
            "transit_stations_percent_change_from_baseline": "mean",
            "workplaces_percent_change_from_baseline": "mean",
            "residential_percent_change_from_baseline": "mean",
        }
    )
    dfaverages = dfaverages.reset_index()
    dfaverages.rename(columns={"region_aggregate": "sub_region_1"}, inplace=True)
    dfaverages["country_region_code"] = countrycode
    dfaverages["country_region"] = country
    dfaverages["sub_region_2"] = np.nan
    return dfaverages


### OpenCovid ###
dfdata = pd.read_csv("Deaths\OpenCovid Data.csv")
# dfmobility = pd.read_csv('New\mobility.csv')
# dfweather = pd.read_csv('New\weather.csv')
# dfresponse = pd.read_csv('New\Response.csv')


### Import Mappings ###
dfmap = pd.read_excel("Global Dataset.xlsx", encoding="ISO-8859-1")
dfmapUK = pd.read_excel("Map UK.xlsx")

mapUKNutsNHS = {
    "East Of England": ["East of England"],
    "London": ["London"],
    "Midlands": ["West Midlands (England)", "East Midlands (England)"],
    "North East And Yorkshire": ["North East (England)", "Yorkshire and The Humber"],
    "North West (UK)": ["North West (England)"],
    "South East": ["South East (England)"],
    "South West": ["South West (England)"],
}

# Get NUTS2 level for each NHS region
for x in mapUKNutsNHS:
    mapUKNutsNHS[x] = list(
        dfmapUK[dfmapUK["NUTS118NM"].isin(mapUKNutsNHS[x])]["NUTS218NM"].unique()
    )

mapPortugalDistrRegion = {
    "Norte": [
        "Aveiro District",
        "Braga",
        "Bragança District",
        "Porto District",
        "Viana do Castelo District",
        "Vila Real District",
    ],
    "Alentejo": ["Beja District", "Évora District", "Portalegre District", "Setubal"],
    "Centro": [
        "Castelo Branco District",
        "Coimbra District",
        "Guarda District",
        "Leiria District",
        "Santarém District",
        "Viseu District",
    ],
    "Lisbon": ["Lisbon"],
    "Algarve": ["Faro District"],
}


# Source: https://www.covid-19.no/critical-care-bed-numbers-in-europe
dfCriticalCareBeds = pd.DataFrame(
    {
        "Country": [
            "Germany",
            "Luxemburg",
            "Austria",
            "Belgium",
            "Italy",
            "France",
            "Spain",
            "Norway",
            "Denmark",
            "UK",
            "Netherlands",
            "Finland",
            "Sweden",
            "Portugal",
            "Poland",
        ],
        "CriticalCareBeds": [
            29.2,
            24.8,
            21.8,
            15.9,
            12.5,
            11.6,
            9.7,
            8.0,
            6.7,
            6.6,
            6.4,
            6.1,
            5.8,
            4.2,
            6.9,
        ],
    }
)

### Import Deaths ###
dfGermany = pd.read_excel("Deaths/Germany Cases.xlsx")
dfItaly = pd.read_excel("Deaths/Italy Cases.xlsx", sheet_name="Tabelle2")
dfBelgium = pd.read_excel("Deaths/Belgium Cases.xlsx")
dfFrance = pd.read_csv("Deaths/France Cases.csv")
dfSpain = pd.read_csv("Deaths/Spain Cases.csv")
dfSweden = pd.read_csv("Deaths/Sweden Cases.csv", sep=",")
dfUK = pd.read_excel("Deaths/UK Cases.xlsx", sheet_name="Data")
dfGlobal = pd.read_csv(
    "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"
)

dfHospitalBeds = pd.read_excel(
    "Eurostat Data/Eurostat Hospital Beds.xlsx", sheet_name="Data"
)
dfGDP = pd.read_csv(
    "Eurostat Data\Eurostat GDP/nama_10r_2gdp_1_Data.csv", encoding="ISO-8859-1"
)
dfHouseholds = pd.read_csv(
    "Eurostat Data/Eurostat Households/lfst_r_lfsd2hh_1_Data.csv", encoding="ISO-8859-1"
)
dfPopulation = pd.read_csv(
    "Eurostat Data/Eurostat Population/demo_r_pjangrp3_1_Data.csv",
    encoding="ISO-8859-1",
)
dfPopulationDensity = pd.read_csv(
    "Eurostat Data/Eurostat Density/demo_r_d3dens_1_Data.csv", encoding="ISO-8859-1"
)

dfGlobalMobility = pd.read_csv("Global_Mobility_Report.csv")
### Get Global Mobility Data in right format ###
# If no region -> Take country as region and rename
dfGlobalMobility.loc[
    dfGlobalMobility["sub_region_1"].isna(), "sub_region_1"
] = dfGlobalMobility.loc[dfGlobalMobility["sub_region_1"].isna(), "country_region"]

dfPortGMagg = GoogMobaggregate(
    mapPortugalDistrRegion, dfGlobalMobility, "Portugal", "PT"
)
dfUKGMagg = GoogMobaggregate(mapUKNutsNHS, dfGlobalMobility, "United Kingdom", "GB")

dfGlobalMobility = pd.concat([dfGlobalMobility, dfPortGMagg, dfUKGMagg])
dfGlobalMobility["date"] = pd.to_datetime(dfGlobalMobility.date)
dfGlobalMobility.rename(columns={"sub_region_1": "regionGoogleMob"}, inplace=True)


#####Clean Data#####
# Germany#
# Melt into right format
dfGermany_final = dfGermany.melt(id_vars="Vortag")
# Rename index
dfGermany_final.columns = ["date", "region", "deaths"]
dfGermany_final = dfGermany_final.replace({"–": 0})

# Italy
# Melt into right format
dfItaly_final = dfItaly.melt(id_vars="date")
# Sum until this date
dfItaly_final["value"] = dfItaly_final.groupby("variable").cumsum()
# Rename
dfItaly_final.columns = ["date", "region", "deaths"]

# France
# Remove everything except regions and only OpenCovid (As they have all the deceased data)
dfFrance_final = dfFrance[dfFrance["granularite"] == "region"]
dfFrance_final = dfFrance_final[dfFrance_final["source_nom"] == "OpenCOVID19-fr"]
dfFrance_final = dfFrance_final[["date", "maille_nom", "deces"]]
dfFrance_final.columns = ["date", "region", "deaths"]
dfFrance_final["date"] = pd.to_datetime(dfFrance_final.date)

# Belgium
# Sum all entries together for region and specific date
dfBelgium_final = dfBelgium.groupby(["DATE", "REGION"]).sum().reset_index()
dfBelgium_final["DEATHS"] = dfBelgium_final.groupby("REGION").cumsum()
dfBelgium_final.columns = ["date", "region", "deaths"]

# Spain
# Delete all unused columns, totals and rename
dfSpain_final = dfSpain[["fecha", "CCAA", "total"]]
dfSpain_final = dfSpain_final[dfSpain_final["CCAA"] != "Total"]
dfSpain_final.columns = ["date", "region", "deaths"]
dfSpain_final["date"] = pd.to_datetime(dfSpain_final.date)

# UK
# Melt into right format
dfUK_final = dfUK.melt(id_vars="NHS England Region").dropna()
dfUK_final["NHS England Region"] = dfUK_final["NHS England Region"].str.replace(
    "North West", "North West (UK)"
)
# Sum until this date
dfUK_final["value"] = dfUK_final.groupby("NHS England Region").cumsum()
# Rename
dfUK_final.columns = ["region", "date", "deaths"]

# Sweden
# Drop not needed Columns
dfSweden_final = dfSweden.drop(
    [
        "Region",
        "Population",
        "Lat",
        "Long",
        "Today",
        "Diff",
        "Region_Deaths",
        "FHM_Deaths_Today",
    ],
    axis=1,
)
# Drop last two rows that are cumulative
dfSweden_final = dfSweden_final[dfSweden_final["Display_Name"].notna()]
# Melt into right format
dfSweden_final = dfSweden_final.melt(id_vars="Display_Name").fillna(0)
# Sum until this date
dfSweden_final["value"] = dfSweden_final.groupby("Display_Name").cumsum()
dfSweden_final.columns = ["region", "date", "deaths"]
dfSweden_final["date"] = pd.to_datetime(dfSweden_final.date)

# Portugal
# Get data from Opencovid
dfPortugal_final = dfdata[dfdata["CountryName"] == "Portugal"].dropna()
dfPortugal_final = dfPortugal_final[["Date", "RegionName", "Deaths"]]
dfPortugal_final.columns = ["date", "region", "deaths"]
dfPortugal_final["date"] = pd.to_datetime(dfPortugal_final.date)

# Get full country data (no regional data avlbl or useful)
listcountries = [
    "Austria",
    "Luxemburg",
    "Norway",
    "Poland",
    "Denmark",
    "Netherlands",
    "Finland",
]
dfdata_country = dfdata[
    dfdata["CountryName"].isin(listcountries) & dfdata["RegionName"].isna()
]
dfdata_country = dfdata_country[["Date", "CountryName", "Deaths"]]
dfdata_country.columns = ["date", "region", "deaths"]
dfdata_country["date"] = pd.to_datetime(dfdata_country.date)


### EUROSTAT DATA ###
# Population Numbers
# Problem with Points (633.383.938) as string -> not identified
dfPopulation_final = dfPopulation
dfPopulation_final["Value"] = pd.to_numeric(
    (dfPopulation_final["Value"].str.replace(",", "")).str.replace(":", "")
)
# Delete male and female numbers
dfPopulation_final = dfPopulation_final[dfPopulation_final["SEX"] == "Total"]
# Delete unnecessary columns and empty rows
dfPopulation_final = dfPopulation_final[["TIME", "GEO", "Value"]].dropna()
# Only Keep latest entry of every region
dfPopulation_final = dfPopulation_final.sort_values("TIME", ascending=False)
dfPopulation_final.columns = ["Year_Population", "regionNUTS", "Population"]
# UK Specific aggregation
dfPopulation_final = pd.concat(
    [
        UKaggregate(mapUKNutsNHS, dfPopulation_final, "sum", "Population", 2019),
        dfPopulation_final,
    ]
).drop_duplicates(subset=["regionNUTS"], keep="first")


# Population Density
# Problem with Points (633.383,789) as string -> not identified
dfPopulationDensity_final = dfPopulationDensity
dfPopulationDensity_final["Value"] = pd.to_numeric(
    (dfPopulationDensity_final["Value"].str.replace(",", "")).str.replace(":", "")
)
# Delete unnecessary columns and empty rows
dfPopulationDensity_final = dfPopulationDensity_final[["TIME", "GEO", "Value"]].dropna()
# Only Keep latest entry of every region
dfPopulationDensity_final = dfPopulationDensity_final.sort_values(
    "TIME", ascending=False
)
dfPopulationDensity_final.columns = [
    "Year_PopulationDensity",
    "regionNUTS",
    "PopulationDensity",
]
# UK Specific aggregation
dfPopulationDensity_final = pd.concat(
    [
        UKaggregate(
            mapUKNutsNHS, dfPopulationDensity_final, "avg", "PopulationDensity", 2018
        ),
        dfPopulationDensity_final,
    ]
).drop_duplicates(subset=["regionNUTS"], keep="first")


# GDP
# Problem with Points (633.383,789) as string -> not identified
dfGDP_final = dfGDP
dfGDP_final["Value"] = pd.to_numeric(
    (dfGDP_final["Value"].str.replace(",", "")).str.replace(":", "")
)
# Delete unnecessary columns and empty rows
dfGDP_final = dfGDP_final[["TIME", "GEO", "Value"]].dropna()
# Only Keep latest entry of every region
dfGDP_final = dfGDP_final.sort_values("TIME", ascending=False)
dfGDP_final.columns = ["Year_GDP", "regionNUTS", "GDP"]
# UK and Sweden Specific data and aggregation
# Import Swedish Data
# Source: http://www.statistikdatabasen.scb.se/pxweb/en/ssd/START__NR__NR0105__NR0105A/NR0105ENS2010T01A/table/tableViewLayout1/
dfGDP_Sweden = pd.read_excel("Eurostat Data\Eurostat GDP/GDP_Sweden.xlsx")
dfGDP_final = pd.concat(
    [
        dfGDP_Sweden,
        UKaggregate(mapUKNutsNHS, dfGDP_final, "sum", "GDP", 2018),
        dfGDP_final,
    ]
).drop_duplicates(subset=["regionNUTS"], keep="first")

# Households
# Problem with Points (633.383,789) as string -> not identified
dfHouseholds_final = dfHouseholds
dfHouseholds_final["Value"] = pd.to_numeric(
    (dfHouseholds_final["Value"].str.replace(",", "")).str.replace(":", "")
)
# Delete unnecessary columns and empty rows
dfHouseholds_final = dfHouseholds_final[["TIME", "GEO", "Value"]].dropna()
# Only Keep latest entry of every region
dfHouseholds_final = dfHouseholds_final.sort_values("TIME", ascending=False)
dfHouseholds_final.columns = ["Year_Households", "regionNUTS", "Households"]
# UK and Sweden- Specific additions
# Add swedish data (not in Eurostats dataset):
# Source: http://www.statistikdatabasen.scb.se/pxweb/en/ssd/START__BE__BE0101__BE0101S/HushallT05/table/tableViewLayout1/
dfHouseholds_Sweden = pd.read_excel(
    "Eurostat Data/Eurostat Households/Households_Sweden.xlsx"
)
dfHouseholds_Sweden.Households = dfHouseholds_Sweden.Households / 1000
# Put everything toghether
dfHouseholds_final = pd.concat(
    [
        dfHouseholds_Sweden,
        UKaggregate(mapUKNutsNHS, dfHouseholds_final, "sum", "Households", 2019),
        dfHouseholds_final,
    ]
).drop_duplicates(subset=["regionNUTS"], keep="first")


# Hospital Beds
dfHospitalBeds_final = dfHospitalBeds.melt(id_vars="TIME")
dfHospitalBeds_final.columns = ["GEO", "TIME", "Value"]
dfHospitalBeds_final["Value"] = pd.to_numeric(
    dfHospitalBeds_final["Value"], errors="coerce"
)
# Delete unnecessary columns and empty rows
dfHospitalBeds_final = dfHospitalBeds_final[["TIME", "GEO", "Value"]].dropna()
# Only Keep latest entry of every region
dfHospitalBeds_final = dfHospitalBeds_final.sort_values(
    "TIME", ascending=False
).drop_duplicates(subset=["GEO"])
dfHospitalBeds_final.columns = ["Year_HospitalBeds", "regionNUTS", "HospitalBeds"]
# UK Specific additions not necessary, as none avlbl
# dfHospitalBeds_final = pd.concat([dfHospitalBeds_final , UKaggregate(mapUKNutsNHS,dfHospitalBeds_final,'sum','HospitalBeds',2019)])

### Create final Death dataframe ###
ListCountrydf = [
    dfBelgium_final,
    dfItaly_final,
    dfSpain_final,
    dfGermany_final,
    dfUK_final,
    dfFrance_final,
    dfSweden_final,
    dfPortugal_final,
    dfdata_country,
]
dfDeathdata = pd.concat(ListCountrydf)

# Get NUTS region to merge with Eurostat data

dfDeathdata = pd.merge(dfDeathdata, dfmap, how="left", on="region")
dfDeathdata = pd.merge(dfDeathdata, dfPopulation_final, how="left", on="regionNUTS")
dfDeathdata = pd.merge(dfDeathdata, dfHouseholds_final, how="left", on="regionNUTS")
dfDeathdata = pd.merge(
    dfDeathdata, dfPopulationDensity_final, how="left", on="regionNUTS"
)
dfDeathdata = pd.merge(dfDeathdata, dfHospitalBeds_final, how="left", on="regionNUTS")
dfDeathdata = pd.merge(dfDeathdata, dfGDP_final, how="left", on="regionNUTS")
dfDeathdata = pd.merge(dfDeathdata, dfCriticalCareBeds, how="left", on="Country")

dfDeathdata.set_index(["regionGoogleMob", "date"], inplace=True)
dfGlobalMobility.set_index(["regionGoogleMob", "date"], inplace=True)

dfDeathdata = pd.merge(
    dfDeathdata, dfGlobalMobility, how="left", left_index=True, right_index=True
)

dfDeathdata["deathsper1m"] = dfDeathdata["deaths"] / dfDeathdata["Population"] * 1000000
dfDeathdata["chgdeathsper1m"] = dfDeathdata["deathsper1m"].diff()

dfDeathdata["GDPpercapita"] = dfDeathdata["GDP"] / dfDeathdata["Population"] * 1000

dfDeathdata["personsperhousehold"] = (
    dfDeathdata["Population"] / dfDeathdata["Households"] / 1000
)

# Shift Deths by 24 days
# 19days median days from illness onset until death: (https://www.thelancet.com/action/showPdf?pii=S0140-6736%2820%2930566-3)
# 5 days median incubation time: https://www.acpjournals.org/doi/10.7326/M20-0504
dfDeathdata["chgdeathsper1m_shifted"] = dfDeathdata.groupby("region")[
    "chgdeathsper1m"
].shift(-24)

dfDeathdata["deathsper1m_shifted"] = dfDeathdata.groupby("region")["deathsper1m"].shift(
    -24
)
# 3day moving average
dfint = dfDeathdata.groupby("region").rolling(window=3).mean()

# Get correct index -> From Google mob to region
dfint.reset_index(inplace=True)
dfint.set_index(["region", "date"], inplace=True)
dfDeathdata.reset_index(inplace=True)
dfDeathdata.set_index(["region", "date"], inplace=True)

dfDeathdata["chgdeathsper1m_shifted3dma"] = dfint["chgdeathsper1m_shifted"]
dfDeathdata["retail_and_recreation_percent_change_from_baseline3dma"] = dfint[
    "retail_and_recreation_percent_change_from_baseline"
]
dfDeathdata["grocery_and_pharmacy_percent_change_from_baseline3dma"] = dfint[
    "grocery_and_pharmacy_percent_change_from_baseline"
]
dfDeathdata["parks_percent_change_from_baseline3dma"] = dfint[
    "parks_percent_change_from_baseline"
]
dfDeathdata["transit_stations_percent_change_from_baseline3dma"] = dfint[
    "transit_stations_percent_change_from_baseline"
]
dfDeathdata["workplaces_percent_change_from_baseline3dma"] = dfint[
    "workplaces_percent_change_from_baseline"
]
dfDeathdata["residential_percent_change_from_baseline3dma"] = dfint[
    "residential_percent_change_from_baseline"
]

dfDeathdata["intDeathsandretail_and_recreation_percent_change_from_baseline3dma"] = (
    dfDeathdata["retail_and_recreation_percent_change_from_baseline3dma"]
    * dfDeathdata["deathsper1m_shifted"]
)
dfDeathdata["intDeathsandtransit_stations_percent_change_from_baseline3dma"] = (
    dfDeathdata["transit_stations_percent_change_from_baseline3dma"]
    * dfDeathdata["deathsper1m_shifted"]
)
dfDeathdata["intDeathsandworkplaces_percent_change_from_baseline3dma"] = (
    dfDeathdata["workplaces_percent_change_from_baseline3dma"]
    * dfDeathdata["deathsper1m_shifted"]
)


### Fixed Effects regression ###
mod = PanelOLS.from_formula(
    "chgdeathsper1m_shifted3dma ~ CriticalCareBeds + GDPpercapita + personsperhousehold + PopulationDensity + retail_and_recreation_percent_change_from_baseline3dma + transit_stations_percent_change_from_baseline3dma + workplaces_percent_change_from_baseline3dma",
    data=dfDeathdata[dfDeathdata["chgdeathsper1m_shifted3dma"].between(1, 100)],
)
res = mod.fit(cov_type="clustered", cluster_entity=True)
res


### OLS Regression ###
model = ols(
    "chgdeathsper1m_shifted3dma ~ CriticalCareBeds + GDPpercapita + personsperhousehold + PopulationDensity + retail_and_recreation_percent_change_from_baseline3dma +transit_stations_percent_change_from_baseline3dma",
    data=dfDeathdata[dfDeathdata["chgdeathsper1m_shifted3dma"].between(1, 60)],
    missing="drop",
)
results = model.fit()
results.summary()

# For Dash App:
#   only get data that is needed
dfDeathdatafinal = dfDeathdata[
    [
        "deathsper1m",
        "chgdeathsper1m_shifted3dma",
        "CriticalCareBeds",
        "GDPpercapita",
        "personsperhousehold",
        "PopulationDensity",
        "retail_and_recreation_percent_change_from_baseline3dma",
        "transit_stations_percent_change_from_baseline3dma",
        "parks_percent_change_from_baseline3dma",
        "grocery_and_pharmacy_percent_change_from_baseline3dma",
        "Country",
    ]
].dropna()
#Delete Data with errors (change in deaths can only be positive)
dfDeathdatafinal = dfDeathdatafinal[dfDeathdatafinal["chgdeathsper1m_shifted3dma"] > 0]

dfDeathdatafinal.reset_index(inplace=True)

#Get average movement changes
dfDeathdatafinal['retail_and_recreation_avg_change'] = dfDeathdatafinal.groupby(dfDeathdatafinal['region'])['retail_and_recreation_percent_change_from_baseline3dma'].transform('mean') 

#Only keep last entry
dfDeathdatafinal = dfDeathdatafinal.sort_values(
    by='date', ascending=False
).drop_duplicates(subset=['region'])


col_options = [dict(label=x, value=x) for x in dfDeathdatafinal.columns]
dimensions = ["x", "y", "color", "facet_col", "facet_row"]

app = dash.Dash(
    __name__, external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"]
)

app.layout = html.Div(
    [
        html.H1("Demo: Plotly Express in Dash with Tips Dataset"),
        html.Div(
            [
                html.P([d + ":", dcc.Dropdown(id=d, options=col_options)])
                for d in dimensions
            ],
            style={"width": "25%", "float": "left"},
        ),
        dcc.Graph(id="graph", style={"width": "75%", "display": "inline-block"}),
    ]
)


@app.callback(Output("graph", "figure"), [Input(d, "value") for d in dimensions])
def make_figure(x, y, color, facet_col, facet_row):
    return px.scatter(
        dfDeathdatafinal.dropna(),
        x=x,
        y=y,
        color=color,
        facet_col=facet_col,
        facet_row=facet_row,
        height=700,
    )


if __name__ == "__main__":
    app.run_server(debug=False)
