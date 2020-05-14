import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import datetime
import json
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table as dt
import pickle
import os
from dash.dependencies import Input, Output, State
from pathlib import Path
from scout_apm.flask import ScoutApm

# Custom functions
from functions import *

path_input = Path.cwd() / 'input'
Path.mkdir(path_input, exist_ok = True)
#path_policy = Path.cwd() / 'input' / 'policy.csv'

#####################################################################################################################################
# Boostrap CSS and font awesome . Option 1) Run from codepen directly Option 2) Copy css file to assets folder and run locally
#####################################################################################################################################
external_stylesheets = [dbc.themes.FLATLY]

#Insert your javascript here. In this example, addthis.com has been added to the web app for people to share their webpage

app = dash.Dash(__name__, external_stylesheets = external_stylesheets)

app.title = 'COVID-19 - World dashboard'

app.config.suppress_callback_exceptions = True
flask_app = app.server

ScoutApm(flask_app)

flask_app.config["SCOUT_NAME"] = "COVID-19 - World dashboard"

#for heroku to run correctly
server = app.server

#############################################################################
# UNPICKLIFICATION TIME 
#############################################################################

pickle_path = Path.cwd() / 'pickles_jar'
pickles_list = [
    'df_confirmed_t',
    'df_deaths_t',
    'df_policy_index',
    'df_epic_confirmed',
    'df_epic_days_confirmed',
    'df_epic_deaths',
    'df_epic_days_deaths',
    'df_tab_right',
    'pop_t',
    'coord_df',
    'map_data',
    'df_world',
    'df_EU28',
    'df_left_list_confirmed_t',
    'df_left_list_deaths_t',
    'df_left_list_daily_confirmed_increase',
    'df_left_list_daily_deaths_increase',
    'daily_confirmed_world',
    'daily_deaths_world',
    'daily_confirmed_EU28',
    'daily_deaths_EU28',
    'top_4',
    'available_variables',
    'available_indicators',
    'ISO',
    ]
    
pickle_files = [str(pickle_path) + os.sep + x + '.pkl' for x in pickles_list]

def unpicklify(path):
    file_read = open(path, 'rb')
    dataframe = pickle.load(file_read)
    file_read.close()
    return dataframe


df_confirmed_t = unpicklify(pickle_files[0])
df_deaths_t = unpicklify(pickle_files[1])
df_policy_index = unpicklify(pickle_files[2])
df_epic_confirmed = unpicklify(pickle_files[3])
df_epic_days_confirmed = unpicklify(pickle_files[4])
df_epic_deaths = unpicklify(pickle_files[5])
df_epic_days_deaths = unpicklify(pickle_files[6])
df_tab_right = unpicklify(pickle_files[7])
pop_t = unpicklify(pickle_files[8])
coord_df = unpicklify(pickle_files[9])
map_data = unpicklify(pickle_files[10])
df_world = unpicklify(pickle_files[11])
df_EU28 = unpicklify(pickle_files[12])
df_left_list_confirmed_t = unpicklify(pickle_files[13])
df_left_list_deaths_t = unpicklify(pickle_files[14])
df_left_list_daily_confirmed_increase = unpicklify(pickle_files[15])
df_left_list_daily_deaths_increase = unpicklify(pickle_files[16])
daily_confirmed_world = unpicklify(pickle_files[17])
daily_deaths_world = unpicklify(pickle_files[18])
daily_confirmed_EU28 = unpicklify(pickle_files[19])
daily_deaths_EU28 = unpicklify(pickle_files[20])
top_4 = unpicklify(pickle_files[21])
available_variables = unpicklify(pickle_files[22])
available_indicators = unpicklify(pickle_files[23])
ISO = unpicklify(pickle_files[24])

#for pickle_file in pickle_files:
#    df = unpicklify(pickle_file)

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
                temp_confirmed = df_confirmed_t.loc[df_confirmed_t[country] > 0].copy()
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
                if df_deaths_t[country].max() == 0:
                    temp_deaths = df_deaths_t.copy()
                else:
                    temp_deaths = df_deaths_t.loc[df_deaths_t[country] > 0].copy()
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
                                    hovertext = [f"Country/Region: {country} <br>Confirmed: {df_confirmed_t.iloc[indice][country]:,} <br>ln % of total cases (3-day MA): {np.exp(df_epic_confirmed.iloc[indice][country]):.3f}% <br>Days: {df_epic_days_confirmed.iloc[indice][country]} <br>Date: {df_epic_confirmed.reset_index().iloc[indice]['index'].date()}" for indice in range(len(df_confirmed_t))]))
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
                                    hovertext = [f"Country/Region: {country} <br>Deaths: {df_deaths_t.iloc[indice][country]:,} <br>ln % of total deaths (3-day MA): {np.exp(df_epic_deaths.iloc[indice][country]):.3f}% <br>Days: {df_epic_days_deaths.iloc[indice][country]} <br>Date: {df_epic_deaths.reset_index().iloc[indice]['index'].date()}" for indice in range(len(df_confirmed_t))]))
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
    style={ "height": "275px" },
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
    style={ "height": "275px" },
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
    style={ "height": "275px" },
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
    style={ "height": "275px" },
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
We focus on this dashboard on the global COVID-19 pandemic. This dashboard is part of a larger set of dashboards available [on our website](https://www.learningfromthecurve.net/dashboards/).

Articles by members of the Learning from the Curve team reporting daily information on COVID-19 are available [here](https://www.learningfromthecurve.net/commentaries/).

Please, report any bug at the following contact address: learningfromthecurve.info@gmail.com.
''')

# Accordion countries
def make_item(available_indicators, top_4):
    return dbc.Card(
        [
            dbc.CardHeader(
                dbc.Button(
                    "Discover more",
                    color="primary",
                    id="temp_prova_accordion",
                    block = True,
                    active = True
                ),
            ),
            dbc.Collapse(
                dbc.CardBody(
                    [html.Div([
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
                    ),], className = "pt-1 pb-0"),
                id="temp_prova_collapse",
            ),
        ], className = "my-2 shadow", style = {"overflow": "visible"}
        )

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

            html.Div(
                    [make_item(available_indicators, top_4)], className="accordion sticky-top"
            ),

            #Country select Dropdown

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
                        style= {'opacity': '0.9'}
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
                        'Epidemic curve: Reports the fraction of cases or deaths out of the total numbers up until today. For each selected country the date with the largest log of the 3-day MA of percentage of total cases or deaths is considered as day 0, defined also as the "turning point".'
                    ],),
                    html.P([
                        "Stringency Index: This index ranges between 0 (no policy) to 100 (maximum measures) and combines 13 indicators of government responses, including school closures, travel bans, and fiscal or monetary measures."
                    ],),],
                    target="epidemic_and_policy_variables",
                    style= {'opacity': '0.9'}
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
                style= {'opacity': '0.9'}
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
                        style= {'opacity': '0.9'}
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
                ],
                className="nav-justified"
                ),
            ],
            className="card my-2 shadow",
            id="worldStats",
            ),
            html.Div([
                dbc.Tabs([
                    dbc.Tab(tab_confirmed_increase_left, label="Daily cases"),
                    dbc.Tab(tab_deaths_increase_left, label="Daily deaths")
                ],
                className="nav-justified"
                ),
            ],
            className="card my-2 shadow",
            id="worldStats_daily",
            )
        ],
        className="col-md-3 order-md-1"
        ),

        #Col2 Right
        html.Div([
            html.Div([
                dbc.Tabs([
                    dbc.Tab(tab_right, label="Country statistics" + u"\U0001F6C8"),
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
                style= {'opacity': '0.9'}
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
    Output('line-graph-deaths', 'figure')],
    [Input('demo-dropdown', 'value'),
    Input('graph-line', 'value')])
def line_selection(dropdown, graph_line):
    if len(dropdown) == 0:
        for country in top_4:
            dropdown.append(country)
    fig1 = draw_singleCountry_Scatter(df_confirmed_t, df_deaths_t, 'confirmed', graph_line, selected_country = dropdown)
    fig2 = draw_singleCountry_Scatter(df_confirmed_t, df_deaths_t, 'deaths', graph_line, selected_country = dropdown)
    return fig1, fig2

@app.callback(
    Output('line-graph-multiple', 'figure'),
    [Input('demo-dropdown', 'value'),
    Input('x-var', 'value'),
    Input('variable-dropdown', 'value')])
def line_selection(dropdown, x_choice, variable):
    if len(dropdown) == 0:
        for country in top_4:
            dropdown.append(country)
    fig1 = draw_mortality_fatality(df_confirmed_t, df_deaths_t, pop_t, variable = variable, x_graph = x_choice, selected_country = dropdown)
    return fig1

@app.callback(
    [Output('line-graph-epicurve', 'figure'),
    Output('line-graph-policy', 'figure')],
    [Input('demo-dropdown', 'value'),
    Input('variable-dropdown-epic', 'value')])
def line_selection(dropdown, plots_epic_policy):
    if len(dropdown) == 0:
        for country in top_4:
            dropdown.append(country)
    fig1 = draw_singleCountry_Epicurve(df_confirmed_t, df_deaths_t, df_policy_index, df_epic_confirmed, df_epic_days_confirmed, df_epic_deaths, df_epic_days_deaths, 'confirmed', plot = plots_epic_policy, selected_country = dropdown)
    fig2 = draw_singleCountry_Epicurve(df_confirmed_t, df_deaths_t, df_policy_index, df_epic_confirmed, df_epic_days_confirmed, df_epic_deaths, df_epic_days_deaths, 'deaths', plot = plots_epic_policy, selected_country = dropdown)
    return fig1, fig2


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

@app.callback(
    Output("temp_prova_collapse", "is_open"),
    [Input("temp_prova_accordion", "n_clicks"),],
    [State("temp_prova_collapse", "is_open")],)
def toggle_accordion(n1, is_open1):
    ctx = dash.callback_context
    if not ctx.triggered:
        return ""
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if button_id == "temp_prova_accordion" and n1:
        return not is_open1
    return is_open1

if __name__ == '__main__':
    app.run_server(debug=False)
