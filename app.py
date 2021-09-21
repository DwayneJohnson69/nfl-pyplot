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

fig.update_layout(
    plot_bgcolor = 'rgba(0, 0, 0, 0)',
    paper_bgcolor = 'rgba(0, 0, 0, 0)',
    font_color=colors['text'],
    )

#Create dash application
app = dash.Dash(__name__, title = 'NFL-PYPLOT', external_stylesheets = [dbc.themes.JOURNAL])

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

sidebar = html.Div(
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
                                {'label' : '2006', 'value' : 2006},
                                {'label' : '2007', 'value' : 2007}, 
                                {'label' : '2008', 'value' : 2008}, 
                                {'label' : '2009', 'value' : 2009}, 
                                {'label' : '2010', 'value' : 2010}, 
                                {'label' : '2011', 'value' : 2011}, 
                                {'label' : '2012', 'value' : 2012}, 
                                {'label' : '2013', 'value' : 2013}, 
                                {'label' : '2014', 'value' : 2014}, 
                                {'label' : '2015', 'value' : 2015}, 
                                {'label' : '2016', 'value' : 2016}, 
                                {'label' : '2017', 'value' : 2017}, 
                                {'label' : '2018', 'value' : 2018}, 
                                {'label' : '2019', 'value' : 2019}, 
                                {'label' : '2020', 'value' : 2020},
                                {'label' : '2021', 'value' : 2021}
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
    ],
    style=SIDEBAR_STYLE,
    )

content = html.Div(id="page-content", children = [], style=CONTENT_STYLE)

content_player = [
            dbc.Nav(
                [
                    html.Img(src='/assets/nfl_logo.png', style={'height':'2%', 'width':'4%'}),
                    dbc.NavLink("Player Statistics", href="/player-statistics", active="exact"),
                    dbc.NavLink("Team Statistics", href="/team-statistics", active="exact")
                ], 
                vertical = False,
                pills =  True
            ),
            html.P(
            "Player Statistics", className="lead", style = {'fontSize' : 50, 'color' : 'black'}
            ),
            dcc.Graph(
                    id='graph_1',
                    figure = fig,
                        config={
                            'displayModeBar': False
                        }
                )
            ]

content_team = [
            dbc.Nav(
                [
                    html.Img(src='/assets/nfl_logo.png', style={'height':'2%', 'width':'4%'}),
                    dbc.NavLink("Player Statistics", href="/player-statistics", active = "exact"),
                    dbc.NavLink("Team Statistics", href="/team-statistics", active = "exact")
                ], 
                vertical = False,
                pills =  True
            ),
            html.P(
            "Team Statistics", className="lead", style = {'fontSize' : 50, 'color' : 'black'}
            ),
            dcc.Graph(
                    id='graph_1',
                    figure = fig,
                    config={
                            'displayModeBar': False
                        }
            )
            ]

#configure layout
app.layout = html.Div(
                [dcc.Location(id = 'url'),
                sidebar, content]
                )

#app callback to define selected category
@app.callback(
    Output(component_id = 'page-content', component_property = 'children'),
    Input(component_id= 'url', component_property= 'pathname')
)
def update_content(pathname):
    if pathname == '/team-statistics':
        return content_team
    else:
        return content_player

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
    else:
        df = player_df_dict[selected_category]
        player_team = 'Player'
        hover_name = 'Player'
        hover_data = ['Tm', 'Year', 'Pos']

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
        color_continuous_scale='Bluered'
    )

    fig.update_layout(
        plot_bgcolor = 'rgba(0, 0, 0, 0)',
        paper_bgcolor = 'rgba(0, 0, 0, 0)',
        font_color=colors['text']
    )

    #fig.show(config={"displayModeBar": False, "showTips": False})

    if n_clicks == None:
        return fig, None, selected_category, years, x_axis, y_axis, color, size

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
