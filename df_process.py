import warnings
warnings.filterwarnings("ignore")

import pickle
import json
import pandas as pd
import numpy as np
from pathlib import Path
from process_functions import adjust_names, aggregate_countries, moving_average, write_log
from pickle_functions import picklify, unpicklify

######################################
# Retrieve data
######################################

# Paths
path_UN = Path.cwd() / 'input' / 'world_population_2020.csv'
path_confirmed = Path.cwd() / 'input' / 'df_confirmed.csv'
path_deaths = Path.cwd() / 'input' / 'df_deaths.csv'
path_policy = Path.cwd() / 'input' / 'df_policy.csv'
#path_geo = Path.cwd() / 'input'/ 'countries.geojson'

# get data directly from github. The data source provided by Johns Hopkins University.
url_confirmed = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
url_deaths = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'
url_policy = 'https://raw.githubusercontent.com/OxCGRT/covid-policy-tracker/master/data/OxCGRT_latest.csv'

#df.to_csv(r'C:/Users/John\Desktop/export_dataframe.csv', index = None)
pop = pd.read_csv(path_UN)

#load old data
df_confirmed_backup = pd.read_csv(path_confirmed)
old_df_confirmed = df_confirmed_backup[['Province/State','Country/Region']]
df_deaths_backup = pd.read_csv(path_deaths)
old_df_deaths = df_deaths_backup[['Province/State','Country/Region']]
df_policy_backup = pd.read_csv(path_policy)
old_names_df_policy = set(df_policy_backup['CountryName'])
old_dates_df_policy = set(df_policy_backup['Date'])
#load new data
df_confirmed = pd.read_csv(url_confirmed, error_bad_lines=False)
new_df_confirmed = df_confirmed[['Province/State','Country/Region']]
df_deaths = pd.read_csv(url_deaths, error_bad_lines=False)
new_df_deaths = df_confirmed[['Province/State','Country/Region']]
df_policy = pd.read_csv(url_policy, error_bad_lines=False)
new_names_df_policy = set(df_policy['CountryName'])
new_dates_df_policy = set(df_policy['Date'])

#compute difference of rows and columns
confirmed_country_diff = new_df_confirmed[~new_df_confirmed.apply(tuple,1).isin(old_df_confirmed.apply(tuple,1))]
confirmed_date_diff = set(df_confirmed.columns).symmetric_difference(set(df_confirmed_backup.columns))
deaths_country_diff = new_df_deaths[~new_df_deaths.apply(tuple,1).isin(old_df_deaths.apply(tuple,1))]
deaths_date_diff = set(df_deaths.columns).symmetric_difference(set(df_deaths_backup.columns))
policy_country_diff = new_names_df_policy.symmetric_difference(old_names_df_policy)
policy_date_diff = new_dates_df_policy.symmetric_difference(old_dates_df_policy)

#write log and load the backup df if there are new countries until the next update
#for confirmed
write_log('--- confirmed cases file check'.upper())
if confirmed_country_diff.empty:
    write_log('no new countries added')
else:
    write_log('new countries added:\n' + str(confirmed_country_diff))
    #df_confirmed = df_confirmed_backup

if len(confirmed_date_diff) > 1:
    write_log('multiple new dates added: ' + str(confirmed_date_diff))
elif len(confirmed_date_diff) == 1:
    write_log('new date added: ' + str(confirmed_date_diff))
else:
    write_log('no new date added')

#for deaths
write_log('--- deaths file check'.upper())
if deaths_country_diff.empty:
    write_log('no new countries added')
else:
    write_log('new countries added:\n' + str(deaths_country_diff))
    #df_deaths = df_deaths_backup

if len(deaths_date_diff) > 1:
    write_log('multiple new dates added: ' + str(deaths_date_diff))
elif len(deaths_date_diff) == 1:
    write_log('new date added: ' + str(deaths_date_diff))
else:
    write_log('no new date added')

#for policy
write_log('--- policy file check'.upper())
if not bool(policy_country_diff):
    write_log('no new countries added')
else:
    write_log('new countries added:\n' + str(policy_country_diff))
    #df_policy = df_policy_backup

if len(policy_date_diff) > 1:
    write_log('multiple new dates added: ' + str(policy_date_diff))
elif len(policy_date_diff) == 1:
    write_log('new date added: ' + str(policy_date_diff))
else:
    write_log('no new date added')

df_confirmed.to_csv(path_confirmed, index = None)
df_deaths.to_csv(path_deaths, index = None)
df_policy.to_csv(path_policy, index = None)



#########################################################################################
# Data preprocessing for getting useful data and shaping data compatible to plotly plot
#########################################################################################

# List of EU28 countries
eu28 = ['Austria',	'Italy', 'Belgium',	'Latvia', 'Bulgaria', 'Lithuania', 'Croatia', 'Luxembourg',
            'Cyprus', 'Czech Republic', 'Malta', 'Netherlands', 'Denmark',	'Poland', 'Estonia', 'Portugal', 'Finland',	'Romania',
            'France', 'Slovakia', 'Germany', 'Slovenia', 'Greece', 'Spain', 'Hungary', 'Sweden', 'Ireland', 'United Kingdom']


#filter the countries' names to fit our list of names
df_confirmed = adjust_names(df_confirmed.copy())
df_deaths = adjust_names(df_deaths.copy())
df_confirmed = aggregate_countries(df_confirmed.copy(), graph = 'scatter')
df_deaths = aggregate_countries(df_deaths.copy(), graph = 'scatter')

# Create a dataframe for the world with the date as columns, keep the Province/State column to rename it below
df_world = df_confirmed[0:0].drop(columns = ['Country/Region', 'Lat', 'Long']).copy()

# Create dataframes for EU28 for each variable
df_EU28_confirmed = df_confirmed.set_index('Country/Region').loc[eu28].copy()
df_EU28_confirmed = df_EU28_confirmed.drop(columns = ['Lat', 'Long'])
df_EU28_deaths = df_deaths.set_index('Country/Region').loc[eu28].copy()
df_EU28_deaths = df_EU28_deaths.drop(columns = ['Lat', 'Long'])

# Sum variables to get aggregate EU28 values
df_confirmed_EU28 = df_EU28_confirmed.reset_index().drop(columns = ['Country/Region']).iloc[:, :].sum(axis=0)
df_deaths_EU28 = df_EU28_deaths.reset_index().drop(columns = ['Country/Region']).iloc[:, :].sum(axis=0)

# Drop columns
df_EU28 = df_EU28_confirmed[0:0].reset_index().drop(columns = ['Country/Region']).copy()

# Total cases
df_confirmed_total = df_confirmed.drop(columns = ['Country/Region', 'Lat', 'Long']).iloc[:, :].sum(axis=0)
df_deaths_total = df_deaths.drop(columns = ['Country/Region', 'Lat', 'Long']).iloc[:, :].sum(axis=0)

# Add the rows to the world dataframe by date
df_world = df_world.append([df_confirmed_total, df_deaths_total] , ignore_index=True)
df_EU28 = df_EU28.append([df_confirmed_EU28, df_deaths_EU28] , ignore_index=True)

#add a column to explicitly define the the row for confirmed cases and for deaths
df_EU28.insert(loc=0, column='cases', value=['confirmed', 'deaths'])
df_world.insert(loc=0, column='cases', value=['confirmed', 'deaths'])

# Compute the increment from the previous day for the latest available data
daily_confirmed_world = df_world.iloc[0, -1] - df_world.iloc[0, -2]
daily_deaths_world = df_world.iloc[1, -1] - df_world.iloc[1, -2]

daily_confirmed_EU28 = df_EU28.iloc[0, -1] - df_EU28.iloc[0, -2]
daily_deaths_EU28 = df_EU28.iloc[1, -1] - df_EU28.iloc[1, -2]

# Recreate required columns for map data
map_data = df_confirmed[["Country/Region", "Lat", "Long"]]
map_data['Confirmed'] = df_confirmed.loc[:, df_confirmed.columns[-1]]
map_data['Deaths'] = df_deaths.loc[:, df_deaths.columns[-1]]

#aggregate the data of countries divided in provinces
map_data = aggregate_countries(map_data , graph = 'map')

#adjust some names of countries in the population dataframe
pop = pop[['name', 'pop2019']]
pop['pop2019'] = pop['pop2019'] * 1000
pop.at[pop['name'] == 'United States','name'] = 'United States of America'
pop.at[pop['name'] == 'Ivory Coast','name'] = "Cote d'Ivoire"
pop.at[pop['name'] == 'Republic of the Congo','name'] = "Republic of Congo"
pop.at[pop['name'] == 'DR Congo','name'] = "Democratic Republic of the Congo"
pop.at[pop['name'] == 'Timor-Leste','name'] = "East Timor"
pop.at[pop['name'] == 'Vatican City','name'] = "Holy See"
pop.at[pop['name'] == 'Macedonia','name'] = "North Macedonia"
pop.at[pop['name'] == 'Saint Barthélemy','name'] = "Saint Barthelemy"
pop.at[pop['name'] == 'Saint Martin','name'] = "St Martin"

temp_pop_names = list(pop['name'])

#create a list with the names of countries in the cases df not present in the population df
not_matched_countries = []
for i in list(df_confirmed['Country/Region'].unique()):
    if i not in temp_pop_names:
        not_matched_countries.append(i)

#add the total world and eu28 population to the population df
world_population = pop.drop(columns = ['name']).iloc[:, :].sum(axis=0)
pop_EU28 = pop.set_index('name').loc[eu28].copy()
EU28_population = pop_EU28.reset_index().drop(columns = ['name']).iloc[:, :].sum(axis=0)
pop = pop.set_index('name')
pop_t = pop.T.astype(int)
pop_t['World'] = int(world_population)
pop_t['EU28'] = int(EU28_population)

#last 24 hours increase
#map_data['Deaths_24hr']=df_deaths.iloc[:,-1] - df_deaths.iloc[:,-2]
#map_data['Confirmed_24hr']=df_confirmed.iloc[:,-1] - df_confirmed.iloc[:,-2]
#map_data.sort_values(by='Confirmed', ascending=False, inplace=True)


#create utility df transposed without lat and lon
df_confirmed_t=df_confirmed.drop(['Lat','Long'],axis=1).T
df_deaths_t=df_deaths.drop(['Lat','Long'],axis=1).T
df_confirmed_t.columns = df_confirmed_t.iloc[0]
df_confirmed_t = df_confirmed_t.iloc[1:]
df_deaths_t.columns = df_deaths_t.iloc[0]
df_deaths_t = df_deaths_t.iloc[1:]


df_world_t = df_world.T
df_world_t.columns = df_world_t.iloc[0]
df_world_t = df_world_t.iloc[1:]


df_EU28_t = df_EU28.T
df_EU28_t.columns = df_EU28_t.iloc[0]
df_EU28_t = df_EU28_t.iloc[1:]


# Remove countries for which we lack population data from the UN
df_confirmed_t = df_confirmed_t.drop(not_matched_countries, axis = 1)
df_deaths_t = df_deaths_t.drop(not_matched_countries, axis = 1)

# Set the countries available as choices in the dropdown menu
available_indicators = ['World', 'EU28']
for i in list(df_confirmed_t):
    available_indicators.append(i)



df_confirmed_t.index=pd.to_datetime(df_confirmed_t.index)
df_deaths_t.index=pd.to_datetime(df_confirmed_t.index)
df_world_t.index = pd.to_datetime(df_world_t.index)
df_EU28_t.index = pd.to_datetime(df_EU28_t.index)
df_left_list_confirmed = df_confirmed_t.iloc[-1].copy()
df_left_list_confirmed_t = df_left_list_confirmed.T
df_left_list_confirmed_t = df_left_list_confirmed_t.sort_values(ascending = False)

df_left_list_deaths = df_deaths_t.iloc[-1].copy()
df_left_list_deaths_t = df_left_list_deaths.T
df_left_list_deaths_t = df_left_list_deaths_t.sort_values(ascending = False)

df_left_list_daily_confirmed_increase = df_confirmed_t[0:0].copy()
for country in list(df_confirmed_t):
    df_left_list_daily_confirmed_increase.at['Daily increase confirmed cases', country] = df_confirmed_t.iloc[-1][country] - df_confirmed_t.iloc[-2][country]

df_left_list_daily_confirmed_increase = df_left_list_daily_confirmed_increase.T.sort_values(by = 'Daily increase confirmed cases', ascending = False)
df_left_list_daily_confirmed_increase = df_left_list_daily_confirmed_increase.T

df_left_list_daily_deaths_increase = df_deaths_t[0:0].copy()
for country in list(df_deaths_t):
    df_left_list_daily_deaths_increase.at['Daily increase deaths', country] = df_deaths_t.iloc[-1][country] - df_deaths_t.iloc[-2][country]

df_left_list_daily_deaths_increase = df_left_list_daily_deaths_increase.T.sort_values(by = 'Daily increase deaths', ascending = False)
df_left_list_daily_deaths_increase = df_left_list_daily_deaths_increase.T



df_confirmed_t['World'] = df_world_t['confirmed']
df_deaths_t['World'] = df_world_t['deaths']

df_confirmed_t['EU28'] = df_EU28_t['confirmed']
df_deaths_t['EU28'] = df_EU28_t['deaths']

# set the variable names for the dropdown manu used for to choose variables
available_variables = ['Mortality rate', 'Infection rate', 'Growth rate confirmed cases', 'Growth rate deaths']

# Part to adjust data for plots with Stringency Index
df_policy = df_policy[['CountryName', 'Date', 'StringencyIndexForDisplay']]

# List with first 4 countries by cases
top_4 = df_confirmed.sort_values(by=df_confirmed.columns[-1], ascending = False)['Country/Region'].head(4).to_list()

#adjust the policy df to fit other dfs
df_policy = df_policy.rename(columns = {'CountryName': 'name', 'StringencyIndexForDisplay': 'Stringency Index'})
date_max_policy = str(df_policy['Date'].max())

#
if str(df_confirmed_t.reset_index()['index'].iloc[-1])[:10] != (date_max_policy[:4] + '-' + date_max_policy[4:6] + '-' + date_max_policy[6:]):
    df_policy = df_policy[(df_policy['Date'] >= 20200122) & (df_policy['Date'] != df_policy['Date'].max())]
else:
    df_policy = df_policy[df_policy['Date'] >= 20200122]

df_policy.at[df_policy['name'] == 'Kyrgyz Republic','name'] = 'Kyrgyzstan'
df_policy.at[df_policy['name'] == 'Democratic Republic of Congo','name'] = 'Democratic Republic of the Congo'
df_policy.at[df_policy['name'] == 'United States','name'] = 'United States of America'
df_policy.at[df_policy['name'] == 'Eswatini','name'] = 'Swaziland'
df_policy.at[df_policy['name'] == 'Slovak Republic','name'] = 'Slovakia'
df_policy.at[df_policy['name'] == 'Timor-Leste','name'] = 'East Timor'
df_policy.at[df_policy['name'] == 'Congo','name'] = "Republic of Congo"

df_policy['Date'] = df_policy['Date'].astype('str')
df_policy['Date'] = pd.to_datetime(df_policy['Date'], format='%Y-%m-%d')

df_policy_index = df_confirmed_t.copy().astype('float64')

#print(list(df_confirmed_t))
#print(set(df_policy['name']))
#store the countries without policy index
countries_w_o_policy = []
for i in list(df_confirmed_t):
    if i not in set(df_policy['name']):
        countries_w_o_policy.append(i)
    df_policy_index[i] = np.nan
#
#print(countries_w_o_policy)
#
#store the countries without policy index
#countries_w_policy = []
#for i in set(df_policy['name']):
#    if i not in list(df_confirmed_t):
#        countries_w_policy.append(i)
#
#print(countries_w_policy)

# Missing Spain data for May 2 
# fill the gaps for consistency and create the df for the stringency index
for country in list(df_policy_index):
    if country not in countries_w_o_policy:
        temp_policy = df_policy[df_policy['name'] == country]
        for date in df_policy_index.index:
            try: 
                temp_value = float(temp_policy[df_policy['Date'] == date]['Stringency Index'])
                df_policy_index.at[date, country] = temp_value
            except:
                df_policy_index.at[date, country] = np.nan

# create the df with moving_average
df_epic_confirmed, df_epic_days_confirmed = moving_average(df_confirmed_t, 3)
df_epic_deaths, df_epic_days_deaths = moving_average(df_deaths_t, 3)

#store the statistics for the right tab countries
df_tab_right = df_confirmed_t[0:0].copy()
for country in list(df_confirmed_t):
    df_tab_right.at['Confirmed cases', country] = df_confirmed_t.iloc[-1][country]
    df_tab_right.at['Deaths', country] = df_deaths_t.iloc[-1][country]
    if pop_t[country][0] != 0:
        df_tab_right.at['Mortality rate', country] = (df_deaths_t.iloc[-1][country])/(pop_t[country][0])
    else:
        df_tab_right.at['Mortality rate', country] = np.nan
    if pop_t[country][0] != 0:
        df_tab_right.at['Infection rate', country] = (df_confirmed_t.iloc[-1][country])/(pop_t[country][0])
    else:
        df_tab_right.at['Infection rate', country] = np.nan
    if df_confirmed_t.iloc[-1]['World'] > 0:
        df_tab_right.at['Share of global confirmed cases', country] = (df_confirmed_t.iloc[-1][country]/df_confirmed_t.iloc[-1]['World'])
    else:
        df_tab_right.at['Share of global confirmed cases', country] = np.nan
        write_log("***division by zero in df_confirmed_t.iloc[-1]['World']***")
    if df_deaths_t.iloc[-1]['World'] > 0:
        df_tab_right.at['Share of global deaths', country] = (df_deaths_t.iloc[-1][country]/df_deaths_t.iloc[-1]['World'])
    else:
        df_tab_right.at['Share of global deaths', country] = np.nan
        write_log("***division by zero in df_deaths_t.iloc[-1]['World']***")
    df_tab_right.at['Date of 1st confirmed case', country] = str(df_confirmed_t[country][df_confirmed_t[country] > 0].first_valid_index())[0:10]
    df_tab_right.at['Date of 1st confirmed death', country] = str(df_deaths_t[country][df_deaths_t[country] > 0].first_valid_index())[0:10]
    #take the last non-null value
    ind = len(df_policy_index[country])-1
    while ind >=0 and pd.isna(df_policy_index.iloc[ind][country]):
        ind-=1
    df_tab_right.at['Stringency Index', country] = df_policy_index.iloc[ind][country]
    df_tab_right.at['Population in 2019', country] = pop_t[country][0]

#store the pickles for all the df needed
dataframe_list = [
    [df_confirmed_t, 'df_confirmed_t'],
    [df_deaths_t, 'df_deaths_t'],
    [df_policy_index, 'df_policy_index'],
    [df_epic_confirmed, 'df_epic_confirmed'],
    [df_epic_days_confirmed, 'df_epic_days_confirmed'],
    [df_epic_deaths, 'df_epic_deaths'],
    [df_epic_days_deaths, 'df_epic_days_deaths'],
    [df_tab_right, 'df_tab_right'],
    [pop_t, 'pop_t'],
    [map_data, 'map_data'],
    [df_world, 'df_world'],
    [df_EU28, 'df_EU28'],
    [df_left_list_confirmed_t, 'df_left_list_confirmed_t'],
    [df_left_list_deaths_t, 'df_left_list_deaths_t'],
    [df_left_list_daily_confirmed_increase, 'df_left_list_daily_confirmed_increase'],
    [df_left_list_daily_deaths_increase, 'df_left_list_daily_deaths_increase'],
    [daily_deaths_world, 'daily_deaths_world'],
    [daily_confirmed_world, 'daily_confirmed_world'],
    [daily_deaths_EU28, 'daily_deaths_EU28'],
    [daily_confirmed_EU28, 'daily_confirmed_EU28'],
    [top_4, 'top_4'],
    [available_variables, 'available_variables'],
    [available_indicators, 'available_indicators'],
    #[ISO, 'ISO'],
    ]


for dataframe, name in dataframe_list:
    picklify(dataframe, name)
