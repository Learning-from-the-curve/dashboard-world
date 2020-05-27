html.Div([ #Main Container   
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
                    dcc.Graph(id='global_map', figure = gen_map(map_data = map_data))
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
