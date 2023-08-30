import dash
import pymysql
from sqlalchemy import create_engine                                
from dash import Dash, dcc, html, Input, Output, callback
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from datetime import date
from datetime import timedelta
import pandas as pd
import sqlite3
import numpy as np
import json
import boto3


dapp = Dash(__name__,
    external_stylesheets=[dbc.themes.LUX, dbc.icons.FONT_AWESOME]
)

# Establish a connection to the database
s3_client = boto3.client('s3')
response = s3_client.get_object(Bucket='zappa-db-cre', Key='confg.txt')
data = response['Body'].read()
conf = json.loads(data)

engine = create_engine("mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
                       .format(**conf))

connection = engine.connect()

# Global Variables

# Images
LOGO = 'eleccarb/assets/logo.jpg'
ERROR404 = 'eleccarb/assets/AA-4.png'

#Colors 
COLR1 = '#DB444B' # Red
COLR2 = '#006BA2' # Blue
COLR3 = '#3EBCD2' # Cyan
COLR4 = '#379A8B' # Green
COLR5 = '#EBB434' # Yellow
COLR6 = '#B4BA39' # Olive
COLR7 = '#9A607F' # Purple
COLR8 = '#D1B07C' # Gold
COLR9 = '#758D99' # Gray

GEN1 = '#6bc7d9'
GEN2 = '#acdee8'
GEN3 = '#e4f4f7'
GEN4 = '#dcdddd'
GEN5 = '#bbbdbd'
GEN6 = '#7a7e7e'
GEN7 = '#5c6161'
GEN8 = '#404545'


# Variables for replacement & selection

## Trading Period number to Time
tp_time = {
    1:'00:00',  2:'00:30', 3:'01:00', 4:'01:30',
    5:'02:00',  6:'02:30', 7:'03:00', 8:'03:30',
    9:'04:00',  10:'04:30',11:'05:00', 12:'05:30',
    13:'06:00', 14:'06:30',15:'07:00', 16:'07:30',
    17:'08:00', 18:'08:30',19:'09:00', 20:'09:30',
    21:'10:00', 22:'10:30',23:'11:00', 24:'11:30',
    25:'12:00', 26:'12:30',27:'13:00', 28:'13:30',
    29:'14:00', 30:'14:30',31:'15:00', 32:'15:30',
    33:'16:00', 34:'16:30',35:'17:00', 36:'17:30',
    37:'18:00', 38:'18:30',39:'19:00', 40:'19:30',
    41:'20:00', 42:'20:30',43:'21:00', 44:'21:30',
    45:'22:00', 46:'22:30',47:'23:00', 48:'23:30',
    49:'TP49',  50:'TP50'     
}

## Time to trading period with TP at start
trd_period = {
    '00:00':'TP01', '00:30':'TP02','01:00':'TP03', '01:30':'TP04',
    '02:00':'TP05', '02:30':'TP06','03:00':'TP07', '03:30':'TP08',
    '04:00':'TP09', '04:30':'TP10','05:00':'TP11', '05:30':'TP12',
    '06:00':'TP13', '06:30':'TP14','07:00':'TP15', '07:30':'TP16',
    '08:00':'TP17', '08:30':'TP18','09:00':'TP19', '09:30':'TP20',
    '10:00':'TP21', '10:30':'TP22','11:00':'TP23', '11:30':'TP24',
    '12:00':'TP25', '12:30':'TP26','13:00':'TP27', '13:30':'TP28',
    '14:00':'TP29', '14:30':'TP30','15:00':'TP31', '15:30':'TP32',
    '16:00':'TP33', '16:30':'TP34','17:00':'TP35', '17:30':'TP36',
    '18:00':'TP37', '18:30':'TP38','19:00':'TP39', '19:30':'TP40',
    '20:00':'TP41', '20:30':'TP42','21:00':'TP43', '21:30':'TP44',
    '22:00':'TP45', '22:30':'TP46','23:00':'TP47', '23:30':'TP48'              
}

## Year variable
year_vals =[
    {'label':'2022', 'value':2022},
    {'label':'2021', 'value':2021},
    {'label':'2020', 'value':2020},
    {'label':'2019', 'value':2019},
    {'label':'2018', 'value':2018},
    {'label':'2017', 'value':2017},
    {'label':'2016', 'value':2016},
    {'label':'2015', 'value':2015},
    {'label':'2014', 'value':2014},
    {'label':'2013', 'value':2013},
    {'label':'2012', 'value':2012},
    {'label':'2011', 'value':2011},
    {'label':'2010', 'value':2010},
    {'label':'2009', 'value':2009},
    {'label':'2008', 'value':2008},
    {'label':'2007', 'value':2007},
    {'label':'2006', 'value':2006},
    {'label':'2005', 'value':2005},
    {'label':'2004', 'value':2004},
    {'label':'2003', 'value':2003},
]

## Point of Connection variable 
poc_vals = [
    {"label": "BEN2201", "value": "BEN2201"},
    {"label": "HAY2201", "value": "HAY2201"},
    {"label": "KIK2201", "value": "KIK2201"},
    {"label": "ISL2201", "value": "ISL2201"},
    {"label": "OTA2201", "value": "OTA2201"},
    {"label": "WKM2201", "value": "WKM2201"},
                ]




# ------------------------------------------------------------------------------
# Functions

# Function conver hex to rgb
def hex_to_rgb(hex_color: str) -> tuple:
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = hex_color * 2
    return int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)

# Function checking fuel type availability per day
def check_fuel(data):
    fuels = ['Coal','Diesel','Gas','Geo','Hydro','Wind','Co-Gen']
    for fuel in fuels:
        if not (data['Fuel_Code']==fuel).any():
            n = [data.iloc[0,0],fuel] + ([0]*50)
            data.loc[len(data)] = n
    return data


# Function for group daily detail charts
def daily_charts(df3,df4,sp_df,clk_date,pocs):
    # Data preparation
    # Generation dataframe
    df3_0 = pd.melt(df3,id_vars = ['Trading_Date','Fuel_Code'], var_name='Trading_Period',
        value_vars= df3.columns[df3.columns.str.startswith('TP')].to_list(),
        value_name= 'Generation(MWh)')
    
    df3_1 = pd.pivot(df3_0, index=['Trading_Date','Trading_Period'], columns='Fuel_Code',
        values='Generation(MWh)').reset_index().rename_axis(None,axis=1)
    
    # Carbon intensity dataframe
    df4_1 = pd.melt(df4,id_vars='Trading_Date',var_name= 'Trading_Period' ,
        value_name='Carbon_Intensity(g/KWh)', 
        value_vars=df4.columns[df4.columns.str.startswith('c_int')].to_list())
    df4_1['Trading_Period'] = df4_1['Trading_Period'].str.replace('c_int','TP')

    # Emission dataframe
    df4_2 = pd.melt(df4,id_vars='Trading_Date',var_name= 'Trading_Period' ,
        value_name='Emission(tCO2)', 
        value_vars=df4.columns[df4.columns.str.startswith('eTP')].to_list())
    df4_2['Trading_Period'] = df4_2['Trading_Period'].str.replace('e','')

    # Spotprice dataframe
    sp_df = sp_df.replace({'Trading_Period':tp_time})
    sp_df = sp_df.replace({'Trading_Period':trd_period})


    # Plot group charts
    fig4 = make_subplots(rows=4, cols=1,
        shared_xaxes=True,
        subplot_titles=('Carbon Intensity (g/KWh)','Total Emission (tCO2)',
            'Spot Price ($/MWh)','Total Generation (MWh)'),
        vertical_spacing=0.1,
        row_width=[0.4,0.2,0.2,0.2])
    
    # Carbon intensity
    fig4.add_trace(
        go.Scatter(x = df4_1['Trading_Period'], y = df4_1['Carbon_Intensity(g/KWh)'], 
            name='Carbon Intensity(g/KWh)',
            line = dict(color=COLR1, width=2, dash='dot'),
            hovertemplate = '%{y:,.3f} g/KWh'),
            row=1,col=1
        )

    # Emission
    fig4.add_trace(
        go.Scatter(x = df4_2['Trading_Period'], y = df4_2['Emission(tCO2)'],
            fill='tozeroy', marker=dict(color=COLR5),
            fillcolor=f'rgba{(*hex_to_rgb(COLR5), 0.2)}',
            name='Emission(tCO2)', hovertemplate = '%{y:,.2f} tCO2'),
            row=2,col=1
        )
    
    #Chart 4 Average spot price
    for poc in pocs:
        df = sp_df[(sp_df['POC']== poc)]
        fig4.add_trace(
            go.Scatter(x=df['Trading_Period'], y=df['$/MWh'], name= poc,
                   mode='lines',
                   line=dict(width=1),
                   hovertemplate = '%{y:,.2f} $/MWh'),
            row=3,col=1
        )

    # Generation
    fig4.add_trace(
        go.Bar(x=df3_1['Trading_Period'], y=df3_1['Wind'], name='Wind(MWh)',
            marker=dict(color=GEN1,line = dict(width=0)),showlegend=False,
            hovertemplate = '%{y:,.2f} MWh'),
        row=4,col=1
    )

    fig4.add_trace(
        go.Bar(x=df3_1['Trading_Period'], y=df3_1['Hydro'], name='Hydro(MWh)',
            marker=dict(color=GEN2,line = dict(width=0)),showlegend=False,
            hovertemplate = '%{y:,.2f} MWh'),
        row=4,col=1
    )

    fig4.add_trace(
        go.Bar(x=df3_1['Trading_Period'], y=df3_1['Geo'], name='Geothermal(MWh)',
            marker=dict(color=GEN3,line = dict(width=0)),showlegend=False,
            hovertemplate = '%{y:,.2f} MWh'),
        row=4,col=1
    )

    fig4.add_trace(
        go.Bar(x=df3_1['Trading_Period'], y=df3_1['Gas'], name='Gas(MWh)',
            marker=dict(color=GEN4,line = dict(width=0)),showlegend=False,
            hovertemplate = '%{y:,.2f} MWh'),
        row=4,col=1
    )
    
    fig4.add_trace(
        go.Bar(x=df3_1['Trading_Period'], y=df3_1['Diesel'], name='Diesel(MWh)',
            marker=dict(color=GEN5,line = dict(width=0)),showlegend=False,
            hovertemplate = '%{y:,.2f} MWh'),
        row=4,col=1
    )
    
    fig4.add_trace(
        go.Bar(x=df3_1['Trading_Period'], y=df3_1['Coal'], name='Coal(MWh)',
            marker=dict(color=GEN6,line = dict(width=0)),showlegend=False,
            hovertemplate = '%{y:,.2f} MWh'),
        row=4,col=1
    )

    fig4.add_trace(
        go.Bar(x=df3_1['Trading_Period'], y=df3_1['Co-Gen'], name='Co-Gen(MWh)',
            marker=dict(color=GEN8,line = dict(width=0)),showlegend=False,
            hovertemplate = '%{y:,.2f} MWh'),
        row=4,col=1
    )

    # Layout setting

    fig4.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0')
    fig4.update_traces(xaxis='x4')
    fig4.update_xaxes(row=4, col=1, type='category', categoryorder='category ascending')

    # Subplots title setting
    for n in range (4):
        fig4.layout.annotations[n].update(x=0,font_size=12,xanchor ='left')
    sel_date = str(clk_date).split(' ',1)[0]
    fig4.update_layout( height=822,
        plot_bgcolor = '#FFFFFF', paper_bgcolor = '#FFFFFF',
        title_text=(f'<span style="font-size: 18px; ">Detail Data of {sel_date}</span>'),
        yaxis2 = dict(range=[(df4_2.loc[df4_2['Emission(tCO2)']>0,'Emission(tCO2)'].min())-5,
            df4_2['Emission(tCO2)'].max()]),
        title_x= 0.035,
        hovermode='x unified',
        margin = dict(r=30,b=50),
        barmode = 'stack',
        xaxis3 = dict(tickangle = -45, tickfont =dict(size=10),showticklabels=True),
        legend=dict(orientation='h',yanchor='bottom',y=1.02,xanchor='right',x=1))

    return fig4


# Side bar
sidebar = html.Div(
    [
        html.Div(
            [
                html.A(href='https://nicknguyen.me',children=[html.Img(src=LOGO,style={"width": "3rem"})]),
                html.H4('Nick Nguyen',style={'color':'gray'}),
            ],
            className="sidebar-header",
        ),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink(
                    [html.I(className="fas fa-chart-column me-2"), html.Span("Overview")],
                    href="/eleccarb",
                    active="exact",
                ),
                dbc.NavLink(
                    [
                        html.I(className="fas fa-magnifying-glass-chart me-2"),
                        html.Span("Detail View"),
                    ],
                    href="/detail",
                    active="exact",
                ),
                dbc.NavLink(
                    [
                        html.I(className="fas fa-d me-2"),
                        html.Span("Daily View"),
                    ],
                    href="/day",
                    active="exact",
                ),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    className='sidebar',
)

# Overview page
overview = html.Div([
    html.H4("Electricity Generation and Carbon Footprint in New Zealand 2003-2022", style={'textAlign':'center'}),
    html.Br(),html.Br(),
    dbc.Row(html.H6('Choose the period to view ')),
    dbc.Row(dcc.RangeSlider(min =2003, max =2022, step =1,id='year-slider',
                            value=[2003, 2022], 
                            marks={i: '{}'.format(i) for i in range(2003,2023,1)})),
    html.Br(),html.Br(),
    dbc.Row([
        dcc.Loading(id='ov', children= [dbc.Card(dcc.Graph(id='overview-graph',
                                        figure={}))],
            type = 'default',)
    ]),
])

# Detail page
detail_view = html.Div([
    html.H4("Detail Electricity Production, Carbon Emissions and Spot Price", style={'textAlign':'center'}),
    html.Br(),html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select the year for viewing'),width=3),
        dbc.Col(html.H6('Choose the Point of Connection for Average Spot Price'),width=9),
        ]),
    dbc.Row([
            dbc.Col(dcc.Dropdown(id='year-picker', multi=False, clearable=False, 
                                        value=2022,options=year_vals,style={'width':'86%'}),width=3),
            dbc.Col(dcc.Dropdown(
                options=poc_vals,
                multi=True,
                clearable=False, 
                value=['ISL2201','OTA2201'],
                id="pocs-checkbox"
                ),width=6),
            ]),
    html.Br(),
    dbc.Row([  
        dcc.Loading(id='detail_loading',children=
            [dbc.Card(dcc.Graph(id='detail-graph', figure={}, clickData=None, 
                hoverData=None)
            )],
            type = 'default',
        )
    ]),
    html.Br(),html.Hr(),html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Date selection method'),width=3),
        dbc.Col(html.H6('Select the date'),width=2),
        dbc.Col(html.H6('Choose the Point of Connection for Average Spot Price'),width=7)
        ]),
    dbc.Row([
            dbc.Col(dcc.Dropdown(id='method', multi=False, options=[
                        {"label": "Click on the chart above", "value": 1},
                        {"label": "Select using Datepicker", "value": 2},
                    ],
                    value=1, clearable=False, style={'width':'85%'}),width=3),
            dbc.Col(html.Div(id='datepicker',children=[]),width=2),
            dbc.Col(dcc.Dropdown(
                options=poc_vals,
                clearable=False,
                multi=True, 
                value=['ISL2201','OTA2201'],
                id="pocs-checkbox-day"
                ),width=7),
            ]),
    html.Br(),
    dbc.Row(
            dcc.Loading(id='detail_loading2',children=
                [dbc.Card(dcc.Graph(id='detail-graph2', figure={}, clickData=None, 
                hoverData=None)
                )],
            type = 'default',)
            ),

])


content = html.Div(id='page-content', className='content')

dapp.layout = html.Div([
        dcc.Location(id="url"),
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Loading...")),
                dbc.ModalBody("This application is hosted on the AWS Lambda serverless\
                    infrastructure. Please allow a few seconds for it to fully \
                    load its dataset.",
                    style={'text-align':'center'}),
            ],
            id="modal",
            is_open=True,
        ),
        sidebar,
        content],
    style={'backgroundColor':'#F5F5F5'})

# ------------------------------------------------------------------------------
# Callback

# set the content according to the current pathname
@callback(Output("page-content", "children"), Input("url", "pathname")
              )
def render_page_content(pathname):
    if pathname == '/eleccarb':
        return overview
    elif pathname == '/detail':
        return detail_view
    elif pathname == "/daily":
        return html.P("Here are all your messages")
    # If the user tries to reach a different page, return a 404 message
    return html.Div(
        [
            html.H1("404: Not found - Who ate the charts ?", className="text-danger"),
            html.Br(),html.Br(),
            html.Img(src=ERROR404),
            html.Br(),html.Br(),
            html.H2("We didn't eat that, we swear!"),
            html.P(f"The pathname {pathname} was not recognised..."),
        ],
        style={'textAlign':'center'}
    )


#Overview chart
@callback(
    Output(component_id='overview-graph', component_property='figure'),
    Input(component_id='year-slider', component_property='value')
)
def update_overviewchart(value):
    connection = engine.connect()

    year_chosen = value
  
    df = pd.read_sql(f'SELECT * FROM viz_yr_ems_ov WHERE Year >= {year_chosen[0]} and Year <= {year_chosen[1]}',
        con=connection)

    df2 = pd.read_sql(f'SELECT * FROM yearly_elec_fueltype WHERE Year >= {year_chosen[0]} and Year <= {year_chosen[1]}',
        con=connection)
    
    connection.close()

    fig = make_subplots(rows=2, cols=1,
                        shared_xaxes=True,
                        subplot_titles=('Total Generation (GWh) & Total Carbon Emission (KtCO2)',
                                        'Electricity Generation by Fuel Type in Percentage'),
                        vertical_spacing=0.1,
                        row_width=[0.5,0.5],
                        specs=[[{"secondary_y": True}],
                               [{"secondary_y": False}]])

    # Total emission chart
    fig.add_trace(
        go.Scatter(x = df['Year'], y = df['Emission(KtCO2)'], name='Emission(KtCO2)', 
            mode='lines+markers',
            line=dict(color=COLR2),
            marker=dict(symbol="diamond",size=6,color=COLR2),
            hovertemplate = '%{y:,.2f} KtCO2'),
        secondary_y=True,row=1,col=1
    )

    # Electricity generation chart
    
    fig.add_trace(
        go.Bar(x=df2['Year'], y=df2['Wind'], name='Wind(GWh)',
            marker=dict(color=GEN1,line = dict(width=0)),
            hovertemplate = '%{y:,.2f} GWh'),
        secondary_y=False,row=1,col=1
    )

    fig.add_trace(
        go.Bar(x=df2['Year'], y=df2['Hydro'], name='Hydro(GWh)',
            marker=dict(color=GEN2,line = dict(width=0)),
            hovertemplate = '%{y:,.2f} GWh'),
        secondary_y=False,row=1,col=1
    )

    fig.add_trace(
        go.Bar(x=df2['Year'], y=df2['Geo'], name='Geothermal(GWh)',
            marker=dict(color=GEN3,line = dict(width=0)),
            hovertemplate = '%{y:,.2f} GWh'),
        secondary_y=False,row=1,col=1
    )

    fig.add_trace(
        go.Bar(x=df2['Year'], y=df2['Gas'], name='Gas(GWh)',
            marker=dict(color=GEN4,line = dict(width=0)),
            hovertemplate = '%{y:,.2f} GWh'),
        secondary_y=False,row=1,col=1
    )
    
    fig.add_trace(
        go.Bar(x=df2['Year'], y=df2['Diesel'], name='Diesel(GWh)',
            marker=dict(color=GEN5,line = dict(width=0)),
            hovertemplate = '%{y:,.2f} GWh'),
        secondary_y=False,row=1,col=1
    )
    
    fig.add_trace(
        go.Bar(x=df2['Year'], y=df2['Coal'], name='Coal(GWh)',
            marker=dict(color=GEN6,line = dict(width=0)),
            hovertemplate = '%{y:,.2f} GWh'),
        secondary_y=False,row=1,col=1
    )

    fig.add_trace(
        go.Bar(x=df2['Year'], y=df2['Co-Gen'], name='Co-Gen(GWh)',
            marker=dict(color=GEN8,line = dict(width=0)),
            hovertemplate = '%{y:,.2f} GWh'),
        secondary_y=False,row=1,col=1
    )
    
    # Electricity generation by fuel type charts
    
    fig.add_trace(
        go.Scatter(x=df2['Year'], y=df2['Wind'], name='Wind(%)',
            mode='lines',
            line=dict(color=GEN1,width=0.5),
            hovertemplate = '%{y:,.3f} %',
            stackgroup='one',
            groupnorm='percent'),
        secondary_y=False,row=2,col=1
    )

    fig.add_trace(
        go.Scatter(x=df2['Year'], y=df2['Hydro'], name='Hydro(%)',
            mode='lines',
            line=dict(color=GEN2,width=0.5),
            hovertemplate = '%{y:,.3f} %',
            stackgroup='one'),
        secondary_y=False,row=2,col=1
    )

    fig.add_trace(
        go.Scatter(x=df2['Year'], y=df2['Geo'], name='Geothermal(%)',
            mode='lines',
            line=dict(color=GEN3,width=0.5),
            hovertemplate = '%{y:,.3f} %',
            stackgroup='one'),
        secondary_y=False,row=2,col=1
    )

    fig.add_trace(
        go.Scatter(x=df2['Year'], y=df2['Gas'], name='Gas(%)',
            mode='lines',
            line=dict(color=GEN4,width=0.5),
            hovertemplate = '%{y:,.3f} %',
            stackgroup='one'),
        secondary_y=False,row=2,col=1
    )
    
    fig.add_trace(
        go.Scatter(x=df2['Year'], y=df2['Diesel'], name='Diesel(%)',
            mode='lines',
            line=dict(color=GEN5,width=0.5),
            hovertemplate = '%{y:,.3f} %',
            stackgroup='one'),
        secondary_y=False,row=2,col=1
    )
    
    fig.add_trace(
        go.Scatter(x=df2['Year'], y=df2['Coal'], name='Coal(%)',
            mode='lines',
            line=dict(color=GEN6,width=0.5),
            hovertemplate = '%{y:,.3f} %',
            stackgroup='one'),
        secondary_y=False,row=2,col=1
    )

    fig.add_trace(
        go.Scatter(x=df2['Year'], y=df2['Co-Gen'], name='Co-Gen(%)',
            mode='lines',
            line=dict(color=GEN8,width=0.5),
            hovertemplate = '%{y:,.3f} %',
            stackgroup='one'),
        secondary_y=False,row=2,col=1
    )



    # Layout setting
    fig.update_traces(xaxis='x2')
    fig.update_xaxes(row=2, col=1, range = [(year_chosen[0]-0.5),(year_chosen[1]+0.5)])

    # Subplots title setting
    for n in range (2):
        fig.layout.annotations[n].update(x=0,font_size=12,xanchor ='left') 

    # Add figure layout
    fig.update_layout(title_text=(f'<span style="font-size: 18px;"> Total Electricity Generated and Carbon Emission {year_chosen[0]} - {year_chosen[1]}</span>'),
        height = 800,
        hovermode='x unified',
        plot_bgcolor='#FFFFFF',
        barmode = 'stack',
        margin = dict(r=20),
        xaxis2 = dict(tickmode = 'linear',tick0 = 2003,dtick = 1),
        legend=dict(orientation='h',yanchor='top',y=-0.1,xanchor='left',x=0),
        yaxis3=dict(type='linear',range=[1, 100],ticksuffix='%')
        )
    
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0')
    fig.update_yaxes(title_text='Elec.Generated(GWh)', title_font=dict(size=12,color=COLR3), secondary_y=False)
    fig.update_yaxes(row=2, col=1,title_text='Elec.Generated(%)', title_font=dict(size=12,color=COLR3))
    fig.update_yaxes(title_text='Emission (KtCO2)', title_font=dict(size=12,color=COLR2),tickformat= ',.1s',secondary_y=True)

    return fig
 

# Year detail charts
@callback(
    Output(component_id='detail-graph', component_property='figure'),
    Input(component_id='year-picker', component_property='value'),
    Input(component_id='pocs-checkbox', component_property='value')
)
def update_group_charts(sel_year,pocs):
    
    connection = engine.connect()

    df2 = pd.read_sql(f"SELECT * FROM viz_yr_ems_detail WHERE Year = {sel_year}",
        con=connection)
    df2['Trading_Date'] = pd.to_datetime(df2['Trading_Date'])

    df2_1 = pd.read_sql(f"SELECT * FROM weather WHERE Year = {sel_year}",
        con=connection)
    df2_1['Date(NZST)'] = pd.to_datetime(df2_1['Date(NZST)'])

    df2_2 = pd.read_sql(f"SELECT * FROM daily_elec_fueltype WHERE Year = {sel_year}",
        con=connection)
    df2_2['Trading_Date'] = pd.to_datetime(df2_2['Trading_Date'])

    spdf = pd.read_sql(f"SELECT * FROM spotprice_daily WHERE Year = {sel_year}",
        con=connection)
    spdf['Trading_Date'] = pd.to_datetime(spdf['Trading_Date'])

    connection.close()

    daterange = [df2_2['Trading_Date'].min(),df2_2['Trading_Date'].max()]

    fig2 = make_subplots(rows=5, cols=1,
                        shared_xaxes=True,
                        subplot_titles=('Temprature (C)','Carbon Intensity (g/KWh)', 
                            'Total Emission (KtCO2)','Average Spot Price ($/MWh)',
                            'Total Generation (GWh)'),
                        vertical_spacing=0.1,
                        row_width=[0.4,0.15,0.15,0.15,0.15])

    # Chart 1 Temperature
    fig2.add_trace(
            go.Scatter(
                name='Avg Temp(C)',
                x=df2_1['Date(NZST)'],
                y=df2_1['Tavg(C)'],
                mode='lines',
                line=dict(color=COLR6)
            ),row=1,col=1)

    fig2.add_trace(
            go.Scatter(
                name='Max Temp(C)',
                x=df2_1['Date(NZST)'],
                y=df2_1['Tmax(C)'],
                mode='lines',
                marker=dict(color="#444"),
                line=dict(width=0),
                showlegend=False
            ),row=1,col=1)

    fig2.add_trace(
            go.Scatter(
                name='Min Temp(C)',
                x=df2_1['Date(NZST)'],
                y=df2_1['Tmin(C)'],
                marker=dict(color="#444"),
                line=dict(width=0),
                mode='lines',
                fillcolor=f'rgba{(*hex_to_rgb(COLR6), 0.1)}',
                fill='tonexty',
                showlegend=False
            ),row=1,col=1
        )

    # Chart 2 Carbon Intensity
    fig2.add_trace(
            go.Scatter(x = df2['Trading_Date'], y = df2['Carbon_Intensity(g/KWh)'], 
                name='Carbon Intensity(g/KWh)',
                line = dict(color=COLR1, width=2, dash='dot'),
                hovertemplate = '%{y:,.3f} g/KWh'),
                row=2,col=1
        )

    # Chart 3 Emission
    fig2.add_trace(
        go.Scatter(x = df2['Trading_Date'], y = df2['Emission(KtCO2)'],
            fill='tozeroy', marker=dict(color=COLR5),
            fillcolor=f'rgba{(*hex_to_rgb(COLR5), 0.2)}',
            name='Emission(KtCO2)', hovertemplate = '%{y:,.2f} KtCO2'),
            row=3,col=1
        )

    #Chart 4 Average spot price

    for poc in pocs:
        df = spdf[(spdf['POC']== poc)]
        fig2.add_trace(
            go.Scatter(x=df['Trading_Date'], y=df['Avg($/MWh)'], name= poc,
                   mode='lines',
                   line=dict(width=1),
                   hovertemplate = '%{y:,.2f} $/MWh'),
            row=4,col=1
        )

    # Chart 5 Generation

    fig2.add_trace(
        go.Bar(x=df2_2['Trading_Date'], y=df2_2['Wind'], name='Wind(GWh)',
            marker=dict(color=GEN1,line = dict(width=0)),showlegend=False,
            hovertemplate = '%{y:,.2f} GWh'),
        row=5,col=1
    )

    fig2.add_trace(
        go.Bar(x=df2_2['Trading_Date'], y=df2_2['Hydro'], name='Hydro(GWh)',
            marker=dict(color=GEN2,line = dict(width=0)),showlegend=False,
            hovertemplate = '%{y:,.2f} GWh'),
        row=5,col=1
    )

    fig2.add_trace(
        go.Bar(x=df2_2['Trading_Date'], y=df2_2['Geo'], name='Geothermal(GWh)',
            marker=dict(color=GEN3,line = dict(width=0)),showlegend=False,
            hovertemplate = '%{y:,.2f} GWh'),
        row=5,col=1
    )

    fig2.add_trace(
        go.Bar(x=df2_2['Trading_Date'], y=df2_2['Gas'], name='Gas(GWh)',
            marker=dict(color=GEN4,line = dict(width=0)),showlegend=False,
            hovertemplate = '%{y:,.2f} GWh'),
        row=5,col=1
    )
    
    fig2.add_trace(
        go.Bar(x=df2_2['Trading_Date'], y=df2_2['Diesel'], name='Diesel(GWh)',
            marker=dict(color=GEN5,line = dict(width=0)),showlegend=False,
            hovertemplate = '%{y:,.2f} GWh'),
        row=5,col=1
    )
    
    fig2.add_trace(
        go.Bar(x=df2_2['Trading_Date'], y=df2_2['Coal'], name='Coal(GWh)',
            marker=dict(color=GEN6,line = dict(width=0)),showlegend=False,
            hovertemplate = '%{y:,.2f} GWh'),
        row=5,col=1
    )

    fig2.add_trace(
        go.Bar(x=df2_2['Trading_Date'], y=df2_2['Co-Gen'], name='Co-Gen(GWh)',
            marker=dict(color=GEN8,line = dict(width=0)),showlegend=False,
            hovertemplate = '%{y:,.2f} GWh'),
        row=5,col=1
    )

    fig2.add_trace(
        go.Scatter(x=df2['Trading_Date'], y=df2['Generation(GWh)'], name='Total(GWh)',
            marker=dict(size=1, symbol='line-ew', line=dict(width=0.5, 
            color='rgba(135, 206, 250, 0)',)),
            mode="markers",
            showlegend=False,
            hovertemplate = '%{y:,.2f} GWh'),
        row=5,col=1
    )

    # Layout setting

    fig2.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0')
    fig2.update_traces(xaxis='x5')
    fig2.update_xaxes(row=5, col=1, range = daterange)

    # Subplots title setting
    for n in range (5):
        fig2.layout.annotations[n].update(x=0,font_size=12,xanchor ='left') 

    fig2.update_layout( height=1000,
        plot_bgcolor = '#FFFFFF', paper_bgcolor = '#FFFFFF',
        title_text=(f'<span style="font-size: 18px; ">Detail Data of year {sel_year}</span>'),
        title_x= 0.035,
        hovermode='x unified',
        margin = dict(r=30,b=50),
        barmode = 'stack',
        xaxis5 = dict(tickangle = 0, tickfont =dict(size=10),showticklabels=True, 
            dtick ='M1', range = daterange, type="date"),
        xaxis5_rangeslider_visible=True, xaxis5_rangeslider_thickness=0.05,
        legend=dict(orientation='h',yanchor='bottom',y=1.02,xanchor='right',x=1)
                    )
    return fig2        

# Date picker panel
@callback(
    Output(component_id='datepicker', component_property='children'),
    Input(component_id='method', component_property='value'),
    Input(component_id='detail-graph', component_property='clickData'),
)
def dt_picker(method_val,clk_data):
    if method_val == 1:
        return html.Div(dcc.DatePickerSingle(
                id='dpicker',
                month_format='MMMM Y',
                placeholder='MMMM Y',
                min_date_allowed=date(2003, 1, 1),
                max_date_allowed=date(2022, 12, 31),
                initial_visible_month=date(2022, 1, 1),
                date=date(2022, 1, 1),
                disabled= True))
    elif (method_val==2) & (clk_data is None):
        year = 2022
        return html.Div(dcc.DatePickerSingle(
                id='dpicker',
                month_format='MMMM Y',
                placeholder='MMMM Y',
                min_date_allowed=date(2003, 1, 1),
                max_date_allowed=date(2022, 12, 31),
                initial_visible_month=date(year, 1, 1),
                date=date(year, 1, 1),
                disabled= False))
    elif (method_val==2) & (clk_data is not None):
        year = pd.to_datetime(clk_data['points'][0]['x']).year
        return html.Div(dcc.DatePickerSingle(
                id='dpicker',
                month_format='MMMM Y',
                placeholder='MMMM Y',
                min_date_allowed=date(2003, 1, 1),
                max_date_allowed=date(2022, 12, 31),
                initial_visible_month=date(year, 1, 1),
                date=date(year, 1, 1),
                disabled= False))

# Daily detail charts and cards
@callback(
    Output(component_id='detail-graph2', component_property='figure'),
    Input(component_id='method', component_property='value'),
    Input(component_id='dpicker', component_property='date'),
    Input(component_id='detail-graph', component_property='clickData'),
    Input(component_id='pocs-checkbox-day', component_property='value')
)
def update_daily_charts(method_val,dp_date,clk_data,pocs):

    def days_chart(clk_date):
        
        connection = engine.connect()

        df3 = pd.read_sql(f"SELECT * FROM elec_detail WHERE Trading_Date = '{clk_date}'",
        con=connection)
        df3['Trading_Date'] = pd.to_datetime(df3['Trading_Date'])
        df3 = check_fuel(df3)

        df4 = pd.read_sql(f"SELECT * FROM daily_ems WHERE Trading_Date = '{clk_date}'",
        con=connection)
        df4['Trading_Date'] = pd.to_datetime(df4['Trading_Date'])

        sp_df = pd.read_sql(f"SELECT * FROM spotprice_detail WHERE Trading_Date = '{clk_date}'",
        con=connection)
        sp_df['Trading_Date'] = pd.to_datetime(sp_df['Trading_Date'])

        connection.close()
   
        fig4 = daily_charts(df3,df4,sp_df,clk_date,pocs)
        return fig4
    

    if (method_val ==1) & (clk_data is None):
        default = '2022-01-01'
        clk_date = default
        return days_chart(clk_date)

    elif (method_val ==1) & (clk_data is not None):
        clk_date = (clk_data['points'][0]['x'])      
        return days_chart(clk_date)
    
    elif (method_val ==2):
        clk_date = pd.to_datetime(dp_date).dt.date
        return days_chart(clk_date)

app = dapp.server.wsgi_app

if __name__ == "__main__":
    dapp.run_server(host='0.0.0.0', port=80, debug=False)