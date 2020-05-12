import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import datetime
import json
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table as dt
import pickle

from dash.dependencies import Input, Output, State
from pathlib import Path

path_input = Path.cwd() / 'input'
Path.mkdir(path_input, exist_ok = True)
path_UN = Path.cwd() / 'input' / 'world_population_2020.csv'
path_geo = Path.cwd() / 'input'/ 'countries.geojson'
path_policy = Path.cwd() / 'input' / 'policy.csv'

#####################################################################################################################################
# Boostrap CSS and font awesome . Option 1) Run from codepen directly Option 2) Copy css file to assets folder and run locally
#####################################################################################################################################
external_stylesheets = [dbc.themes.FLATLY]

#Insert your javascript here. In this example, addthis.com has been added to the web app for people to share their webpage

app = dash.Dash(__name__, external_stylesheets = external_stylesheets)

app.title = 'COVID-19 - World dashboard'

#for heroku to run correctly
server = app.server

#Overwrite your CSS setting by including style locally

######################################
# Retrieve data
######################################

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

def growth_rate(data, window):
    df_sub = data.copy()
    df_sub = df_sub.apply(lambda x: x - x.shift(periods = 1))
    df_sub.iloc[0] = data.iloc[0]
    df_GR = df_sub.copy()
    temp_data = data.copy()
    for country in list(df_GR):
        temp_data[country] = temp_data[country].replace(0, np.nan)
        df_GR[country] = (df_GR[country]/temp_data[country].shift(periods = 1))
        df_GR[country] = df_GR[country].rolling(window).mean()
    return df_GR

def ticks_log(df, selected_country):
    temp_max = 0
    label_max = []
    text_label_max = []
    tick = 1
    for country in selected_country:
        if temp_max < df[country].max():
            temp_max = df[country].max()
    while tick < temp_max*(0.50):
        label_max.append(tick)
        text_label_max.append(f'{tick:,}')
        tick *= 10
    label_max.append(temp_max)
    text_label_max.append(f'{temp_max:,}')
    return label_max, text_label_max

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

#############################################################################
# mapbox_access_token keys, not all mapbox function require token to function. 
#############################################################################


mapbox_access_token = 'pk.eyJ1IjoiZmVkZWdhbGwiLCJhIjoiY2s5azJwaW80MDQxeTNkcWh4bGhjeTN2NyJ9.twKWO-W5wPLX6m9OfrpZCw'

def gen_map(map_data,zoom,lat,lon):
    return {
        "data": [{
            "type": "choroplethmapbox",  #specify the type of data to generate, in this case, scatter map box is used
            "locations": list(map_data['Country/Region']),
            "geojson": coord_df,
            "featureidkey": 'properties.ADMIN',
            "z": np.log(list(map_data['Confirmed'])),
            "hoverinfo": "text",         
            "hovertext": [f"Country/Region: {map_data.iloc[indice]['Country/Region']} <br>Confirmed: {map_data.iloc[indice]['Confirmed']:,} <br>Deaths: {map_data.iloc[indice]['Deaths']:,}" for indice in range(len(map_data['Country/Region']))],
            'colorbar': dict(thickness=20, ticklen=3),
            'colorscale': 'Geyser',
            'autocolorscale': False,
            'showscale': False,
        },
        ],
        "layout": dict(
            autoscale = True,
            height=550,
            titlefont=dict(size='14'),
            margin=dict(
                l=0,
                r=0,
                b=0,
                t=0
            ),
            hovermode="closest",
            mapbox=dict(
                accesstoken=mapbox_access_token,
                style='mapbox://styles/mapbox/light-v10',
                center=dict(
                    lon=lon,
                    lat=lat,
                ),
                zoom=zoom,
            )
        ),
    }

def map_selection(data):
    aux = data
    zoom = 1
    return gen_map(aux,zoom,41.89193,12.51133)

def draw_singleCountry_Scatter(df_confirmed_t, df_deaths_t, variable, graph_line, selected_country):
    fig = go.Figure()
    if variable == 'confirmed':
        label_max, text_label_max = ticks_log(df_confirmed_t, selected_country)
        for country in selected_country:
            try:
                ISO_legend = ISO['alpha-3'].loc[ISO['name'] == country].to_list()[0]
            except:
                ISO_legend = country
            if graph_line == 'Log':
                y = df_confirmed_t.loc[df_confirmed_t[country] >= 1].copy()
                x = [x for x in range(len(y))]
                fig.add_trace(go.Scatter(x =  x, y = y[country],
                                    mode='lines+markers',
                                    name=ISO_legend,
                                    line=dict(width=3), marker = dict(size = 3, line = dict(width = 1,color = 'DarkSlateGrey')), hoverinfo = "text",
                                    hovertext = [f"Country/Region: {country}, ({ISO_legend}) <br>Confirmed: {y.iloc[indice][country]:,} <br>Days: {x[indice]}" for indice in range(len(y))]))
                fig.update_yaxes(tickvals = label_max, ticktext = text_label_max)
            else:
                x = df_confirmed_t.index
                fig.add_trace(go.Scatter(x =  x, y = df_confirmed_t[country],
                                    mode='lines+markers',
                                    name=ISO_legend,
                                    line=dict(width=3), marker = dict(size = 3, line = dict(width = 1,color = 'DarkSlateGrey')), hoverinfo = "text",
                                    hovertext = [f"Country/Region: {country}, ({ISO_legend}) <br>Confirmed: {df_confirmed_t.iloc[indice][country]:,} <br>Date: {str(x[indice])[:10]}" for indice in range(len(df_confirmed_t))]))
                fig.update_xaxes(tickformat = '%d %B (%a)<br>%Y')
                fig.update_yaxes(tickformat = ',')
        fig.update_layout(title= 'Total confirmed cases')
    elif variable == 'deaths':
        label_max, text_label_max = ticks_log(df_deaths_t, selected_country)
        for country in selected_country:
            try:
                ISO_legend = ISO['alpha-3'].loc[ISO['name'] == country].to_list()[0]
            except:
                ISO_legend = country
            if graph_line == 'Log':
                y = df_deaths_t.loc[df_deaths_t[country] >= 1].copy()
                x = [x for x in range(len(y))]
                fig.add_trace(go.Scatter(x =  x, y = y[country],
                                    mode='lines+markers',
                                    name=ISO_legend,
                                    line=dict(width=3), marker = dict(size = 3, line = dict(width = 1,color = 'DarkSlateGrey')), hoverinfo = "text",
                                    hovertext = [f"Country/Region: {country}, ({ISO_legend}) <br>Deaths: {y.iloc[indice][country]:,} <br>Days: {x[indice]}" for indice in range(len(y))]))
                fig.update_yaxes(tickvals = label_max, ticktext = text_label_max)
            else:
                x = df_deaths_t.index
                fig.add_trace(go.Scatter(x =  x, y = df_deaths_t[country],
                                    mode='lines+markers',
                                    name=ISO_legend,
                                    line=dict(width=3), marker = dict(size = 3, line = dict(width = 1,color = 'DarkSlateGrey')), hoverinfo = "text",
                                    hovertext = [f"Country/Region: {country}, ({ISO_legend}) <br>Deaths: {df_deaths_t.iloc[indice][country]:,} <br>Date: {str(x[indice])[:10]}" for indice in range(len(df_deaths_t))]))
                fig.update_xaxes(tickformat = '%d %B (%a)<br>%Y')
                fig.update_yaxes(tickformat = ',')
        fig.update_layout(title= 'Total deaths')

    fig.update_layout(
        hovermode='closest',
        legend=dict(
            traceorder="normal",
            font=dict(
                family="sans-serif",
                size=12,
            ),
            borderwidth=0,
            #x=0,
            #y=-0.4,
            #orientation="h"
        ),
        margin=dict(l=0, r=0, t=65, b=0),
        #height=350,
        yaxis = {'type': 'linear' if graph_line == 'Linear' else 'log'},
        plot_bgcolor = "white",
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
    fig.update_yaxes(zeroline=True, zerolinewidth=2, zerolinecolor='black')

    return fig

def draw_mortality_fatality(df_confirmed_t, df_deaths_t, pop_t, variable, x_graph, selected_country):
    fig = go.Figure()
    if x_graph == 'Date':
        if variable == 'Mortality rate':
            for country in selected_country:
                try:
                    ISO_legend = ISO['alpha-3'].loc[ISO['name'] == country].to_list()[0]
                except:
                    ISO_legend = country
                y = (df_deaths_t[country])/(pop_t[country][0]).copy()
                fig.add_trace(go.Scatter(x =  df_deaths_t.index, y = y,
                                        mode='lines+markers',
                                        name=ISO_legend,
                                        line=dict(width=3), marker = dict(size = 3, line = dict(width = 1,color = 'DarkSlateGrey')), hoverinfo = "text",
                                        hovertext = [f"Country/Region: {country}, ({ISO_legend}) <br>Mortality rate: {y.iloc[indice]*100:.4f}% <br>Deaths: {df_deaths_t.iloc[indice][country]:,} <br>Date: {df_deaths_t.reset_index().iloc[indice]['index'].date()}" for indice in range(len(df_deaths_t))]))
                fig.update_layout(title= 'Mortality rate', yaxis = {'tickformat': '.4%'})
        elif variable == 'Share of infected population':
            for country in selected_country:
                try:
                    ISO_legend = ISO['alpha-3'].loc[ISO['name'] == country].to_list()[0]
                except:
                    ISO_legend = country
                y = (df_confirmed_t[country]/pop_t[country][0]).copy()
                fig.add_trace(go.Scatter(x =  df_confirmed_t.index, y = y,
                                        mode='lines+markers',
                                        name=ISO_legend,
                                        line=dict(width=3), marker = dict(size = 3, line = dict(width = 1,color = 'DarkSlateGrey')), hoverinfo = "text",
                                        hovertext = [f"Country/Region: {country}, ({ISO_legend}) <br>Share of infected population: {y.iloc[indice]*100:.2f}% <br>Confirmed: {df_confirmed_t.iloc[indice][country]:,} <br>Population: {pop_t[country][0]:,} <br>Date: {df_confirmed_t.reset_index().iloc[indice]['index'].date()}" for indice in range(len(df_confirmed_t))]))
            fig.update_layout(title= 'Share of infected population', yaxis = {'tickformat': '.2%'})
        elif variable == 'Growth rate confirmed cases':
            df_confirmed_GR = growth_rate(df_confirmed_t, 4)
            for country in selected_country:
                try:
                    ISO_legend = ISO['alpha-3'].loc[ISO['name'] == country].to_list()[0]
                except:
                    ISO_legend = country
                fig.add_trace(go.Scatter(x =  df_confirmed_GR.index, y = df_confirmed_GR[country],
                                        mode='lines+markers',
                                        name=ISO_legend,
                                        line=dict(width=3), marker = dict(size = 3, line = dict(width = 1,color = 'DarkSlateGrey')), connectgaps = True, hoverinfo = "text",
                                        hovertext = [f"Country/Region: {country}, ({ISO_legend}) <br>Growth rate confirmed cases: {df_confirmed_GR.iloc[indice][country]*100:.2f}% <br>Confirmed: {df_confirmed_t.iloc[indice][country]:,} <br>Date: {df_confirmed_t.reset_index().iloc[indice]['index'].date()}" for indice in range(len(df_confirmed_t))]))
            fig.update_layout(title= 'Growth rate confirmed cases (3-day MA)', yaxis = {'tickformat': '.2%'})
        elif variable == 'Growth rate deaths':
            df_deaths_GR = growth_rate(df_deaths_t, 4)
            for country in selected_country:
                try:
                    ISO_legend = ISO['alpha-3'].loc[ISO['name'] == country].to_list()[0]
                except:
                    ISO_legend = country
                fig.add_trace(go.Scatter(x =  df_deaths_GR.index, y = df_deaths_GR[country],
                                        mode='lines+markers',
                                        name=ISO_legend,
                                        line=dict(width=3), marker = dict(size = 3, line = dict(width = 1,color = 'DarkSlateGrey')), hoverinfo = "text",
                                        hovertext = [f"Country/Region: {country}, ({ISO_legend}) <br>Growth rate deaths: {df_deaths_GR.iloc[indice][country]*100:.2f}% <br>Deaths: {df_deaths_t.iloc[indice][country]:,} <br>Date: {df_deaths_t.reset_index().iloc[indice]['index'].date()}" for indice in range(len(df_deaths_t))], connectgaps = True))
            fig.update_layout(title= 'Growth rate deaths (3-day MA)', yaxis = {'tickformat': '.2%'})
        fig.update_xaxes(tickformat = '%d %B (%a)<br>%Y')
    elif x_graph == 'Days':
        if variable == 'Mortality rate':
            for country in selected_country:
                try:
                    ISO_legend = ISO['alpha-3'].loc[ISO['name'] == country].to_list()[0]
                except:
                    ISO_legend = country
                temp_deaths = df_deaths_t.loc[df_deaths_t[country] >= 1].copy()
                y = (temp_deaths[country])/(pop_t[country][0])
                x = [x for x in range(len(y))]
                fig.add_trace(go.Scatter(x =  x, y = y,
                                        mode='lines+markers',
                                        name=ISO_legend,
                                        line=dict(width=3), marker = dict(size = 3, line = dict(width = 1,color = 'DarkSlateGrey')), hoverinfo = "text",
                                        hovertext = [f"Country/Region: {country}, ({ISO_legend}) <br>Mortality rate: {y.iloc[indice]*100:.4f}% <br>Deaths: {temp_deaths.iloc[indice][country]:,} <br>Date: {temp_deaths.reset_index().iloc[indice]['index'].date()} <br>Days: {x[indice]}" for indice in range(len(temp_deaths))]))
            fig.update_layout(title= 'Mortality rate', yaxis = {'tickformat': '.4%'})
        elif variable == 'Share of infected population':
            for country in selected_country:
                try:
                    ISO_legend = ISO['alpha-3'].loc[ISO['name'] == country].to_list()[0]
                except:
                    ISO_legend = country
                temp_confirmed = df_confirmed_t.loc[df_confirmed_t[country] >= 1].copy()
                y = (temp_confirmed[country]/pop_t[country][0])
                x = [x for x in range(len(temp_confirmed))]
                fig.add_trace(go.Scatter(x =  x, y = y,
                                        mode='lines+markers',
                                        name=ISO_legend,
                                        line=dict(width=3), marker = dict(size = 3, line = dict(width = 1,color = 'DarkSlateGrey')), hoverinfo = "text",
                                        hovertext = [f"Country/Region: {country}, ({ISO_legend}) <br>Share of infected population: {y.iloc[indice]*100:.2f}% <br>Confirmed: {temp_confirmed.iloc[indice][country]:,} <br>Population: {pop_t[country][0]:,} <br>Date: {temp_confirmed.reset_index().iloc[indice]['index'].date()} <br>Days: {x[indice]}" for indice in range(len(temp_confirmed))]))
            fig.update_layout(title= 'Share of infected population', yaxis = {'tickformat': '.2%'})
        elif variable == 'Growth rate confirmed cases':
            for country in selected_country:
                try:
                    ISO_legend = ISO['alpha-3'].loc[ISO['name'] == country].to_list()[0]
                except:
                    ISO_legend = country
                temp_confirmed = df_confirmed_t.loc[df_confirmed_t[country] >= 1].copy()
                df_confirmed_GR = growth_rate(temp_confirmed, 4)
                x = [x for x in range(len(df_confirmed_GR))]
                fig.add_trace(go.Scatter(x =  x, y = df_confirmed_GR[country],
                                        mode='lines+markers',
                                        name=ISO_legend,
                                        line=dict(width=3), marker = dict(size = 3, line = dict(width = 1,color = 'DarkSlateGrey')), hoverinfo = "text",
                                        hovertext = [f"Country/Region: {country}, ({ISO_legend}) <br>Growth rate confirmed cases: {df_confirmed_GR.iloc[indice][country]*100:.2f}% <br>Confirmed: {temp_confirmed.iloc[indice][country]:,} <br>Date: {temp_confirmed.reset_index().iloc[indice]['index'].date()} <br>Days: {x[indice]}" for indice in range(len(temp_confirmed))], connectgaps = True))
            fig.update_layout(title= 'Growth rate confirmed cases (3-day MA)', yaxis = {'tickformat': '.2%'})
        elif variable == 'Growth rate deaths':
            for country in selected_country:
                try:
                    ISO_legend = ISO['alpha-3'].loc[ISO['name'] == country].to_list()[0]
                except:
                    ISO_legend = country
                temp_deaths = df_deaths_t.loc[df_deaths_t[country] >= 1].copy()
                df_deaths_GR = growth_rate(temp_deaths, 4)
                x = [x for x in range(len(df_deaths_GR))]
                fig.add_trace(go.Scatter(x =  x, y = df_deaths_GR[country],
                                        mode='lines+markers',
                                        name=ISO_legend,
                                        line=dict(width=3), marker = dict(size = 3, line = dict(width = 1,color = 'DarkSlateGrey')), hoverinfo = "text",
                                        hovertext = [f"Country/Region: {country}, ({ISO_legend}) <br>Growth rate deaths: {df_deaths_GR.iloc[indice][country]*100:.2f}% <br>Deaths: {temp_deaths.iloc[indice][country]:,} <br>Date: {temp_deaths.reset_index().iloc[indice]['index'].date()} <br>Days: {x[indice]}" for indice in range(len(temp_deaths))], connectgaps = True))
            fig.update_layout(title= 'Growth rate deaths (3-day MA)', yaxis = {'tickformat': '.2%'})

    fig.update_layout(
        hovermode='closest',
        legend=dict(
            traceorder="normal",
            font=dict(
                family="sans-serif",
                size=12,
            ),
            borderwidth=0,
            #x=0,
            #y=-0.4,
            #orientation="h"
        ),
        plot_bgcolor='white',
        margin=dict(l=0, r=0, t=65, b=0),
        #height=350
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
    fig.update_yaxes(zeroline=True, zerolinewidth=2, zerolinecolor='black')

    return fig

def draw_singleCountry_Epicurve(df_confirmed_t, df_deaths_t, df_policy_index, df_epic_confirmed, df_epic_days_confirmed, df_epic_deaths, df_epic_days_deaths, variable, plot, selected_country):
    fig = go.Figure()
    if plot == 'Epidemic curves':
        if variable == 'confirmed':
            for country in selected_country:
                try:
                    ISO_legend = ISO['alpha-3'].loc[ISO['name'] == country].to_list()[0]
                except:
                    ISO_legend = country
                fig.add_trace(go.Scatter(x =  df_epic_days_confirmed[country], y = df_epic_confirmed[country],
                                    mode='lines+markers',
                                    name=ISO_legend,
                                    line=dict(width=3), marker = dict(size = 3, line = dict(width = 1,color = 'DarkSlateGrey')), connectgaps = True, hoverinfo = "text",
                                    hovertext = [f"Country/Region: {country} <br>Confirmed: {df_confirmed_t.iloc[indice][country]:,} <br>Pct. of total cases (3-day MA): {np.exp(df_epic_confirmed.iloc[indice][country]):.3f}% <br>Days: {df_epic_days_confirmed.iloc[indice][country]} <br>Date: {df_epic_confirmed.reset_index().iloc[indice]['index'].date()}" for indice in range(len(df_confirmed_t))]))
            fig.update_layout(title = 'Epidemic curve confirmed cases')
            fig.update_yaxes(tickvals = [-6.9, -4.6, -2.3, 0, 2.30258], ticktext = [f'{np.exp(-6.9):.3f}%', f'{np.exp(-4.6):.3f}%', f'{np.exp(-2.3):.3f}%', f'{np.exp(0):.3f}%', f'{np.exp(2.30258):.3f}%'])
        else:
            for country in selected_country:
                try:
                    ISO_legend = ISO['alpha-3'].loc[ISO['name'] == country].to_list()[0]
                except:
                    ISO_legend = country
                fig.add_trace(go.Scatter(x =  df_epic_days_deaths[country], y = df_epic_deaths[country],
                                    mode='lines+markers',
                                    name=ISO_legend,
                                    line=dict(width=3), marker = dict(size = 3, line = dict(width = 1,color = 'DarkSlateGrey')), connectgaps = True, hoverinfo = "text",
                                    hovertext = [f"Country/Region: {country} <br>Deaths: {df_deaths_t.iloc[indice][country]:,} <br>Pct. of deaths (3-day MA): {np.exp(df_epic_deaths.iloc[indice][country]):.3f}% <br>Days: {df_epic_days_deaths.iloc[indice][country]} <br>Date: {df_epic_deaths.reset_index().iloc[indice]['index'].date()}" for indice in range(len(df_confirmed_t))]))
            fig.update_layout(title= 'Epidemic curve deaths')
            fig.update_yaxes(tickvals = [-6.9, -4.6, -2.3, 0, 2.30258], ticktext = [f'{np.exp(-6.9):.3f}%', f'{np.exp(-4.6):.3f}%', f'{np.exp(-2.3):.3f}%', f'{np.exp(0):.3f}%', f'{np.exp(2.30258):.3f}%'])
    if plot == 'Stringency index':
        if variable == 'confirmed':
            label_max, text_label_max = ticks_log(df_confirmed_t, selected_country)
            for country in selected_country:
                try:
                    ISO_legend = ISO['alpha-3'].loc[ISO['name'] == country].to_list()[0]
                except:
                    ISO_legend = country
                fig.add_trace(go.Scatter(x =  df_confirmed_t[country], y = df_policy_index[country],
                                    mode='lines+markers',
                                    name=ISO_legend,
                                    line=dict(width=3), marker = dict(size = 3, line = dict(width = 1,color = 'DarkSlateGrey')), hoverinfo = "text",
                                    hovertext = [f"Country/Region: {country} <br>Confirmed: {df_confirmed_t.iloc[indice][country]:,} <br>Stringency index: {df_policy_index.iloc[indice][country]:,} <br>Date: {df_confirmed_t.reset_index().iloc[indice]['index'].date()}" for indice in range(len(df_confirmed_t))]))
            fig.update_layout(title= 'Stringency index confirmed cases', xaxis = {'type': 'log'})
            fig.update_xaxes(tickvals = label_max, ticktext = text_label_max)
        else:
            label_max, text_label_max = ticks_log(df_deaths_t, selected_country)
            for country in selected_country:
                try:
                    ISO_legend = ISO['alpha-3'].loc[ISO['name'] == country].to_list()[0]
                except:
                    ISO_legend = country
                fig.add_trace(go.Scatter(x =  df_deaths_t[country], y = df_policy_index[country],
                                    mode='lines+markers',
                                    name=ISO_legend,
                                    line=dict(width=3), marker = dict(size = 3, line = dict(width = 1,color = 'DarkSlateGrey')), hoverinfo = "text",
                                    hovertext = [f"Country/Region: {country} <br>Deaths: {df_deaths_t.iloc[indice][country]:,}  <br>Stringency index: {df_policy_index.iloc[indice][country]:,} <br>Date: {df_deaths_t.reset_index().iloc[indice]['index'].date()}" for indice in range(len(df_deaths_t))]))
            fig.update_layout(title= 'Stringency index deaths', xaxis = {'type': 'log'})
            fig.update_xaxes(tickvals = label_max, ticktext = text_label_max)

    fig.update_layout(
        hovermode='closest',
        legend=dict(
            traceorder="normal",
            font=dict(
                family="sans-serif",
                size=12,
            ),
            borderwidth=0,
            #x=0,
            #y=-0.4,
            #orientation="h"
        ),
        plot_bgcolor = 'white',
        margin=dict(l=0, r=0, t=65, b=0),
        #height=350
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
    fig.update_yaxes(zeroline=True, zerolinewidth=2, zerolinecolor='black')

    return fig

tab_confirmed_left = dbc.Card(
    html.Div([
        html.Ul([
            html.Li([
                html.Div([
                    html.H5([
                        dbc.ListGroupItem([f'{country}, {df_left_list_confirmed_t[country]:,}'], className="border-top-0 border-left-0 border-right-0") for country in df_left_list_confirmed_t.index
                    ],
                    ),
                ],
                className='media-body border-0'
                ),
            ],
            className='media border-0'
            ),   
        ],
        className='list-unstyled'
        ),
    ],
    style={ "height": "600px" },
    className="overflow-auto"
    ),
className="border-0",
)

tab_deaths_left = dbc.Card(
    html.Div([
        html.Ul([
            html.Li([
                html.Div([
                    html.H5([
                        dbc.ListGroupItem([f'{country}, {df_left_list_deaths_t[country]:,}'], className="border-top-0 border-left-0 border-right-0") for country in df_left_list_deaths_t.index
                    ],
                    ),
                ],
                className='media-body border-0'
                ),
            ],
            className='media border-0'
            ),   
        ],
        className='list-unstyled'
        ),
    ],
    style={ "height": "600px" },
    className="overflow-auto"
    ),
className="border-0",
)

tab_confirmed_increase_left = dbc.Card(
    html.Div([
        html.Ul([
            html.Li([
                html.Div([
                    html.H5([
                        dbc.ListGroupItem([f'{country}, {df_left_list_daily_confirmed_increase.iloc[0][country]:,}'], className="border-top-0 border-left-0 border-right-0") for country in list(df_left_list_daily_confirmed_increase)
                    ],
                    ),
                ],
                className='media-body border-0'
                ),
            ],
            className='media border-0'
            ),   
        ],
        className='list-unstyled'
        ),
    ],
    style={ "height": "600px" },
    className="overflow-auto"
    ),
className="border-0",
)

tab_deaths_increase_left = dbc.Card(
    html.Div([
        html.Ul([
            html.Li([
                html.Div([
                    html.H5([
                        dbc.ListGroupItem([f'{country}, {df_left_list_daily_deaths_increase.iloc[0][country]:,}'], className="border-top-0 border-left-0 border-right-0") for country in list(df_left_list_daily_deaths_increase)
                    ],
                    ),
                ],
                className='media-body border-0'
                ),
            ],
            className='media border-0'
            ),   
        ],
        className='list-unstyled'
        ),
    ],
    style={ "height": "600px" },
    className="overflow-auto"
    ),
className="border-0",
)

tab_right = dbc.Card(id ='selected-countries-tab')

markdown_data_info = dcc.Markdown('''
The dashboard is updated daily following new daily releases of data from the data sources listed below.

**Data source daily updated:**
* Policy measures from [Oxford COVID-19 Government Response Tracker](https://www.bsg.ox.ac.uk/research/research-projects/oxford-covid-19-government-response-tracker).
* Data on confirmed cases and deaths from the [GitHub repository of the Johns Hopkins University](https://github.com/CSSEGISandData/COVID-19)

**Other data:**
* Geojson for countries in the world from [https://github.com/datasets/geo-countries/blob/master/data/countries.geojson](https://github.com/datasets/geo-countries/blob/master/data/countries.geojson).
* Country population data from [UN](https://population.un.org/wpp/Download/Standard/CSV).
* Countries' ISO codes from [https://raw.githubusercontent.com/lukes/ISO-3166-Countries-with-Regional-Codes/master/all/all.csv](https://raw.githubusercontent.com/lukes/ISO-3166-Countries-with-Regional-Codes/master/all/all.csv).
''')

markdown_relevant_info = dcc.Markdown('''
This dashboard is part of a larger set of dashboards available on our website. In particular, here we focus on the global COVID-19 pandemic.

Our dashboard focusing on Belgium can be found here.

Articles reporting daily information on COVID-19 are available here.
''')

############################
# Bootstrap Grid Layout
############################

app.layout = html.Div([ #Main Container   
    #Header TITLE
    html.Div([
        #Info Modal Button LEFT
        dbc.Button("Relevant info", id="open-centered-left", className="btn-sm"),
        dbc.Modal(
            [
                dbc.ModalHeader("Relevant information"),
                dbc.ModalBody(children = markdown_relevant_info),
                dbc.ModalFooter(
                    dbc.Button(
                        "Close", id="close-centered-left", className="ml-auto"
                    )
                ),
            ],
            id="modal-centered-left",
            centered=True,
        ),
        #H1 Title
        html.H1(
            children='COVID-19 Dashboard',
            className="text-center",
        ),
        #Info Modal Button RIGHT
        dbc.Button("Datasets info", id="open-centered-right", className="btn-sm"),
        dbc.Modal(
            [
                dbc.ModalHeader("Information on datasets used"),
                dbc.ModalBody(children = markdown_data_info),
                dbc.ModalFooter(
                    dbc.Button(
                        "Close", id="close-centered-right", className="ml-auto"
                    )
                ),
            ],
            id="modal-centered-right",
            centered=True,
        ),
    ],
    className="d-flex justify-content-md-between my-2"
    ),
    
    #First Row CARDS 3333
    html.Div([
        html.Div([
            #Card 1
            html.Div([
                # Card 1 body
                html.Div([
                    html.H4(
                        children='Global Cases: ',
                        className='card-title'
                    ),
                    html.H4(f"{df_world.iloc[0, -1]:,d}",
                        className='card-text'
                    ),
                    html.P('New daily confirmed cases: ' + f"{daily_confirmed_world:,d}",
                        className='card-text'
                    ),
                ],
                className="card-body"
                )
            ],
            className='card my-2 text-center shadow'
            ),
        ],
        className="col-md-3"
        ),
        html.Div([
            #Card 2
            html.Div([
                # Card 2 body
                html.Div([
                    html.H4(
                        children='Global Deaths: ',
                        className='card-title'
                    ),
                    html.H4(f"{df_world.iloc[1, -1]:,d}",
                        className='card-text'
                    ),
                    html.P('New daily confirmed deaths: ' + f"{daily_deaths_world:,d}",
                        className='card-text'
                    ),
                ],
                className="card-body"
                )
            ],
            className='card my-2 text-center shadow'
            ),
        ],
        className="col-md-3"
        ),
        html.Div([
            #Card 3
            html.Div([
                # Card 3 body
                html.Div([
                    html.H4(
                        children='EU28 Cases: ',
                        className='card-title'
                    ),
                    html.H4(f"{df_EU28.iloc[0, -1]:,d}",
                        className='card-text'
                    ),
                    html.P('New daily confirmed cases: ' + f"{daily_confirmed_EU28:,d}",
                        className='card-text'
                    ),
                ],
                className="card-body"
                )
            ],
            className='card my-2 text-center shadow'
            ),
        ],
        className="col-md-3"
        ),        
        html.Div([
            #Card 4
            html.Div([
                # Card 4 body
                html.Div([
                    html.H4(
                        children='EU28 Deaths: ',
                        className='card-title'
                    ),
                    html.H4(f"{df_EU28.iloc[1, -1]:,d}",
                        className='card-text'
                    ),
                    html.P('New daily confirmed deaths: ' + f"{daily_deaths_EU28:,d}",
                        className='card-text'
                    ),
                ],
                className="card-body"
                )
            ],
            className='card my-2 text-center shadow'
            ),
        ],
        className="col-md-3"
        ),
    ],
    className="row"
    ),

    #Second Row 363
    html.Div([

        #Col6 Middle
        html.Div([
            #Map, Title
            html.Div([
                html.H3(
                    children='World Map',
                    style={},
                    className='text-center'
                ),
                html.P(
                    children='by number of confirmed cases',
                    style={},
                    className='text-center'
                ),
            ],
            className='my-2 mx-auto'
            ),
            #Map, Table
            html.Div([
                html.Div([
                    dcc.Graph(id='global_map', figure = map_selection(map_data))
                ],
                className='',
                id="worldMap",
                ),
            ],
            className='my-2 shadow'
            ),
            #Country select Dropdown
            html.Div([
                html.Div([
                    html.Div([
                        dbc.Button("World Map", href="#worldMap", external_link=True),
                        dbc.Button("World Stats", href="#worldStats", external_link=True),
                        dbc.Button("Countries Stats", href="#countriesStats", external_link=True),
                    ],
                    className='text-center d-md-none'                        
                    ),
                    html.H4(
                        children='Add or remove countries to compare',
                        style={},
                        className='text-center my-2'
                    ),
                    dcc.Dropdown(
                        id='demo-dropdown',
                        options=[{'label': i, 'value': i} for i in available_indicators],
                        multi=True,
                        value = top_4,
                        placeholder = 'Select countries to plot - Default to top 4 countries by confirmed cases'
                    ),
                ],
                className='card-body pt-1 pb-0'
                ),
            ],
            className='card my-2 shadow sticky-top'
            ),
            html.Div([
                html.Div([
                    dbc.Label("Select a scale:", html_for="graph-line"),
                    dbc.RadioItems(
                            id='graph-line',
                            options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                            value='Linear',
                            labelStyle={},
                            className='',
                            inline=True
                    ),
                    dbc.Tooltip(children = [
                        html.P([
                            "Switch between linear and logarithmic scale for the plots reporting the number of confirmed cases and deaths for each selected country."
                        ],),
                        html.P([
                            "When displaying the logarithmic scale, the horizontal axis reports the count from the day of the first confirmed case (or death)."
                        ],),],
                        target="graph-line",
                        style= {'opacity': '0.8'}
                    ),
                ],
                className='card-body text-center'
                ),
            ],
            className='card my-2 shadow'
            ),
            #Line Graph Confirmed
            html.Div([
                html.Div([
                    dcc.Graph(id='line-graph-confirmed',)
                ],
                className='p-1'
                ),
            ],
            className='card my-2 shadow'
            ),
            #Line Graph Deaths
            html.Div([
                html.Div([
                    dcc.Graph(id='line-graph-deaths',)
                ],
                className='p-1'
                ),
            ],
            style={},
            className='card my-2 shadow'
            ),
            #Variable Dropdown Epicurve / Policy
            html.Div([
                html.H4(
                    children='Epidemic curve and policy index',
                    style={"textDecoration": "underline", "cursor": "pointer"},
                    className='text-center my-2',
                    id = 'epidemic_and_policy_variables'
                ),
                dbc.Tooltip(children = [
                    html.P([
                        'Epidemic curve: Reports the fraction of cases or deaths out of the total numbers up until today. For each selected country the date with the largest fraction of new registered cases or deaths is considered as day 0, defined also as the "turning point".'
                    ],),
                    html.P([
                        "Stringency Index: This index ranges between 0 (no policy) to 100 (maximum measures) and combines 13 indicators of government responses, including school closures, travel bans, and fiscal or monetary measures."
                    ],),],
                    target="epidemic_and_policy_variables",
                    style= {'opacity': '0.8'}
                ),
                html.Div([
                    dcc.Dropdown(
                        id='variable-dropdown-epic',
                        options=[{'label': i, 'value': i} for i in ['Epidemic curves', 'Stringency index']],
                        multi=False,
                        value = 'Epidemic curves',
                    ),
                ],
                className="card-body text-center"
                )
            ],
            className='card my-2 shadow'
            ),
            #Line Graph Epidemic curves
            html.Div([
                html.Div([
                    dcc.Graph(id='line-graph-epicurve',)
                ],
                className='p-1'
                ),
            ],
            className='card my-2 shadow'
            ),
            #Line Graph Policy
            html.Div([
                html.Div([
                    dcc.Graph(id='line-graph-policy',)
                ],
                className='p-1'
                ),
            ],
            style={},
            className='card my-2 shadow'
            ),
            #Variable Dropdown Fatality
            html.Div([
                html.H4(
                    children='Other relevant statistics',
                    style={"textDecoration": "underline", "cursor": "pointer"},
                    className='text-center my-2',
                    id = 'other_variables_tooltip'
                ),
                dbc.Tooltip(children = [
                    html.P([
                        "Mortality rate: Share of deaths out of population in 2019 for each selected country."
                    ],),
                    html.P([
                        "Share of infected population: Share of confirmed cases out of population in 2019 for each selected country."
                    ],),
                    html.P([
                        "Growth rate confirmed cases (deaths): Day-to-day percentage changes in confirmed cases or deaths. We take a 3-day simple moving average to account for fluctuations."
                    ],),],
                target="other_variables_tooltip",
                style= {'opacity': '0.8'}
                ),
                html.Div([
                    dbc.RadioItems(
                        id='x-var',
                        options=[{'label': i, 'value': i} for i in ['Date', 'Days']],
                        value='Date',
                        labelStyle={},
                        inline=True,
                        className='mb-1',
                        style = {}
                    ),
                    dbc.Tooltip(children = [
                        html.P([
                            "Date: Use calendar days as horizonal axis. This is the default choice."
                        ],),
                        html.P([
                            "Days: Sets the horizonal axis to be the count from the day of the first confirmed case (or death) for each selected country."
                        ],),],
                        target="x-var",
                        style= {'opacity': '0.8'}
                    ),
                    dcc.Dropdown(
                        id='variable-dropdown',
                        options=[{'label': i, 'value': i} for i in available_variables],
                        multi=False,
                        value = 'Mortality rate',
                        className='',
                        style = {}
                    ), 
                ],
                className ='card-body text-center'
                ),
            ],
            className='card my-2 shadow'
            ),
            #Line Graph Multiple
            html.Div([
                html.Div([
                    dcc.Graph(id='line-graph-multiple',)
                ],
                className='p-1'
                ),
            ],
            style={},
            className='card my-2 shadow'
            ),
        ],
        className="col-md-6 order-md-2"
        ),

        #Col2 Left
        html.Div([
            html.Div([
                dbc.Tabs([
                    dbc.Tab(tab_confirmed_left, label="Cases"),
                    dbc.Tab(tab_deaths_left, label="Deaths"),
                    dbc.Tab(tab_confirmed_increase_left, label="New cas."),
                    dbc.Tab(tab_deaths_increase_left, label="New dea.")
                ],
                className="nav-justified"
                )
            ],
            className="card my-2 shadow",
            id="worldStats",
            )
        ],
        className="col-md-3 order-md-1"
        ),

        #Col2 Right
        html.Div([
            html.Div([
                dbc.Tabs([
                    dbc.Tab(tab_right, label="Country statistics(*)"),
                ],
                className="nav-justified",
                id = 'info_tab_right'
                )
            ],
            className="card my-2 shadow",
            id="countriesStats",
            ),
            dbc.Tooltip(children = [
                html.P([
                    "This tab shows a set of statistics for the countries selected in the dropdown menu."
                ],),
                html.P([
                    "All the reported statistics are updated to the current day."
                ],),],
                target="info_tab_right",
                style= {'opacity': '0.8'}
            ),
        ],
        className="col-md-3 order-md-3",
        ),
        
    ],
    className="row"
    ),

    #Bottom fixed NavBar
    #nav,

],
className="container-fluid"
)

@app.callback(
    [Output('line-graph-confirmed', 'figure'),
    Output('line-graph-deaths', 'figure'),
    Output('line-graph-multiple', 'figure'),
    Output('line-graph-epicurve', 'figure'),
    Output('line-graph-policy', 'figure')],
    [Input('demo-dropdown', 'value'),
    Input('graph-line', 'value'),
    Input('x-var', 'value'),
    Input('variable-dropdown', 'value'),
    Input('variable-dropdown-epic', 'value')])
def line_selection(dropdown, graph_line, x_choice, variable, plots_epic_policy):
    if len(dropdown) == 0:
        for country in top_4:
            dropdown.append(country)
    fig1 = draw_singleCountry_Scatter(df_confirmed_t, df_deaths_t, 'confirmed', graph_line, selected_country = dropdown)
    fig2 = draw_singleCountry_Scatter(df_confirmed_t, df_deaths_t, 'deaths', graph_line, selected_country = dropdown)
    fig3 = draw_mortality_fatality(df_confirmed_t, df_deaths_t, pop_t, variable = variable, x_graph = x_choice, selected_country = dropdown)
    fig4 = draw_singleCountry_Epicurve(df_confirmed_t, df_deaths_t, df_policy_index, df_epic_confirmed, df_epic_days_confirmed, df_epic_deaths, df_epic_days_deaths, 'confirmed', plot = plots_epic_policy, selected_country = dropdown)
    fig5 = draw_singleCountry_Epicurve(df_confirmed_t, df_deaths_t, df_policy_index, df_epic_confirmed, df_epic_days_confirmed, df_epic_deaths, df_epic_days_deaths, 'deaths', plot = plots_epic_policy, selected_country = dropdown)
    return fig1, fig2, fig3, fig4, fig5


@app.callback(
    Output('selected-countries-tab', 'children'),
    [Input('demo-dropdown', 'value')])
def tab_right_countries(dropdown):
    newline = '\n'
    if len(dropdown) == 0:
        for country in top_4:
            dropdown.append(country)
    return html.Div([
        html.Ul([
            html.Li([
                html.Div([
                        dbc.ListGroupItem([
                            dbc.ListGroupItemHeading(f'{country}:'),
                            dbc.ListGroupItemText(f'Confirmed cases: {df_tab_right.iloc[0][country]:,}', color = 'info'),
                            dbc.ListGroupItemText(f'Deaths: {df_tab_right.iloc[1][country]:,}', color = 'danger'),
                            dbc.ListGroupItemText(f'Mortality rate: {df_tab_right.iloc[2][country]*100:.2f}%', color = 'warning'),
                            dbc.ListGroupItemText(f'Share of infected population: {df_tab_right.iloc[3][country]*100:.2f}%', color = 'warning'),
                            dbc.ListGroupItemText(f'Share out of global confirmed cases: {df_tab_right.iloc[4][country]*100:.4f}%', color = 'info'),
                            dbc.ListGroupItemText(f'Share out of global deaths: {df_tab_right.iloc[5][country]*100:.4f}%', color = 'danger'),
                            dbc.ListGroupItemText(f'Date of 1st confirmed case: {df_tab_right.iloc[6][country]}', color = 'info'),
                            dbc.ListGroupItemText(f'Date of 1st confirmed death: {df_tab_right.iloc[7][country]}', color = 'danger'),
                            dbc.ListGroupItemText(f'Stringency Index: {df_tab_right.iloc[8][country]}', color = 'success'),
                            dbc.ListGroupItemText(f'Population in 2019: {df_tab_right.iloc[9][country]:,}', color = 'success'),], className="border-top-0 border-left-0 border-right-0") for country in dropdown
                ],
                className='media-body border-0'
                ),
            ],
            className='media border-0'
            ),   
        ],
        className='list-unstyled'
        ),
    ],
    style={ "height": "600px" },
    className="overflow-auto"
    ),
    className="border-0",

@app.callback(
    Output("modal-centered-left", "is_open"),
    [Input("open-centered-left", "n_clicks"), Input("close-centered-left", "n_clicks")],
    [State("modal-centered-left", "is_open")],)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

@app.callback(
    Output("modal-centered-right", "is_open"),
    [Input("open-centered-right", "n_clicks"), Input("close-centered-right", "n_clicks")],
    [State("modal-centered-right", "is_open")],)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

if __name__ == '__main__':
    app.run_server(debug=False)
