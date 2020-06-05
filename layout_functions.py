import numpy as np 
import pandas as pd
from pickle_functions import unpicklify
import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table as dt
from dash.dependencies import Input, Output, State
from app_functions import *
from pickle_functions import unpicklify
from process_functions import write_log

def list_item(opening, data, ending):
    '''
    input: 
    info data about a statistic for a country
    a string describing it
    a string of eventual text after data
    output: 
    if the data is valid returns an item, otherwise nothing
    '''
    if pd.isna(data) or data == 'None' or data == 0:
        return
    else:
        return dbc.ListGroupItemText(f'{opening}{data}{ending}')


def gen_map(map_data):
    '''
    Function to generate and plot the world map with the # of confirmed cases for each country as the Z parameter
    '''
    wrong_values= sum(n < 1 for n in list(map_data['Confirmed']))
    if wrong_values > 0:
        pass
        #write_log('***cannot compute the log of '.upper() + str(wrong_values) + 'values***')
    z_value = np.log(list(map_data['Confirmed']))
    #mapbox_access_token = 'pk.eyJ1IjoiZmVkZWdhbGwiLCJhIjoiY2s5azJwaW80MDQxeTNkcWh4bGhjeTN2NyJ9.twKWO-W5wPLX6m9OfrpZCw'
    return {
        "data": [{
            "type": "choropleth",  
            'locations' : map_data['alpha-3'],
            "z": z_value,
            "hoverinfo": "text",         
            "hovertext": [f"Country/Region: {map_data.iloc[indice]['Country/Region']} <br>Confirmed: {map_data.iloc[indice]['Confirmed']:,} <br>Deaths: {map_data.iloc[indice]['Deaths']:,}" for indice in range(len(map_data['Country/Region']))],
            'colorscale': 'Geyser',
            'autocolorscale': False,
            'showscale' : False
        },
        ],
        "layout":{
            'geo':{
                'bgcolor' : '#2c3e50'
            },
            'paper_bgcolor': '#2c3e50',
            'height': 660,
            'title': {
                'xanchor' :"center",
                'text':"World Map",
                'font':{
                    'size': 36,
                    'family' : 'Helvetica',
                    'color' : '#4DDDDD'
                }
                },
            'margin': {
                'l':0,
                'r':0,
            }
        }            
    }

def draw_singleCountry_Scatter(df, variable, graph_line, selected_country,ISO):
    '''
    Function to generate and plot a scatterplot for confirmed/deaths with linear or log scale for the selected countries
    '''
    fig = go.Figure()
    label_max, text_label_max = ticks_log(df, selected_country)
    for country in selected_country:
        try:
            ISO_legend = ISO['alpha-3'].loc[ISO['name'] == country].to_list()[0]
        except:
            ISO_legend = country
        if graph_line == 'Log':
            y = df.loc[df[country] >= 1].copy()
            x = [x for x in range(len(y))]
            fig.add_trace(go.Scatter(x =  x, y = y[country],
                                mode='lines+markers',
                                name=ISO_legend,
                                line=dict(width=3), marker = dict(size = 3, line = dict(width = 1,color = 'DarkSlateGrey')), hoverinfo = "text",
                                hovertext = [f"Country/Region: {country}, ({ISO_legend}) <br>{variable}: {y.iloc[indice][country]:,} <br>Days: {x[indice]}" for indice in range(len(y))]))
            fig.update_yaxes(tickvals = label_max, ticktext = text_label_max)
        else:
            x = df.index
            fig.add_trace(go.Scatter(x =  x, y = df[country],
                                mode='lines+markers',
                                name=ISO_legend,
                                line=dict(width=3), marker = dict(size = 3, line = dict(width = 1,color = 'DarkSlateGrey')), hoverinfo = "text",
                                hovertext = [f"Country/Region: {country}, ({ISO_legend}) <br>{variable}: {df.iloc[indice][country]:,} <br>Date: {str(x[indice])[:10]}" for indice in range(len(df))]))
            fig.update_xaxes(tickformat = '%d %B (%a)<br>%Y')
            fig.update_yaxes(tickformat = ',')
    fig.update_layout(title= f'Total {variable}')

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
        plot_bgcolor = '#2c3e50',
        paper_bgcolor = '#5AC7C1',
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#5AC7C1')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#5AC7C1')
    fig.update_yaxes(zeroline=True, zerolinewidth=2, zerolinecolor='black')

    return fig

def draw_mortality_fatality(df_confirmed_t, df_deaths_t, pop_t, variable, x_graph, selected_country,ISO):
    '''
    Function to generate and plot a scatterplot for mortality rate/Share of infected population/Growth rate confirmed cases/Growth rate deaths
    with date or days scale for the selected countries
    '''
    fig = go.Figure()
    if x_graph == 'Date':
        if variable == 'Mortality rate':
            for country in selected_country:
                try:
                    ISO_legend = ISO['alpha-3'].loc[ISO['name'] == country].to_list()[0]
                except:
                    ISO_legend = country
                if pop_t[country][0] > 0:
                    y = (df_deaths_t[country])/(pop_t[country][0]).copy()
                else:
                    y = np.nan
                    write_log("***division by zero in pop_t[country][0]***")
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
        plot_bgcolor='#2c3e50',
        paper_bgcolor = '#5AC7C1',
        margin=dict(l=0, r=0, t=65, b=0),
        #height=350
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#5AC7C1')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#5AC7C1')
    fig.update_yaxes(zeroline=True, zerolinewidth=2, zerolinecolor='black')

    return fig

def draw_singleCountry_Epicurve(df, df_policy_index, df_epic, df_epic_days, variable, plot, selected_country,ISO):
    '''
    Function to generate and plot a scatterplot for Epidemic curve and policy index for confirmed/deaths for the selected countries
    '''
    fig = go.Figure()
    if plot == 'Epidemic curves':
        for country in selected_country:
            try:
                ISO_legend = ISO['alpha-3'].loc[ISO['name'] == country].to_list()[0]
            except:
                ISO_legend = country
            fig.add_trace(go.Scatter(x =  df_epic_days[country], y = df_epic[country],
                                mode='lines+markers',
                                name=ISO_legend,
                                line=dict(width=3), marker = dict(size = 3, line = dict(width = 1,color = 'DarkSlateGrey')), connectgaps = True, hoverinfo = "text",
                                hovertext = [f"Country/Region: {country} <br>{variable}: {df.iloc[indice][country]:,} <br>3-day MA of ln % of total cases: {np.exp(df_epic.iloc[indice][country]):.3f}% <br>Days: {df_epic_days.iloc[indice][country]} <br>Date: {df_epic.reset_index().iloc[indice]['index'].date()}" for indice in range(len(df))]))
        fig.update_layout(title = f'Epidemic curve for {variable}')
        fig.update_yaxes(tickvals = [-6.9, -4.6, -2.3, 0, 2.30258], ticktext = [f'{np.exp(-6.9):.3f}%', f'{np.exp(-4.6):.3f}%', f'{np.exp(-2.3):.3f}%', f'{np.exp(0):.3f}%', f'{np.exp(2.30258):.3f}%'])
    if plot == 'Stringency index':
        label_max, text_label_max = ticks_log(df, selected_country)
        for country in selected_country:
            try:
                ISO_legend = ISO['alpha-3'].loc[ISO['name'] == country].to_list()[0]
            except:
                ISO_legend = country
            fig.add_trace(go.Scatter(x =  df[country], y = df_policy_index[country],
                                mode='lines+markers',
                                name=ISO_legend,
                                line=dict(width=3), marker = dict(size = 3, line = dict(width = 1,color = 'DarkSlateGrey')), hoverinfo = "text",
                                hovertext = [f"Country/Region: {country} <br>{variable}: {df.iloc[indice][country]:,} <br>Stringency index: {df_policy_index.iloc[indice][country]:,} <br>Date: {df.reset_index().iloc[indice]['index'].date()}" for indice in range(len(df))]))
        fig.update_layout(title= f'Stringency index {variable}', xaxis = {'type': 'log'})
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
        plot_bgcolor = '#2c3e50',
        paper_bgcolor = '#5AC7C1',
        margin=dict(l=0, r=0, t=65, b=0),
        #height=350
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#5AC7C1')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#5AC7C1')
    fig.update_yaxes(zeroline=True, zerolinewidth=1, zerolinecolor='#5AC7C1')
    fig.update_xaxes(zeroline=True, zerolinewidth=1, zerolinecolor='#5AC7C1')


    return fig

def make_item(available_indicators, top_4):
    '''
    Function to create the Accordion to click to show/hide the dropdown menù of the countries
    '''
    return dbc.Card(
        [
            dbc.CardHeader(
                dbc.Button(
                    "Hide/Show Bar",
                    color="primary",
                    id="temp_prova_accordion",
                    block = True,
                    active = True
                ),
            ),
            dbc.Collapse(
                dbc.CardBody(
                    [html.Div([
                         dbc.ButtonGroup(
                            [dbc.Button("World Map", href="#worldMap", external_link=True),
                            dbc.Button("World Stats", href="#worldStats", external_link=True),
                            dbc.Button("Countries Stats", href="#countriesStats", external_link=True),],
                        ),
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
                    ),], className = "py-1"),
                id="temp_prova_collapse",
            ),
        ], className = "my-2 shadow", style = {"overflow": "visible"}
        )

