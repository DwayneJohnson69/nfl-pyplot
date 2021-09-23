from sys import path
import pandas as pd
import dash
from dash import dcc
from dash import html
import plotly.express as px
import numpy as np
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash_table

#load csv files in dictionaries for player and merged team data
def load_df_dict(type, table_ids):
    df_dict = {}
    for table_id in table_ids:
        if type in ['player']:
            path = r'data/players/{}.csv'.format(table_id)
        if type in ['merged']:
            path =  r'data/teams/merged_{}.csv'.format(table_id)
        df_dict[table_id] = pd.read_csv(path)
        for col in df_dict[table_id].columns:
            df_dict[table_id][col] = pd.to_numeric(df_dict[table_id][col], errors = 'ignore')
    return df_dict

player_table_ids = ['passing',  'rushing', 'receiving', 'scrimmage', 'defense', 'returns', 'scoring']
player_df_dict = load_df_dict('player', player_table_ids)

merged_table_ids = ['team_stats', 'passing', 'rushing', 'returns', 'team_scoring', 'team_conversions', 'drives']
merged_df_dict = load_df_dict('merged', merged_table_ids)

#set dict for color schemes
colors = {
    'background': '#f7f7f9',
    'text': '#111111'
}

#create blank figure as figure placeholder
fig = px.scatter()
compare_fig = px.scatter()

fig.update_layout(
    plot_bgcolor = 'rgba(0, 0, 0, 0)',
    paper_bgcolor = 'rgba(0, 0, 0, 0)',
    font_color=colors['text'],
    )
compare_fig.update_layout(
    width = 500,
    height = 500,
    plot_bgcolor = 'rgba(0, 0, 0, 0)',
    paper_bgcolor = 'rgba(0, 0, 0, 0)',
    font_color=colors['text'],
)

#Create dash application
app = dash.Dash(__name__, title = 'NFL-PYPLOT', external_stylesheets = [dbc.themes.JOURNAL], suppress_callback_exceptions = True)

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

#content and sidebar variable initialization   
content = html.Div(id="page-content", children = [], style=CONTENT_STYLE)
sidebar = html.Div(id ="page-sidebar", children = [], style=SIDEBAR_STYLE)

#sidebar for individual team or player stats 
sidebar_individual = [
    html.Div(
    [
        html.H2("NFL-PYPLOT", className="display-9", style = {'fontSize' : 43}),
        html.Hr(),
        html.P(
            "Choose Plot Settings", className="lead"
        ),
        dbc.Nav(
            [
                html.P('Select a Stat Category',
                        style = {'marginBottom' : '0'}
                ), 
                dcc.Dropdown(id = 'category_dropdown',
                            options = [],
                            placeholder = 'Stat Category',
                            style = {'width' : "80%", 
                                    'height' : "28px",
                                    'font-size': '15px',
                                    'display' : 'inline-block',
                                    'marginBottom' : '5px'
                                    }
                            ),
                html.P(
                    '''Select Year(s)''',
                     style = {'marginBottom' : '0'
                            }
                ), 
                dcc.Checklist(id = 'year',
                            options = [
                                {'label' : str(year), 'value': year} for year in np.arange(2006,2022,1)
                            ],
                                style = {'width' : "110%", 
                                        'height' : "10px",
                                        'font-size': '10px',
                                        'display' : 'inline-block',
                                        'marginBottom' : '70px'
                                        },
                                #placeholder = 'Year'
                            ),

                #X-AXIS DATA SELECTION            
                html.P(
                    '''Choose X-Axis Data''',
                    style = {'marginBottom' : '0'
                            }
                ), 
                dcc.Dropdown(id = 'x-axis',
                            options=[
                                {'label': 'No Category Selected', 'value': 'No Category Selected'}
                            ],
                                placeholder = 'X-Axis Data',
                                style = {'width' : "80%", 
                                        'height' : "28px",
                                        'font-size': '15px',
                                        'display' : 'inline-block'
                                        }
                            ),
                html.P('''
                Filter Data Range:
                ''',                   
                    style = {'marginBottom' : '0',
                            'fontSize' : 10
                            }),
                dcc.RangeSlider(
                    id = 'x-axis-range',
                    min = None,
                    max = None,
                    marks={
                    },
                    allowCross = False
                ),

                #Y-AXIS DATA SELECTION   
                html.P(
                    '''Choose Y-Axis Data''',
                    style = {'marginBottom' : '0'
                            }
                ), 
                dcc.Dropdown(id = 'y-axis',
                            options = [
                                {'label':'No Category Selected', 'value': 'No Category Selected'}],
                                placeholder = 'Y-Axis Data',
                                 style = {'width' : "80%", 
                                        'height' : "28px",
                                        'font-size': '15px',
                                        'display' : 'inline-block'
                                        }
                            ),
                html.P('''
                    Filter Data Range:
                    ''',                   
                    style = {'marginBottom' : '0',
                            'fontSize' : 10
                            }
                ),
                dcc.RangeSlider(
                    id = 'y-axis-range',
                ),

                #COLOR DATAPOINT BY STAT
                html.P(
                    '''Color Datapoints''',
                    style = {'marginBottom' : '0'
                            }
                ), 
                dcc.Dropdown(id = 'color',
                            options = [
                                {'label':'No Category Selected', 'value': 'No Category Selected'}],
                                placeholder = 'Data Color',
                                style = {'width' : "80%", 
                                        'height' : "28px",
                                        'font-size': '15px',
                                        'display' : 'inline-block'
                                        },
                            ),
                
                #SIZE DATAPOINT BY STAT
                html.P(
                    '''Size Datapoints''',
                    style = {'marginBottom' : '0'
                            }
                ), 
                dcc.Dropdown(id = 'size',
                            options = [
                                {'label':'No Category Selected', 'value': 'No Category Selected'}],
                                placeholder = 'Data Size',
                                style = {'width' : "80%", 
                                        'height' : "28px",
                                        'font-size': '15px',
                                        'display' : 'inline-block'
                                        },
                            ),
                html.P('''
                '''
                ),
                html.Button(
                    'Clear Selections',
                    id = 'clear-button',
                    style = {
                        'width' : '70%'
                    }
                )
            ],
            vertical=True,
        ),
    ])]

#sidebar for team comparison tab
sidebar_team_compare = [
    html.H2("NFL-PYPLOT", className="display-9", style = {'fontSize' : 43}),
    html.Hr(),
    html.P("Choose Team Comparison Settings", className="lead"),
    html.Br(),

    html.P('Select Team One: ',
        style = {
                'marginBottom' : '2px'
        }
    ),
    html.Div([
        dbc.Nav([
            dcc.Dropdown(id = 'team-compare-year-1',
                        options = [
                            {'label' : str(year), 'value': year} for year in np.arange(2006,2022,1)
                        ],
                        style = {'width' : "50%", 
                                'height' : "20px",
                                'font-size': '12px',
                                'marginRight' : '0px'
                        },
                        placeholder = 'Year'
            ),
            dcc.Dropdown(id = 'team-compare-team-1',
                        options = [
                            {'label': 'No Year Selected', 'value' : None}
                        ],
                        style = {'width' : "50%", 
                                'height' : "20px",
                                'font-size': '12px',
                                'marginBottom' : '30px',
                                'marginLeft' : '0px'
                        },
                        placeholder = 'Team'
            )
            ],
            vertical = False)
        ]),
    html.P('Select Team Two: ',
        style = {
                'marginBottom' : '2px'
        }
    ),
    html.Div([
        dbc.Nav([
            dcc.Dropdown(id = 'team-compare-year-2',
                        options = [
                            {'label' : str(year), 'value': year} for year in np.arange(2006,2022,1)
                        ],
                        style = {'width' : "50%", 
                                'height' : "20px",
                                'font-size': '12px',
                                'marginRight' : '0px'
                        },
                        placeholder = 'Year'
            ),
            dcc.Dropdown(id = 'team-compare-team-2',
                        options = [
                            {'label': 'No Year Selected', 'value' : None}
                        ],
                        style = {'width' : "50%", 
                                'height' : "20px",
                                'font-size': '12px',
                                'marginBottom' : '30px',
                                'marginLeft' : '0px'
                        },
                        placeholder = 'Team'
            )
            ],
            vertical = False)
    ]),
    html.Br(),
    html.P('Plots Axes:',
        style = {
                'marginBottom' : '2px',
                'fontSize' : 15
        }
    ),
    html.P('Passing',
        style = {
                'marginBottom' : '2px',
                'fontSize' : 12
        }
    ),
    html.Div([
        dbc.Nav([
            dcc.Dropdown(
                id = 'compare-pass-x',
                options=[
                        {'label' : col, 'value': col} for col in merged_df_dict['passing'].columns[1:] if col not in ['Tm','Rk']
                ],
                placeholder = 'X-Axis Data',
                value = 'Yds',
                style = {'width' : "50%", 
                        'height' : "28px",
                        'font-size': '12px',
                        'display' : 'inline-block'
                }
            ),
            dcc.Dropdown(
                id = 'compare-pass-y',
                options=[
                        {'label' : col, 'value': col} for col in merged_df_dict['passing'].columns[1:] if col not in ['Tm','Rk']
                ],
                placeholder = 'Y-Axis Data',
                value = 'opp_Yds',
                style = {'width' : "50%", 
                        'height' : "28px",
                        'font-size': '12px',
                        'display' : 'inline-block'
                }
            )
        ],
        vertical = False)
    ]),
    html.P('Rushing',
        style = {
                'marginBottom' : '2px',
                'fontSize' : 12
        }
    ),
    html.Div([
        dbc.Nav([
            dcc.Dropdown(
                id = 'compare-rush-x',
                options=[
                        {'label' : col, 'value': col} for col in merged_df_dict['rushing'].columns[1:] if col not in ['Tm','Rk']
                ],
                placeholder = 'X-Axis Data',
                value = 'Yds',
                style = {'width' : "50%", 
                        'height' : "28px",
                        'font-size': '12px',
                        'display' : 'inline-block'
                }
            ),
            dcc.Dropdown(
                id = 'compare-rush-y',
                options=[
                        {'label' : col, 'value': col} for col in merged_df_dict['rushing'].columns[1:] if col not in ['Tm','Rk']
                ],
                placeholder = 'Y-Axis Data',
                value = 'opp_Yds',
                style = {'width' : "50%", 
                        'height' : "28px",
                        'font-size': '12px',
                        'display' : 'inline-block'
                }
            )
        ],
        vertical = False)
    ]),
    html.P('Per Drive',
        style = {
                'marginBottom' : '2px',
                'fontSize' : 12
        }
    ),
    html.Div([
        dbc.Nav([
            dcc.Dropdown(
                id = 'compare-drive-x',
                options=[
                        {'label' : col, 'value': col} for col in merged_df_dict['drives'].columns[1:] if col not in ['Tm','Rk']
                ],
                placeholder = 'X-Axis Data',
                value = 'Yds',
                style = {'width' : "50%", 
                        'height' : "28px",
                        'font-size': '12px',
                        'display' : 'inline-block'
                }
            ),
            dcc.Dropdown(
                id = 'compare-drive-y',
                options=[
                        {'label' : col, 'value': col} for col in merged_df_dict['drives'].columns[1:] if col not in ['Tm','Rk']
                ],
                placeholder = 'Y-Axis Data',
                value = 'opp_Yds',
                style = {'width' : "50%", 
                        'height' : "28px",
                        'font-size': '12px',
                        'display' : 'inline-block'
                }
            )
        ],
        vertical = False)
    ]),
    html.P('Overall Team Stats',
        style = {
                'marginBottom' : '2px',
                'fontSize' : 12
        }
    ),
    html.Div([
        dbc.Nav([
            dcc.Dropdown(
                id = 'compare-overall-x',
                options=[
                        {'label' : col, 'value': col} for col in merged_df_dict['team_stats'].columns[1:] if col not in ['Tm','Rk']
                ],
                placeholder = 'X-Axis Data',
                value = 'Y/P',
                style = {'width' : "50%", 
                        'height' : "28px",
                        'font-size': '12px',
                        'display' : 'inline-block'
                }
            ),
            dcc.Dropdown(
                id = 'compare-overall-y',
                options=[
                        {'label' : col, 'value': col} for col in merged_df_dict['team_stats'].columns[1:] if col not in ['Tm','Rk']
                ],
                placeholder = 'Y-Axis Data',
                value = 'opp_Y/P',
                style = {'width' : "50%", 
                        'height' : "28px",
                        'font-size': '12px',
                        'display' : 'inline-block'
                }
            )
        ],
        vertical = False)
    ]),
    html.Br(),
    html.P('Datatable Stat Category',
        style = {
                'marginBottom' : '2px',
                'fontSize' : 12
        }
    ),
    dcc.Dropdown(id = 'table_compare_dropdown',
                options = [
                    {'label' : 'Conversions', 'value' : 'team_conversions'},
                    {'label' : 'Drives', 'value' : 'drives'},
                    {'label' : 'Passing', 'value' : 'passing'},
                    {'label' : 'Returns', 'value' : 'returns'},
                    {'label' : 'Rushing', 'value' : 'rushing'},
                    {'label' : 'Scoring', 'value' : 'team_scoring'},
                    {'label' : 'Stats', 'value' : 'team_stats'}
                ],
                placeholder = 'Stat Category',
                value = 'team_stats',
                style = {'width' : "80%", 
                        'height' : "28px",
                        'font-size': '15px',
                        'display' : 'inline-block',
                        'marginBottom' : '5px'
                        }
    ),
    html.Br(),
    html.Button('Clear Selections',
                id = 'compare-clear-button',
                style = {
                    'width' : '70%'
                }
    )
]            

#content for player stats
content_player = [
            dbc.Nav(
                [
                    html.Img(src='/assets/nfl_logo.png', style={'height':'2%', 'width':'4%'}),
                    dbc.NavLink("Player Statistics", href="/player-statistics", active="exact"),
                    dbc.NavLink("Team Statistics", href="/team-statistics", active="exact"),
                    dbc.NavLink("Team Comparison", href="/team-comparison", active="exact")
                ], 
                vertical = False,
                pills =  True
            ),
            html.P(
            "Player Statistics", className="lead", style = {'fontSize' : 50, 'color' : 'black'}
            ),
            html.P(
                "Player Search"
            ),
            dcc.Dropdown(
                id = 'player-search-dropdown',
                style = {'width' : "40%", 
                        'height' : "28px",
                        'font-size': '15px',
                        'display' : 'inline-block',
                        'marginBottom' : '5px'
                        },
                multi = True,
                options = [
                    {'label':'No Category Selected', 'value': None}],
            ),
            dcc.Graph(
                    id='graph_1',
                    figure = fig,
                        config={
                            'displayModeBar': False
                        }
            ),
]

content_team = [
            dbc.Nav(
                [
                    html.Img(src='/assets/nfl_logo.png', style={'height':'2%', 'width':'4%'}),
                    dbc.NavLink("Player Statistics", href="/player-statistics", active = "exact"),
                    dbc.NavLink("Team Statistics", href="/team-statistics", active = "exact"),
                    dbc.NavLink("Team Comparison", href="/team-comparison", active="exact")
                ], 
                vertical = False,
                pills =  True
            ),
            html.P(
            "Team Statistics", className="lead", style = {'fontSize' : 50, 'color' : 'black'}
            ),           
            html.P(
                "Team Search"
            ),
            dcc.Dropdown(
                id = 'team-search-dropdown',
                style = {'width' : "40%", 
                        'height' : "28px",
                        'font-size': '15px',
                        'display' : 'inline-block',
                        'marginBottom' : '5px'
                        },
                multi = True,
                options = [
                    {'label':'No Category Selected', 'value': None}],
            ),
            dcc.Graph(
                    id='graph_1',
                    figure = fig,
                    config={
                            'displayModeBar': False
                        }
            ),
]
#content for team comparison   
content_team_compare = [
    html.Div([
        html.Div([
            dbc.Nav(
                [
                    html.Img(src='/assets/nfl_logo.png', style={'height':'2%', 'width':'4%'}),
                    dbc.NavLink("Player Statistics", href="/player-statistics", active = "exact"),
                    dbc.NavLink("Team Statistics", href="/team-statistics", active = "exact"),
                    dbc.NavLink("Team Comparison", href="/team-comparison", active="exact")
                 ], 
                vertical = False,
                pills =  True
            ),
            html.P(
            "Team Comparison", className="lead", style = {'fontSize' : 50, 'color' : 'black'}
            )
        ]),
        html.Br(),
        dbc.Nav([
            dcc.Graph(
                    id='compare-graph-1',
                    figure = compare_fig,
                        config={
                            'displayModeBar': False
                        }
            ),
            dcc.Graph(
                    id='compare-graph-2',
                    figure = compare_fig,
                        config={
                            'displayModeBar': False
                        }
            )
        ],
        vertical = False),
        dbc.Nav([
            dcc.Graph(
                    id='compare-graph-3',
                    figure = compare_fig,
                        config={
                            'displayModeBar': False
                        }
            ),
            dcc.Graph(
                    id='compare-graph-4',
                    figure = compare_fig,
                        config={
                            'displayModeBar': False
                        }
            )
        ],
        vertical = False)
    ]),
    html.Div([
        dash_table.DataTable(
            id = 'compare-table',
            sort_action = 'native',
            sort_mode = 'single',
            style_data={
                'whiteSpace': 'normal',
                'height': 'auto',
                'minWidth' : '50px',
                'width': 'auto'
            },
        )
    ])
]
#configure layout
app.layout = html.Div(
                [dcc.Location(id = 'url'),
                sidebar, content]
                )

#app callback to define selected category
@app.callback(
    Output(component_id = 'page-content', component_property = 'children'),
    Output(component_id = 'page-sidebar', component_property = 'children'),
    Input(component_id= 'url', component_property= 'pathname')
)
def update_content(pathname):
    if pathname == '/team-statistics':
        return content_team, sidebar_individual
    elif pathname in ['/', '/player-statistics']:
        return content_player, sidebar_individual
    elif pathname in ['/team-comparison']:
        return content_team_compare, sidebar_team_compare

#callback for category dropdown based on player or team 
@app.callback(
    Output(component_id = 'category_dropdown', component_property = 'options'),
    Input(component_id= 'url', component_property= 'pathname')
)
def update_category_dropdown(pathname):
    if pathname == '/team-statistics':
        options = [
            {'label' : 'Conversions', 'value' : 'team_conversions'},
            {'label' : 'Drives', 'value' : 'drives'},
            {'label' : 'Passing', 'value' : 'passing'},
            {'label' : 'Returns', 'value' : 'returns'},
            {'label' : 'Rushing', 'value' : 'rushing'},
            {'label' : 'Scoring', 'value' : 'team_scoring'},
            {'label' : 'Stats', 'value' : 'team_stats'}
            ] 
    else:
        options = [
            {'label' : 'Passing', 'value' : 'passing'}, 
            {'label' : 'Rushing', 'value' : 'rushing'},
            {'label' : 'Receiving', 'value' : 'receiving'},
            {'label' : 'Scrimmage', 'value' : 'scrimmage'},
            {'label' : 'Defense', 'value' : 'defense'},
            {'label' : 'Returns', 'value' : 'returns'},
            {'label' : 'Scoring', 'value' : 'scoring'}
            ]
    return options
        
#create callback for x-axis data using columns of selected category
@app.callback(
    Output(component_id = 'x-axis', component_property = 'options'),
    Input(component_id = 'category_dropdown', component_property = 'value'),
    Input(component_id= 'url', component_property= 'pathname')
)
def columns_for_df(selected_category, pathname):
    if pathname == '/team-statistics':
        df = merged_df_dict[selected_category]
        return [{'label' : col, 'value': col} for col in df.columns[1:] if col not in ['Tm','Rk']]
    else:
        df = player_df_dict[selected_category]
        return [{'label' : col, 'value': col} for col in df.columns[3:] if col not in ['Pos','G','GS']]

@app.callback(
    Output(component_id = 'x-axis-range', component_property = 'min'),
    Output(component_id = 'x-axis-range', component_property = 'max'),
    Output(component_id = 'x-axis-range', component_property = 'value'),
    Output(component_id = 'x-axis-range', component_property = 'step'),
    Output(component_id = 'x-axis-range', component_property = 'marks'),
    Input(component_id = 'category_dropdown', component_property = 'value'),
    Input(component_id = 'year', component_property = 'value'),
    Input(component_id = 'x-axis', component_property = 'value'),
    Input(component_id= 'url', component_property= 'pathname')
)
def update_range_slider(selected_category, years, x_axis_col, pathname):
    if pathname == '/team-statistics':
        df = merged_df_dict[selected_category]
    else: 
        df = player_df_dict[selected_category]
    df = df[df['Year'].isin(years)][x_axis_col]
    if df.min() != 0:
        step = abs((float(df.max()) / float(df.min())) / 100)
    else: 
        step = abs(float(df.max())/ 100)
    value = [float(df.min()), float(df.max())]
    marks = {
        int(df.min()): '{}'.format(df.min()),
        int(df.max()): '{}'.format(df.max())
    }
    return df.min(), df.max(), value, step, marks

#create callback for y-axis data using columns of selected category
@app.callback(
    Output(component_id = 'y-axis', component_property = 'options'),
    Input(component_id = 'category_dropdown', component_property = 'value'),
    Input(component_id= 'url', component_property= 'pathname')
)
def columns_for_df(selected_category, pathname):
    if pathname == '/team-statistics':
        df = merged_df_dict[selected_category]
        return [{'label' : col, 'value': col} for col in df.columns[1:] if col not in ['Tm','Rk']]
    else:
        df = player_df_dict[selected_category]
        return [{'label' : col, 'value': col} for col in df.columns[3:] if col not in ['Pos','G','GS']]
@app.callback(
    Output(component_id = 'y-axis-range', component_property = 'min'),
    Output(component_id = 'y-axis-range', component_property = 'max'),
    Output(component_id = 'y-axis-range', component_property = 'value'),
    Output(component_id = 'y-axis-range', component_property = 'step'),
    Output(component_id = 'y-axis-range', component_property = 'marks'),
    Input(component_id = 'category_dropdown', component_property = 'value'),
    Input(component_id = 'year', component_property = 'value'),
    Input(component_id = 'y-axis', component_property = 'value'),
    Input(component_id= 'url', component_property= 'pathname')
)
def update_range_slider(selected_category, years, y_axis_col, pathname):
    if pathname == '/team-statistics':
        df = merged_df_dict[selected_category]
    else: 
        df = player_df_dict[selected_category]
    df = df[df['Year'].isin(years)][y_axis_col]
    if df.min() != 0:
        step = abs((float(df.max()) / float(df.min())) / 100)
    else: 
        step = abs(float(df.max())/ 100)
    value = [float(df.min()), float(df.max())]
    marks = {
        int(df.min()): '{}'.format(df.min()),
        int(df.max()): '{}'.format(df.max())
    }
    return df.min(), df.max(), value, step, marks

#create callback for color using columns of selected category
@app.callback(
    Output(component_id = 'color', component_property = 'options'),
    Input(component_id = 'category_dropdown', component_property = 'value'),
    Input(component_id= 'url', component_property= 'pathname')
)
def columns_for_df(selected_category, pathname):
    if pathname == '/team-statistics':
        df = merged_df_dict[selected_category]
        return [{'label' : col, 'value': col} for col in df.columns[1:] if col not in ['Tm','Rk']]
    else:
        df = player_df_dict[selected_category]
        return [{'label' : col, 'value': col} for col in df.columns[3:] if col not in ['Pos','G','GS']]

#create callback for size using columns of selected category
@app.callback(
    Output(component_id = 'size', component_property = 'options'),
    Input(component_id = 'category_dropdown', component_property = 'value'),
    Input(component_id= 'url', component_property= 'pathname')
)
def columns_for_df(selected_category, pathname):
    if pathname == '/team-statistics':
        df = merged_df_dict[selected_category]
        return [{'label' : col, 'value': col} for col in df.columns[1:] if col not in ['Tm','Rk']]
    else:
        df = player_df_dict[selected_category]
        return [{'label' : col, 'value': col} for col in df.columns[3:] if col not in ['Pos','G','GS']]

#populate search dropdowns
@app.callback(
    Output(component_id = 'player-search-dropdown', component_property = 'options'),
    Output(component_id = 'team-search-dropdown', component_property = 'options'),
    Input(component_id= 'url', component_property= 'pathname'),
    Input(component_id = 'category_dropdown', component_property = 'value'),
    Input(component_id = 'year', component_property = 'value'),
)
def pop_search(pathname, category, years):
    if pathname in ['/', '/player-statistics']:
        df = player_df_dict[category]
        dff = df[df['Year'].isin(years)]
        player_options = [{'label': name, 'value' : name} for name in dff['Player'].unique()]
        team_options = [{'label': 'No Year Selected', 'value' : None}]
        return player_options, team_options
    elif pathname in ['/team-statistics']:
        df = merged_df_dict[category]
        dff = df[df['Year'].isin(years)]
        player_options = [{'label': 'No Year Selected', 'value' : None}]
        team_options = [{'label': team, 'value' : team} for team in dff['Tm'].unique()]
        return player_options, team_options

#plot scatter figure based on inputted variables
@app.callback(
    Output(component_id = 'graph_1', component_property = 'figure'),
    Output(component_id = 'clear-button' , component_property = 'n_clicks'),
    Output(component_id = 'category_dropdown', component_property = 'value'),
    Output(component_id = 'year', component_property = 'value'),
    Output(component_id = 'x-axis', component_property = 'value'),
    Output(component_id = 'y-axis', component_property = 'value'),
    Output(component_id = 'color', component_property = 'value'),
    Output(component_id = 'size', component_property = 'value'),
    Input(component_id = 'category_dropdown', component_property = 'value'),
    Input(component_id = 'year', component_property = 'value'),
    Input(component_id = 'x-axis', component_property = 'value'),
    Input(component_id = 'x-axis-range', component_property = 'value'),
    Input(component_id = 'y-axis', component_property = 'value'),
    Input(component_id = 'y-axis-range', component_property = 'value'),
    Input(component_id = 'color', component_property = 'value'),
    Input(component_id = 'size', component_property = 'value'),
    Input(component_id = 'clear-button' , component_property = 'n_clicks'),
    Input(component_id= 'url', component_property= 'pathname')
)
def update_graph(selected_category, years, x_axis, x_axis_values, y_axis, y_axis_values, color, size, n_clicks, pathname):
    if pathname in ['/', '/player-statistics', '/team-statistics']:
        fig_blank = px.scatter()
        fig_blank.update_layout(
            plot_bgcolor = 'rgba(0, 0, 0, 0)',
            paper_bgcolor = 'rgba(0, 0, 0, 0)',
            font_color=colors['text'],
        )
        
        if n_clicks != None:
            return fig_blank, None, None, [None], None, None, None, None 
        if pathname == '/team-statistics':
            df = merged_df_dict[selected_category]
            player_team = 'Team'
            hover_name = 'Tm'
            hover_data = ['Year']
            df['split'] = df['Tm'].str.split().str[-1]
        else:
            df = player_df_dict[selected_category]
            player_team = 'Player'
            hover_name = 'Player'
            hover_data = ['Tm', 'Year', 'Pos']
            df['split'] = df['Player'].str.split().str[-1]

        df = df[df['Year'].isin(years)]
        df = df[df[x_axis] >= x_axis_values[0]]
        df = df[df[x_axis] <= x_axis_values[1]]
        df = df[df[y_axis] >= y_axis_values[0]]
        df = df[df[y_axis] <= y_axis_values[1]]

        fig = px.scatter(
            df,
            x = x_axis, y = y_axis, 
            hover_name = hover_name, hover_data = hover_data,
            title = 'NFL {} {} Stats for {} Scatter plot of {} against {}'.format(player_team, selected_category, years, x_axis, y_axis),
            color = color, size = size,
            text = 'split',
            color_continuous_scale='Bluered'
        )

        fig.update_layout(
            plot_bgcolor = 'rgba(0, 0, 0, 0)',
            paper_bgcolor = 'rgba(0, 0, 0, 0)',
            font_color=colors['text']
        )
        if n_clicks == None:
            if pathname in ['/team-statistics']:
                fig.add_hline(
                    y = df[y_axis].mean(),
                    line_width=1, line_dash="dash"
                )   
                fig.add_vline(
                    x = df[x_axis].mean(),
                    line_width=1, line_dash="dash"
                )
                return fig, None, selected_category, years, x_axis, y_axis, color, size
            elif pathname in ['/player-statistics', '/']:
                fig.add_hline(
                    y = df[y_axis].mean(),
                    line_width=1, line_dash="dash"
                )   
                fig.add_vline(
                    x = df[x_axis].mean(),
                    line_width=1, line_dash="dash"
                )
                return fig, None, selected_category, years, x_axis, y_axis, color, size

#create option list for given year in team comparison
@app.callback(
    Output(component_id = 'team-compare-team-1', component_property = 'options'),
    Output(component_id = 'team-compare-team-2', component_property = 'options'),
    Input(component_id = 'team-compare-year-1', component_property = 'value'),
    Input(component_id = 'team-compare-year-2', component_property = 'value')
)
def get_team_list(year_1, year_2):
    df_1 = merged_df_dict['team_stats'][merged_df_dict['team_stats']['Year'] == year_1]
    team_dict_1 = [{'label' : team_name,'value' : team_name} for team_name in df_1['Tm'].unique()]
    df_2 = merged_df_dict['team_stats'][merged_df_dict['team_stats']['Year'] == year_2]
    team_dict_2 = [{'label' : team_name,'value' : team_name} for team_name in df_2['Tm'].unique()]
    return team_dict_1, team_dict_2
#update graphs and data table for given teams
@app.callback(
    Output(component_id = 'compare-graph-1', component_property = 'figure'),
    Output(component_id = 'compare-graph-2', component_property = 'figure'),
    Output(component_id = 'compare-graph-3', component_property = 'figure'),
    Output(component_id = 'compare-graph-4', component_property = 'figure'),
    Output(component_id = 'compare-table', component_property = 'columns'),
    Output(component_id = 'compare-table', component_property = 'data'),
    Input(component_id = 'team-compare-year-1', component_property = 'value'),
    Input(component_id = 'team-compare-year-2', component_property = 'value'),
    Input(component_id = 'team-compare-team-1', component_property = 'value'),
    Input(component_id = 'team-compare-team-2', component_property = 'value'),
    Input(component_id = 'compare-pass-x', component_property = 'value'),
    Input(component_id = 'compare-pass-y', component_property = 'value'),
    Input(component_id = 'compare-rush-x', component_property = 'value'),
    Input(component_id = 'compare-rush-y', component_property = 'value'),
    Input(component_id = 'compare-drive-x', component_property = 'value'),
    Input(component_id = 'compare-drive-y', component_property = 'value'),
    Input(component_id = 'compare-overall-x', component_property = 'value'),
    Input(component_id = 'compare-overall-y', component_property = 'value'),
    Input(component_id = 'compare-clear-button', component_property = 'n_clicks'),
    Input(component_id = 'table_compare_dropdown', component_property = 'value')
)
def update_compare_figures(year_1, year_2, team_1_name, team_2_name, pass_x, pass_y, rush_x, rush_y, drive_x, drive_y, ov_x, ov_y, n_clicks, datatable_category):
    #plot 1 - Passing
    df = merged_df_dict['passing'].set_index(['Tm','Year'])
    pass_df = df.loc[[(team_1_name, year_1), (team_2_name, year_2)]].reset_index()
    pass_fig = px.scatter(
        pass_df,
        x = pass_x,
        y = pass_y,
        hover_name = 'Tm',
        hover_data = ['Year'],
        title = 'Passing',
        color = pass_x,
        size = pass_y,
        text = 'Tm',
        color_continuous_scale='Bluered'
    )
    pass_fig.update_layout(
        plot_bgcolor = 'rgba(0, 0, 0, 0)',
        paper_bgcolor = 'rgba(0, 0, 0, 0)',
        font_color=colors['text']
    )
    pass_fig.add_hline(
        y = merged_df_dict['passing'][pass_y][merged_df_dict['passing']['Year'] != 2021].mean(),
        line_width=1, line_dash="dash",
    )
    pass_fig.add_vline(
        x = merged_df_dict['passing'][pass_x][merged_df_dict['passing']['Year'] != 2021].mean(),
        line_width=1, line_dash="dash",
    )
    dff = merged_df_dict['passing'][merged_df_dict['passing']['Year'] != 2021]
    pass_fig.update_xaxes(range=[dff[pass_x].min(), dff[pass_x].max()])
    pass_fig.update_yaxes(range=[dff[pass_y].min(), dff[pass_y].max()])

    #plot 2 - Rushing
    df = merged_df_dict['rushing'].set_index(['Tm','Year'])
    rush_df = df.loc[[(team_1_name, year_1), (team_2_name, year_2)]].reset_index()
    rush_fig = px.scatter(
        rush_df,
        x = rush_x,
        y = rush_y,
        hover_name = 'Tm',
        hover_data = ['Year'],
        title = 'Rushing',
        color = rush_x,
        size = rush_y,
        text = 'Tm',
        color_continuous_scale='Bluered'
    )
    rush_fig.update_layout(
        plot_bgcolor = 'rgba(0, 0, 0, 0)',
        paper_bgcolor = 'rgba(0, 0, 0, 0)',
        font_color=colors['text']
    )
    rush_fig.add_hline(
        y = merged_df_dict['rushing'][rush_y][merged_df_dict['rushing']['Year'] != 2021].mean(),
        line_width=1, line_dash="dash",
    )
    rush_fig.add_vline(
        x = merged_df_dict['rushing'][rush_x][merged_df_dict['rushing']['Year'] != 2021].mean(),
        line_width=1, line_dash="dash",
    )
    dff = merged_df_dict['rushing'][merged_df_dict['rushing']['Year'] != 2021]
    rush_fig.update_xaxes(range=[dff[rush_x].min(), dff[rush_x].max()])
    rush_fig.update_yaxes(range=[dff[rush_y].min(), dff[rush_y].max()])
    #plot 3 - Per Drive
    df = merged_df_dict['drives'].set_index(['Tm','Year'])
    drives_df = df.loc[[(team_1_name, year_1), (team_2_name, year_2)]].reset_index()
    drives_fig = px.scatter(
        drives_df,
        x = drive_x,
        y = drive_y,
        hover_name = 'Tm',
        hover_data = ['Year'],
        title = 'Per Drive',
        color = drive_x,
        size = drive_y,
        text = 'Tm',
        color_continuous_scale='Bluered'
    )
    drives_fig.update_layout(
        plot_bgcolor = 'rgba(0, 0, 0, 0)',
        paper_bgcolor = 'rgba(0, 0, 0, 0)',
        font_color=colors['text']
    )
    drives_fig.add_hline(
        y = merged_df_dict['drives'][drive_y][merged_df_dict['drives']['Year'] != 2021].mean(),
        line_width=1, line_dash="dash",
    )
    drives_fig.add_vline(
        x = merged_df_dict['drives'][drive_x][merged_df_dict['drives']['Year'] != 2021].mean(),
        line_width=1, line_dash="dash",
    )
    dff = merged_df_dict['drives'][merged_df_dict['drives']['Year'] != 2021]
    drives_fig.update_xaxes(range=[dff[drive_x].min(), dff[drive_x].max()])
    drives_fig.update_yaxes(range=[dff[drive_y].min(), dff[drive_y].max()])
    #plot 4 - Team Stats
    df = merged_df_dict['team_stats'].set_index(['Tm','Year'])
    team_stats_df = df.loc[[(team_1_name, year_1), (team_2_name, year_2)]].reset_index()
    team_stats_fig = px.scatter(
        team_stats_df,
        x = ov_x,
        y = ov_y,
        hover_name = 'Tm',
        hover_data = ['Year'],
        title = 'Overall Team Stats',
        color = ov_x,
        size = ov_y,
        text = 'Tm',
        color_continuous_scale='Bluered'
    )
    team_stats_fig.update_layout(
        plot_bgcolor = 'rgba(0, 0, 0, 0)',
        paper_bgcolor = 'rgba(0, 0, 0, 0)',
        font_color=colors['text']
    )
    team_stats_fig.add_hline(
        y = merged_df_dict['team_stats'][merged_df_dict['team_stats']['Year'] != 2021][ov_y].mean(),
        line_width=1, line_dash="dash",
    )
    team_stats_fig.add_vline(
        x = merged_df_dict['team_stats'][merged_df_dict['team_stats']['Year'] != 2021][ov_x].mean(),
        line_width=1, line_dash="dash",
    )
    dff = merged_df_dict['team_stats'][merged_df_dict['team_stats']['Year'] != 2021]
    team_stats_fig.update_xaxes(range=[dff[ov_x].min(), dff[ov_x].max()])
    team_stats_fig.update_yaxes(range=[dff[ov_y].min(), dff[ov_y].max()])

    #dataframe columns
    df = merged_df_dict[datatable_category].set_index(['Tm','Year'])
    table_df = df.loc[[(team_1_name, year_1), (team_2_name, year_2)]].reset_index()
    table_df = table_df.drop("Unnamed: 0",axis=1)
    columns = [{"name": i, "id": i} for i in table_df.columns]
    data = table_df.to_dict('records')

    return pass_fig, rush_fig, drives_fig, team_stats_fig, columns, data


server = app.server

"""
if __name__ == '__main__': 
    app.run_server(debug = False)
"""
"""
To Do List
Sliders show value for chosen number
fix slider auto-resetting
datapoint search input and highlighting
size dropwdown cant see rows
"""
