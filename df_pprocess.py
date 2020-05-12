import warnings
warnings.filterwarnings("ignore")

import pickle
import json
import pandas as pd
import numpy as np
from pathlib import Path
from functions import *

######################################
# Retrieve data
######################################

# Paths

path_UN = Path.cwd() / 'input' / 'world_population_2020.csv'
path_geo = Path.cwd() / 'input'/ 'countries.geojson'

# get data directly from github. The data source provided by Johns Hopkins University.
url_confirmed = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
url_deaths = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'
url_policy = 'https://raw.githubusercontent.com/OxCGRT/covid-policy-tracker/master/data/OxCGRT_latest.csv'
url_ISO = 'https://raw.githubusercontent.com/lukes/ISO-3166-Countries-with-Regional-Codes/master/all/all.csv'

# Data can also be saved locally and read from local drive
# url_confirmed = 'time_series_covid19_confirmed_global.csv'
# url_deaths = 'time_series_covid19_deaths_global.csv'
# url_recovered = 'time_series_covid19_recovered_global.csv'

df_confirmed = pd.read_csv(url_confirmed)
df_deaths = pd.read_csv(url_deaths)
pop = pd.read_csv(path_UN)
policy = pd.read_csv(url_policy)
ISO = pd.read_csv(url_ISO)

#########################################################################################
# Data preprocessing for getting useful data and shaping data compatible to plotly plot
#########################################################################################

# List of EU28 countries
eu28 = ['Austria',	'Italy', 'Belgium',	'Latvia', 'Bulgaria', 'Lithuania', 'Croatia', 'Luxembourg',
            'Cyprus', 'Czech Republic', 'Malta', 'Netherlands', 'Denmark',	'Poland', 'Estonia', 'Portugal', 'Finland',	'Romania',
            'France', 'Slovakia', 'Germany', 'Slovenia', 'Greece', 'Spain', 'Hungary', 'Sweden', 'Ireland', 'United Kingdom']

# Adjust countries' names. Still problems with most French overseas territories and Channel Islands
def adjust_names(data):
    data['Country/Region'].loc[data['Country/Region'] == 'Burma'] = 'Myanmar'
    data['Country/Region'].loc[data['Country/Region'] == 'Cabo Verde'] = 'Cape Verde'
    data['Country/Region'].loc[data['Country/Region'] == 'Congo (Brazzaville)'] = 'Republic of Congo'
    data['Country/Region'].loc[data['Country/Region'] == 'Congo (Kinshasa)'] = 'Democratic Republic of the Congo'
    data['Country/Region'].loc[data['Country/Region'] == 'Czechia'] = 'Czech Republic'
    data['Country/Region'].loc[data['Country/Region'] == 'Eswatini'] = 'Swaziland'
    data['Country/Region'].loc[data['Country/Region'] == 'Korea, South'] = 'South Korea'
    data['Country/Region'].loc[data['Country/Region'] == 'Taiwan*'] = 'Taiwan'
    data['Country/Region'].loc[data['Country/Region'] == 'Timor-Leste'] = 'East Timor'
    data['Country/Region'].loc[data['Country/Region'] == 'US'] = 'United States of America'
    data['Country/Region'].loc[data['Country/Region'] == 'West Bank and Gaza'] = 'Palestine'
    data['Province/State'].loc[data['Province/State'] == 'Falkland Islands (Malvinas)'] = 'Falkland Islands'
    return data

def aggregate_countries(data, graph):
    # For countries that have disaggregated data sum them
    if graph == "map":
        data = data.set_index('Country/Region')
        data['Confirmed'] = data.groupby(level = 0)['Confirmed'].sum()
        data['Deaths'] = data.groupby(level = 0)['Deaths'].sum()
    else:
        data['Country/Region'][(data['Country/Region'] == 'France') & (data['Province/State'].isna() == False)] = data['Province/State']
        data['Country/Region'][(data['Country/Region'] == 'United Kingdom') & (data['Province/State'].isna() == False)] = data['Province/State']
        data['Country/Region'][(data['Country/Region'] == 'Netherlands') & (data['Province/State'].isna() == False)] = data['Province/State']
        data['Country/Region'][(data['Country/Region'] == 'Denmark') & (data['Province/State'].isna() == False)] = data['Province/State']
        data = data.set_index('Country/Region')
        data = data.groupby(level = 0).sum()
    data = data.groupby(level = 0).first()
    data = data.reset_index()
    return data

def center_date(row, max_MA_index, country):
    temp_string = str(row['index']-max_MA_index)
    final_string = ''
    for char in temp_string:
        if char == '-' or char.isdigit():
            final_string += char
        else:
            break
    row[country] = final_string
    return row

def moving_average(data, window):
    df_sub = data.copy()
    df_sub = df_sub.apply(lambda x: x - x.shift(periods = 1))
    df_sub.iloc[0] = data.iloc[0]
    df_MA = df_sub.copy()
    for country in list(df_MA):
        if data[country].iloc[-1] != 0:
            df_MA[country] = (df_MA[country]/data[country].iloc[-1])*100
            df_MA[country] = df_MA[country].astype('float64').apply(np.log)
            df_MA[country] = df_MA[country].rolling(window).mean()
        else:
            df_MA[country] = np.nan
    df_centered_date = df_MA.copy()
    for country in list(df_centered_date):
        if not np.isnan(df_centered_date[country].max()):
            df_temp = df_centered_date.copy()
            max_MA_index = df_temp.loc[df_temp[country] == df_temp[country].max()].index.tolist()[0]
            df_temp.loc[max_MA_index, [country]] = 0.0
            df_temp = df_temp.reset_index()
            df_temp = df_temp[[country, 'index']].apply(center_date, args = (max_MA_index, country), axis = 1)
            df_temp = df_temp.set_index('index')
            df_centered_date[country] = df_temp[country].copy()
        else:
            pass
            #print(f'Error for {country}')
    return df_MA, df_centered_date

df_confirmed = adjust_names(df_confirmed)
df_deaths = adjust_names(df_deaths)

df_confirmed = aggregate_countries(df_confirmed, graph = 'scatter')
df_deaths = aggregate_countries(df_deaths, graph = 'scatter')

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


df_EU28.insert(loc=0, column='cases', value=['confirmed', 'deaths'])
df_world.insert(loc=0, column='cases', value=['confirmed', 'deaths'])

set_countries_JH = open('input/set_countries_JH.txt', 'rb')
old_JH_countries = pickle.load(set_countries_JH)
set_countries_JH.close()

new_JH_countries = set(df_confirmed['Country/Region'])
if old_JH_countries != new_JH_countries:
    diff_old_from_new = old_JH_countries.difference(new_JH_countries)
    diff_new_from_old = new_JH_countries.difference(old_JH_countries)
    if len(diff_old_from_new) != 0:
        pass
        #print(diff_old_from_new)
    if len(diff_new_from_old) != 0:
        pass
        #print(diff_new_from_old)
else:
    pass
    #print('No update in the set of countries')

# Compute the increment from the previous day for the latest available data

daily_confirmed_world = df_world.iloc[0, -1] - df_world.iloc[0, -2]
daily_deaths_world = df_world.iloc[1, -1] - df_world.iloc[1, -2]

daily_confirmed_EU28 = df_EU28.iloc[0, -1] - df_EU28.iloc[0, -2]
daily_deaths_EU28 = df_EU28.iloc[1, -1] - df_EU28.iloc[1, -2]

# Recreate required columns for map data
map_data = df_confirmed[["Country/Region", "Lat", "Long"]]
map_data['Confirmed'] = df_confirmed.loc[:, df_confirmed.columns[-1]]
map_data['Deaths'] = df_deaths.loc[:, df_deaths.columns[-1]]

map_data = aggregate_countries(map_data , graph = 'map')

pop['pop2019'] = pop['pop2019'] * 1000
pop['name'].loc[pop['name'] == 'United States'] = 'United States of America'
pop = pop[['name', 'pop2019']]
pop['name'].loc[pop['name'] == 'Ivory Coast'] = "Cote d'Ivoire"
pop['name'].loc[pop['name'] == 'Republic of the Congo'] = "Republic of Congo"
pop['name'].loc[pop['name'] == 'DR Congo'] = "Democratic Republic of the Congo"
pop['name'].loc[pop['name'] == 'Timor-Leste'] = "East Timor"
pop['name'].loc[pop['name'] == 'Vatican City'] = "Holy See"
pop['name'].loc[pop['name'] == 'Macedonia'] = "North Macedonia"
pop['name'].loc[pop['name'] == 'Saint Barthélemy'] = "Saint Barthelemy"
pop['name'].loc[pop['name'] == 'Saint Martin'] = "St Martin"

temp_pop_names = list(pop['name'])

not_matched_countries = []

for i in list(df_confirmed['Country/Region'].unique()):
    if i not in temp_pop_names:
        not_matched_countries.append(i)

pop_world = pop[0:0].copy()
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

with open(path_geo) as f:
        coord_df = json.load(f)

temp_list = []
for i in range(len(coord_df['features'])):
    if coord_df['features'][i]['properties']['ADMIN'] == 'The Bahamas':
        coord_df['features'][i]['properties']['ADMIN'] = 'Bahamas'
    elif coord_df['features'][i]['properties']['ADMIN'] == 'Vatican':
        coord_df['features'][i]['properties']['ADMIN'] = 'Holy See'
    elif coord_df['features'][i]['properties']['ADMIN'] == 'Jersey':
        coord_df['features'][i]['properties']['ADMIN'] = 'Channel Islands'
    elif coord_df['features'][i]['properties']['ADMIN'] == 'Guernsey':
        coord_df['features'][i]['properties']['ADMIN'] = 'Channel Islands'
    elif coord_df['features'][i]['properties']['ADMIN'] == 'Ivory Coast':
        coord_df['features'][i]['properties']['ADMIN'] = "Cote d'Ivoire"
    elif coord_df['features'][i]['properties']['ADMIN'] == 'CuraÃ§ao':
        coord_df['features'][i]['properties']['ADMIN'] = "Curacao"
    elif coord_df['features'][i]['properties']['ADMIN'] == 'Guinea Bissau':
        coord_df['features'][i]['properties']['ADMIN'] = "Guinea-Bissau"
    elif coord_df['features'][i]['properties']['ADMIN'] == 'Saint Martin':
        coord_df['features'][i]['properties']['ADMIN'] = "St Martin"
    elif coord_df['features'][i]['properties']['ADMIN'] == 'Macedonia':
        coord_df['features'][i]['properties']['ADMIN'] = "North Macedonia"
    elif coord_df['features'][i]['properties']['ADMIN'] == 'Republic of Serbia':
        coord_df['features'][i]['properties']['ADMIN'] = "Serbia"
    elif coord_df['features'][i]['properties']['ADMIN'] == 'United Republic of Tanzania':
        coord_df['features'][i]['properties']['ADMIN'] = "Tanzania"

    temp_list.append(coord_df['features'][i]['properties']['ADMIN'])
temp_list.sort()

# The code below prints the countries for which we have COVID-19 data but a mismatch/lack of geo data
'''
for i in list(map_data['Country/Region']):
    if i not in temp_list:
        print(i)
'''

df_confirmed_t=df_confirmed.drop(['Lat','Long'],axis=1).T
df_deaths_t=df_deaths.drop(['Lat','Long'],axis=1).T

df_confirmed_t.columns = df_confirmed_t.iloc[0]
df_confirmed_t = df_confirmed_t.iloc[1:]
df_deaths_t.columns = df_deaths_t.iloc[0]
df_deaths_t = df_deaths_t.iloc[1:]

# Remove countries for which we lack population data from the UN
df_confirmed_t = df_confirmed_t.drop(not_matched_countries, axis = 1)
df_deaths_t = df_deaths_t.drop(not_matched_countries, axis = 1)

# Set the countries available as choices in the dropdown menu
available_indicators = ['World', 'EU28']
for i in list(df_confirmed_t):
    available_indicators.append(i)


df_world_t = df_world.T
df_world_t.columns = df_world_t.iloc[0]
df_world_t = df_world_t.iloc[1:]


df_EU28_t = df_EU28.T
df_EU28_t.columns = df_EU28_t.iloc[0]
df_EU28_t = df_EU28_t.iloc[1:]


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

# Define the variable names for the dropdown manu used for to choose variables
available_variables = ['Mortality rate', 'Share of infected population', 'Growth rate confirmed cases', 'Growth rate deaths']

# Part to adjust data for plots with Stringency Index
policy = policy[['CountryName', 'Date', 'StringencyIndexForDisplay']]

# List with first 4 countries by cases
top_4 = df_confirmed.sort_values(by=df_confirmed.columns[-1], ascending = False)['Country/Region'].head(4).to_list()

# Fix ISO codes dictionary
ISO['name'].loc[ISO['name'] == 'Bolivia (Plurinational State of)'] = "Bolivia"
ISO['name'].loc[ISO['name'] == 'Brunei Darussalam'] = "Brunei"
ISO['name'].loc[ISO['name'] == 'Cabo Verde'] = "Cape Verde"
ISO['name'].loc[ISO['name'] == 'Congo, Democratic Republic of the'] = "Democratic Republic of the Congo"
ISO['name'].loc[ISO['name'] == 'Congo'] = "Republic of Congo"
ISO['name'].loc[ISO['name'] == "Côte d'Ivoire"] = "Cote d'Ivoire"
ISO['name'].loc[ISO['name'] == "Curaçao"] = "Curacao"
ISO['name'].loc[ISO['name'] == "Czechia"] = "Czech Republic"
ISO['name'].loc[ISO['name'] == "Eswatini"] = "Swaziland"
ISO['name'].loc[ISO['name'] == "Falkland Islands (Malvinas)"] = "Falkland Islands"
ISO['name'].loc[ISO['name'] == "Iran (Islamic Republic of)"] = "Iran"
ISO['name'].loc[ISO['name'] == "Korea, Republic of"] = "South Korea"
ISO['name'].loc[ISO['name'] == "Lao People's Democratic Republic"] = "Laos"
ISO['name'].loc[ISO['name'] == "Virgin Islands (British)"] = "British Virgin Islands"
ISO['name'].loc[ISO['name'] == "Timor-Leste"] = "East Timor"
ISO['name'].loc[ISO['name'] == "Moldova, Republic of"] = "Moldova"
ISO['name'].loc[ISO['name'] == "Palestine, State of"] = "Palestine"
ISO['name'].loc[ISO['name'] == "Réunion"] = "Reunion"
ISO['name'].loc[ISO['name'] == "Russian Federation"] = "Russia"
ISO['name'].loc[ISO['name'] == "Saint Barthélemy"] = "Saint Barthelemy"
ISO['name'].loc[ISO['name'] == "Sint Maarten (Dutch part)"] = "Sint Maarten"
ISO['name'].loc[ISO['name'] == "Saint Martin (French part)"] = "St Martin"
ISO['name'].loc[ISO['name'] == "Syrian Arab Republic"] = "Syria"
ISO['name'].loc[ISO['name'] == "Taiwan, Province of China"] = "Taiwan"
ISO['name'].loc[ISO['name'] == "Tanzania, United Republic of"] = "Tanzania"
ISO['name'].loc[ISO['name'] == "United Kingdom of Great Britain and Northern Ireland"] = "United Kingdom"
ISO['name'].loc[ISO['name'] == "Venezuela (Bolivarian Republic of)"] = "Venezuela"
ISO['name'].loc[ISO['name'] == "Viet Nam"] = "Vietnam"

'''
for country in list(df_confirmed_t):
    if country not in ISO['name'].to_list():
        print(country)
print(ISO['name'].to_list())
'''

policy = policy.rename(columns = {'CountryName': 'name', 'StringencyIndexForDisplay': 'Stringency Index'})
date_max_policy = str(policy['Date'].max())

if str(df_confirmed_t.reset_index()['index'].iloc[-1])[:10] != (date_max_policy[:4] + '-' + date_max_policy[4:6] + '-' + date_max_policy[6:]):
    policy = policy[(policy['Date'] >= 20200122) & (policy['Date'] != policy['Date'].max())]
else:
    policy = policy[policy['Date'] >= 20200122]

policy['name'].loc[policy['name'] == 'Kyrgyz Republic'] = 'Kyrgyzstan'
policy['name'].loc[policy['name'] == 'Democratic Republic of Congo'] = 'Democratic Republic of the Congo'
policy['name'].loc[policy['name'] == 'United States'] = 'United States of America'
policy['name'].loc[policy['name'] == 'Eswatini'] = 'Swaziland'
policy['name'].loc[policy['name'] == 'Slovak Republic'] = 'Slovakia'

policy['Date'] = policy['Date'].astype('str')
policy['Date'] = pd.to_datetime(policy['Date'], format='%Y-%m-%d')

df_policy_index = df_confirmed_t.copy().astype('float64')

temp_list_2 = []

for i in list(df_confirmed_t):
    if i not in set(policy['name']):
        temp_list_2.append(i)
    df_policy_index[i] = np.nan

# Missing Spain data for May 2
for country in list(df_policy_index):
    if country not in temp_list_2:
        temp_policy = policy[policy['name'] == country]
        for date in df_policy_index.index:
            try: 
                temp_value = float(temp_policy[policy['Date'] == date]['Stringency Index'])
                df_policy_index.at[date, country] = temp_value
            except:
                df_policy_index.at[date, country] = np.nan

df_epic_confirmed, df_epic_days_confirmed = moving_average(df_confirmed_t, 3)
df_epic_deaths, df_epic_days_deaths = moving_average(df_deaths_t, 3)


df_tab_right = df_confirmed_t[0:0].copy()
for country in list(df_confirmed_t):
    df_tab_right.at['Confirmed cases', country] = df_confirmed_t.iloc[-1][country]
    df_tab_right.at['Deaths', country] = df_deaths_t.iloc[-1][country]
    if pop_t[country][0] != 0:
        df_tab_right.at['Mortality rate', country] = (df_deaths_t.iloc[-1][country])/(pop_t[country][0])
    else:
        df_tab_right.at['Mortality rate', country] = np.nan
    if pop_t[country][0] != 0:
        df_tab_right.at['Share of population infected', country] = (df_confirmed_t.iloc[-1][country])/(pop_t[country][0])
    else:
        df_tab_right.at['Share of population infected', country] = np.nan
    df_tab_right.at['Share of global confirmed cases', country] = (df_confirmed_t.iloc[-1][country]/df_confirmed_t.iloc[-1]['World'])
    df_tab_right.at['Share of global deaths', country] = (df_deaths_t.iloc[-1][country]/df_deaths_t.iloc[-1]['World'])
    df_tab_right.at['Date of 1st confirmed case', country] = str(df_confirmed_t[country][df_confirmed_t[country] > 0].first_valid_index())[0:10]
    df_tab_right.at['Date of 1st confirmed death', country] = str(df_deaths_t[country][df_deaths_t[country] > 0].first_valid_index())[0:10]
    df_tab_right.at['Stringency Index', country] = df_policy_index.iloc[-1][country]
    df_tab_right.at['Population in 2019', country] = pop_t[country][0]


set_countries_JH = open('input/set_countries_JH.txt', 'wb')
pickle.dump(set(df_confirmed['Country/Region']), set_countries_JH)
set_countries_JH.close()
# PICKLIFYCATION TIME
def picklify(dataframe, name):
    file_write = open(f"./pickles_jar/{name}.pkl", 'wb')
    pickle.dump(dataframe, file_write)
    file_write.close()


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
    [coord_df, 'coord_df'],
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
    ]


for dataframe, name in dataframe_list:
    picklify(dataframe, name)
