import datetime
import json
import dash
import pickle
import os
from pathlib import Path
import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table as dt
from dash.dependencies import Input, Output, State

import dash_bootstrap_components as dbc
# Custom functions
from layout_functions import gen_map, draw_singleCountry_Scatter, draw_mortality_fatality, draw_singleCountry_Epicurve, make_item
from pickle_functions import unpicklify
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

flask_app.config["SCOUT_NAME"] = "COVID-19 - World dashboard"

#for heroku to run correctly
server = app.server

#############################################################################
# UNPICKLIFICATION TIME - load the datasets in the variables
#############################################################################

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

df_confirmed_t = unpicklify(pickles_list[0])
df_deaths_t = unpicklify(pickles_list[1])
df_policy_index = unpicklify(pickles_list[2])
df_epic_confirmed = unpicklify(pickles_list[3])
df_epic_days_confirmed = unpicklify(pickles_list[4])
df_epic_deaths = unpicklify(pickles_list[5])
df_epic_days_deaths = unpicklify(pickles_list[6])
df_tab_right = unpicklify(pickles_list[7])
pop_t = unpicklify(pickles_list[8])
map_data = unpicklify(pickles_list[9])
df_world = unpicklify(pickles_list[10])
df_EU28 = unpicklify(pickles_list[11])
df_left_list_confirmed_t = unpicklify(pickles_list[12])
df_left_list_deaths_t = unpicklify(pickles_list[13])
df_left_list_daily_confirmed_increase = unpicklify(pickles_list[14])
df_left_list_daily_deaths_increase = unpicklify(pickles_list[15])
daily_confirmed_world = unpicklify(pickles_list[16])
daily_deaths_world = unpicklify(pickles_list[17])
daily_confirmed_EU28 = unpicklify(pickles_list[18])
daily_deaths_EU28 = unpicklify(pickles_list[19])
top_4 = unpicklify(pickles_list[20])
available_variables = unpicklify(pickles_list[21])
available_indicators = unpicklify(pickles_list[22])
ISO = unpicklify(pickles_list[23])


#add to the dataframe map_data the column with ISO codes for each country
iso_j=ISO[['name','alpha-3']]
map_data= map_data.set_index('Country/Region').join(iso_j.set_index('name'))
map_data= map_data.reset_index()

#tab_confirmed_left
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

#tab_deaths_left
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

#tab_confirmed_increase_left
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

#tab_deaths_increase_left
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

#tab_right
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


############################
# Bootstrap Grid Layout
############################

app.layout = html.Div([
    dbc.Row([
        dbc.Col(html.Div(dbc.Alert("One of two columns"),className='divBorder'), width=1),
        dbc.Col(html.H1("Bootstrap Grid System Example",className="text-center"), width=10),
        dbc.Col(html.Div(dbc.Alert("One of two columns"),className='divBorder'), width=1),
        ])
    
, html.H4("no_gutters = False")
, dbc.Row([
    dbc.Col(html.Div(dbc.Alert("One of two columns")), width=3),
    dbc.Col(html.Div(dbc.Alert("One of two columns")), width=3),
    dbc.Col(html.Div(dbc.Alert("One of two columns")), width=3),
    dbc.Col(html.Div(dbc.Alert("One of two columns")), width=3)
])
, html.H4("no_gutters = True")
, dbc.Row([
    dbc.Col(html.Div(dbc.Alert("One of two columns")), width=3),
    dbc.Col(html.Div(dbc.Alert("One of two columns")), width=3),
    dbc.Col(html.Div(dbc.Alert("One of two columns")), width=3),
    dbc.Col(html.Div(dbc.Alert("One of two columns")), width=3)
], no_gutters = True)    
, html.H3("Examples of justify property")
, html.H4("start, center, end, between, around")
, dbc.Row([
    dbc.Col(html.Div(dbc.Alert("One of two columns")), width=4),
    dbc.Col(html.Div(dbc.Alert("One of two columns")), width=4),
],
justify="start")
, dbc.Row([
    dbc.Col(html.Div(dbc.Alert("One of two columns")), width=3),
    dbc.Col(html.Div(dbc.Alert("One of two columns")), width=3),
],
justify="center")
, dbc.Row([
    dbc.Col(html.Div(dbc.Alert("One of three columns")), width=3)
    , dbc.Col(html.Div(dbc.Alert("One of three columns")), width=3)
    , dbc.Col(html.Div(dbc.Alert("One of three columns")), width=3)
],
justify="end")
, dbc.Row([
    dbc.Col(html.Div(dbc.Alert("One of two columns")), width=3),
    dbc.Col(html.Div(dbc.Alert("One of two columns")), width=3)
    , dbc.Col(html.Div(dbc.Alert("One of three columns")), width=3)
],
justify="between")
, dbc.Row([
    dbc.Col(html.Div(dbc.Alert("One of two columns")), width=4),
    dbc.Col(html.Div(dbc.Alert("One of two columns")), width=4),
],
justify="around")
, html.H4("Container Example")
, dbc.Container([
    dbc.Row([
    dbc.Col(html.Div(dbc.Alert("One of two columns")), width=3),
    dbc.Col(html.Div(dbc.Alert("One of two columns")), width=3),
    dbc.Col(html.Div(dbc.Alert("One of two columns")), width=3),
    dbc.Col(html.Div(dbc.Alert("One of two columns")), width=3)
])
, html.H4("no_gutters = True")
, dbc.Row([
    dbc.Col(html.Div(dbc.Alert("One of two columns")), width=3),
    dbc.Col(html.Div(dbc.Alert("One of two columns")), width=3),
    dbc.Col(html.Div(dbc.Alert("One of two columns")), width=3),
    dbc.Col(html.Div(dbc.Alert("One of two columns")), width=3)
], no_gutters = True)    
])
])



# draw the two graphs under the map for confirmed cases and deaths
@app.callback(
    [Output('line-graph-confirmed', 'figure'),
    Output('line-graph-deaths', 'figure')],
    [Input('demo-dropdown', 'value'),
    Input('graph-line', 'value')])
def line_selection(dropdown, graph_line):
    if len(dropdown) == 0:
        for country in top_4:
            dropdown.append(country)
    fig1 = draw_singleCountry_Scatter(df_confirmed_t, 'confirmed cases', graph_line, selected_country = dropdown, ISO = ISO)
    fig2 = draw_singleCountry_Scatter(df_deaths_t, 'deaths', graph_line, selected_country = dropdown,ISO = ISO)
    return fig1, fig2

# draw the graph for the selected statistic from mortality rate/Share of infected population/Growth rate confirmed cases/Growth rate deaths
@app.callback(
    Output('line-graph-multiple', 'figure'),
    [Input('demo-dropdown', 'value'),
    Input('x-var', 'value'),
    Input('variable-dropdown', 'value')])
def line_selection2(dropdown, x_choice, variable):
    if len(dropdown) == 0:
        for country in top_4:
            dropdown.append(country)
    fig1 = draw_mortality_fatality(df_confirmed_t, df_deaths_t, pop_t, variable = variable, x_graph = x_choice, selected_country = dropdown, ISO = ISO)
    return fig1

# draw the two graphs regarding the epicurve for confirmed cases and deaths
@app.callback(
    [Output('line-graph-epicurve', 'figure'),
    Output('line-graph-policy', 'figure')],
    [Input('demo-dropdown', 'value'),
    Input('variable-dropdown-epic', 'value')])
def line_selection3(dropdown, plots_epic_policy):
    if len(dropdown) == 0:
        for country in top_4:
            dropdown.append(country)
    fig1 = draw_singleCountry_Epicurve(df_confirmed_t, df_policy_index, df_epic_confirmed, df_epic_days_confirmed, 'confirmed cases', plot = plots_epic_policy, selected_country = dropdown, ISO = ISO)
    fig2 = draw_singleCountry_Epicurve(df_deaths_t, df_policy_index, df_epic_deaths, df_epic_days_deaths, 'deaths', plot = plots_epic_policy, selected_country = dropdown, ISO = ISO)
    return fig1, fig2

# draw the right tab with the statistics specific for each country selected in the dropdown menù
@app.callback(
    Output('selected-countries-tab', 'children'),
    [Input('demo-dropdown', 'value')])
def tab_right_countries(dropdown):
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
    )

# open/close the left modal
@app.callback(
    Output("modal-centered-left", "is_open"),
    [Input("open-centered-left", "n_clicks"), Input("close-centered-left", "n_clicks")],
    [State("modal-centered-left", "is_open")],)
def toggle_modal_left(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

# open/close the right modal
@app.callback(
    Output("modal-centered-right", "is_open"),
    [Input("open-centered-right", "n_clicks"), Input("close-centered-right", "n_clicks")],
    [State("modal-centered-right", "is_open")],)
def toggle_modal_right(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

# open/close the accordion
@app.callback(
    Output("temp_prova_collapse", "is_open"),
    [Input("temp_prova_accordion", "n_clicks"),],
    [State("temp_prova_collapse", "is_open")],)
def toggle_accordion(n1, is_open1):
    ctx = dash.callback_context
    if not ctx.triggered:
        return True
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if button_id == "temp_prova_accordion" and n1:
        return not is_open1
    return is_open1

if __name__ == '__main__':
   app.run_server(debug=False)
