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
from layout_functions import gen_map, draw_singleCountry_Scatter, draw_mortality_fatality, draw_singleCountry_Epicurve, make_item, list_item
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

config = {'displayModeBar': False}

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
                        dbc.ListGroupItem([
                            html.Span([f'{country} '], className = "spanCountryName"),
                            html.Span([f'{df_left_list_confirmed_t[country]:,}'], className = "spanConfirmed") 
                        ], 
                        className="items"
                        ) for country in df_left_list_confirmed_t.index
                ],
                className='media-body'
                ),
            ],
            className='media'
            ),   
        ],
        className='list-unstyled'
        ),
    ],  
    className="tabcard overflow-auto"
    ),
className="border-0",
)

#tab_deaths_left
tab_deaths_left = dbc.Card(
    html.Div([
        html.Ul([
            html.Li([
                html.Div([
                        dbc.ListGroupItem([
                            html.Span([f'{country} '], className = "spanCountryName"),
                            html.Span([f'{df_left_list_deaths_t[country]:,}'], className = "spanDeaths"),
                        ], 
                        className="items"
                        ) for country in df_left_list_deaths_t.index
                ],
                className='media-body'
                ),
            ],
            className='media'
            ),   
        ],
        className='list-unstyled'
        ),
    ],
     
    className="tabcard overflow-auto"
    ),
className="border-0",
)

#tab_confirmed_increase_left
tab_confirmed_increase_left = dbc.Card(
    html.Div([
        html.Ul([
            html.Li([
                html.Div([
                        dbc.ListGroupItem([
                            html.Span([f'{country} '], className = "spanCountryName"),
                            html.Span([f'{df_left_list_daily_confirmed_increase.iloc[0][country]:,}'], className = "spanConfirmed"),
                        ], 
                        className="items"
                        ) for country in list(df_left_list_daily_confirmed_increase)
                ],
                className='media-body'
                ),
            ],
            className='media'
            ),   
        ],
        className='list-unstyled'
        ),
    ],
     
    className="tabcard overflow-auto"
    ),
className="border-0",
)

#tab_deaths_increase_left
tab_deaths_increase_left = dbc.Card(
    html.Div([
        html.Ul([
            html.Li([
                html.Div([
                        dbc.ListGroupItem([
                            html.Span([f'{country} '], className = "spanCountryName"),
                            html.Span([f'{df_left_list_daily_deaths_increase.iloc[0][country]:,}'], className = "spanDeaths"),
                        ],
                        className="items"
                        ) for country in list(df_left_list_daily_deaths_increase)
                ],
                className='media-body'
                ),
            ],
            className='media'
            ),   
        ],
        className='list-unstyled'
        ),
    ],
     
    className="tabcard overflow-auto"
    ),
className="border-0",
)

#tab_right
#tab_right = dbc.Card(id ='selected-countries-tab')

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

app.layout = html.Div([ #Main Container   
    html.Div([
    #Header TITLE
    html.Div([
        #Info Modal Button LEFT
        #dbc.Button("Relevant info", id="open-centered-left", className="btn "),
        dbc.ButtonGroup(
            [
                dbc.Button("Home", href="https://www.learningfromthecurve.net/", external_link=True, className="py-2"),
                dbc.Button("Dashboards", href="https://www.learningfromthecurve.net/Dashboards/", external_link=True, className="py-2"),
            ],
            vertical=True,
            size="sm",
        ),
        #H2 Title
        html.H2(
            children='COVID-19 Dashboard',
            className="text-center",
        ),
        #Info Modal Button RIGHT
        #dbc.Button("Datasets info", id="open-centered-right", className="btn "),
        dbc.ButtonGroup(
            [
                dbc.Button("Info", id="open-centered-left", className="py-2"),
                dbc.Button("Datasets", id="open-centered-right", className="py-2"),
            ],
            vertical=True,
            size="sm",
        ),
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
        dbc.Modal(
            [
                dbc.ModalHeader("Relevant information"),
                dbc.ModalBody(children = markdown_relevant_info),
                dbc.ModalFooter(
                    dbc.Button("Close", id="close-centered-left", className="ml-auto")
                ),
            ],
            id="modal-centered-left",
            centered=True,
        ),
    ],
    className="topRow d-flex justify-content-between align-items-center mb-2"
    ),
    
      #First Row CARDS 3333
    dbc.Row([
        dbc.Col([
            #Card 1
            dbc.Card([
                # Card 1 body
                html.H4(children='Global Cases: '),
                html.H2(f"{df_world.iloc[0, -1]:,d}"),
                html.P('New daily confirmed cases: ' + f"{daily_confirmed_world:,d}"),
               ],
            className='cards cases'
            ),
        ],
        lg = 3, xs = 12
        ),     
        dbc.Col([
            #Card 2
            dbc.Card([
                # Card 2 body
                    html.H4(children='Global Deaths: '),
                    html.H2(f"{df_world.iloc[1, -1]:,d}"),
                    html.P('New daily confirmed deaths: ' + f"{daily_deaths_world:,d}"),
            ],
            className='cards deaths'
            ),
        ],
        lg = 3, xs = 12
        ),   
        dbc.Col([
            #Card 3
            dbc.Card([
                # Card 3 body
                html.H4(children='EU28 Cases: '),
                html.H2(f"{df_EU28.iloc[0, -1]:,d}"),
                html.P('New daily confirmed cases: ' + f"{daily_confirmed_EU28:,d}"),
            ],
            className='cards cases'
            ),
        ],
        lg = 3, xs = 12
        ),        
        dbc.Col([
            #Card 4
            dbc.Card([
                # Card 4 body
                html.H4(children='EU28 Deaths: '),
                html.H2(f"{df_EU28.iloc[1, -1]:,d}"),
                html.P('New daily confirmed deaths: ' + f"{daily_deaths_EU28:,d}"),
             ],
            className='cards deaths'
            ),
        ],
        lg = 3, xs = 12
        ),     
        ],
        className = "midRow d-flex"
        ),
    #Second Row 363
    dbc.Row([
        #Col2 Left
        dbc.Col([
            dbc.Card([
                dbc.Tabs([
                    dbc.Tab(tab_confirmed_left, label="Cases"),
                    dbc.Tab(tab_deaths_left, label="Deaths"),
                ],
                className="nav-justified"
                ),
            ],
            className="card my-2 ",
            id="worldStats",
            ),
            dbc.Card([
                dbc.Tabs([
                    dbc.Tab(tab_confirmed_increase_left, label="Daily cases"),
                    dbc.Tab(tab_deaths_increase_left, label="Daily deaths")
                ],
                className="nav-justified"
                ),
            ],
            className="card my-2 ",
            id="worldStats_daily",
            )
        ],
        #align = "stretch",
        lg = 3, md = 12 
        ),

    #Col6 Middle
        dbc.Col([
            #Map, Table
            html.Div([
                html.Div([
                    dcc.Graph(figure = gen_map(map_data = map_data),config= config)
                ],
                #className=' h-100',
                id="worldMap",
                ),
            ],
            className='my-2 '
            ),
        ],
        #className="col-md-6 order-md-2"
        lg = 6, xs = 12
        ),

        #Col2 Right
        dbc.Col([
            dbc.Card([
                dbc.Tabs([
                    dbc.Tab(dbc.Card(id ='selected-countries-tab'), label="Country statistics"),
                ],
                className="nav-justified",
                id = 'info_tab_right'
                )
            ],
            className="items my-2 ",
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
        #className= "h-100",
        lg = 3, xs = 12
        ),
    ],
    className = "botRow d-flex"
    )
    ],
    className="container-fluid cf py-2"
    ),

    html.Div([
        #Country select Dropdown
        html.Div(
                [make_item(available_indicators, top_4)], className="accordion sticky-top"
        ),

    dbc.Row([
        dbc.Col([
            html.Div([
                html.Div([
                    dbc.Label("Scale:", html_for="graph-line"),
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
            className='card my-2 '
            ),
        ],
        width =12
        )
    ], 
    justify="center"
    ),

#Line Graph Confirmed
    dbc.Row([
        dbc.Col([
            html.Div([
                html.Div([
                    dcc.Graph(id='line-graph-confirmed',config=config)
                ],
                className='p-1'
                ),
            ],
            className='card my-2 '
            ),
        ],
        lg = 6, md = 12
        ),
        dbc.Col([
            #Line Graph Deaths
            html.Div([
                html.Div([
                    dcc.Graph(id='line-graph-deaths',config=config)
                ],
                className='p-1'
                ),
            ],
            style={},
            className='card my-2 '
            ),
        ],
        lg = 6, md = 12
        )
    ]),
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
                'Epidemic curve: Reports the fraction of cases or deaths out of the total numbers up until today. For each selected country the date with the largest 3-day MA of the log of percentage of total cases or deaths is considered as day 0, defined also as the "turning point".'
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
    className='card my-2 '
    ),
    #Line Graph Epidemic curves
    dbc.Row([
        dbc.Col([
            html.Div([
                html.Div([
                    dcc.Graph(id='line-graph-epicurve',config=config)
                ],
                className='p-1'
                ),
            ],
            className='card my-2 '
            ),
        ],
        lg = 6, md = 12
        ),
        dbc.Col([
            #Line Graph Policy
            html.Div([
                html.Div([
                    dcc.Graph(id='line-graph-policy',config=config)
                ],
                className='p-1'
                ),
            ],
            style={},
            className='card my-2 '
            ),
        ],
        lg = 6, md = 12
        )
    ]),
    dbc.Row([
        dbc.Col([
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
            className='card my-2 '
            ),
            #Line Graph Multiple
            html.Div([
                html.Div([
                    dcc.Graph(id='line-graph-multiple',config=config)
                ],
                className='p-1'
                ),
            ],
            style={},
            className='card my-2 '
            ),
        ],
        lg = 12
        )
    ], 
    justify="center"
    ),

    ],
    className="container-fluid"
    )

],
#className = "my-0"
)

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
    fig1 = draw_singleCountry_Scatter(df_confirmed_t, 'confirmed', graph_line, selected_country = dropdown, ISO = ISO)
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
    fig1 = draw_singleCountry_Epicurve(df_confirmed_t, df_policy_index, df_epic_confirmed, df_epic_days_confirmed, 'confirmed', plot = plots_epic_policy, selected_country = dropdown, ISO = ISO)
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
                            html.Hr(),
                            dbc.ListGroupItemText(f'Confirmed cases: {df_tab_right.iloc[0][country]:,}'),
                            dbc.ListGroupItemText(f'Deaths: {df_tab_right.iloc[1][country]:,}'),
                            list_item('Mortality rate: ', float('%.2f'%(df_tab_right.iloc[2][country]*100)), '%'),
                            dbc.ListGroupItemText(f'Share of infected population: {df_tab_right.iloc[3][country]*100:.2f}%'),
                            dbc.ListGroupItemText(f'Share out of global confirmed cases: {df_tab_right.iloc[4][country]*100:.4f}%'),
                            list_item('Share out of global deaths: ', float('%.4f'%(df_tab_right.iloc[5][country]*100)), '%'),
                            dbc.ListGroupItemText(f'Date of 1st confirmed case: {df_tab_right.iloc[6][country]}'),
                            list_item('Date of 1st confirmed death: ', df_tab_right.iloc[7][country], ''),
                            list_item('Stringency Index: ', df_tab_right.iloc[8][country], ''),
                            dbc.ListGroupItemText(f'Population in 2019: {df_tab_right.iloc[9][country]:,}'),
                            ], className="items") for country in dropdown
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
    className="tabr overflow-auto"
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
