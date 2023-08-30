import dash
from dash import Dash, dcc, html, Input, Output, callback, dash_table
from dash.dash_table import DataTable, FormatTemplate
from dash.dash_table.Format import Format, Scheme, Trim
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from datetime import date
from datetime import timedelta
import pandas as pd
import numpy as np
import os



dashapp = dash.Dash(__name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME]
)


money = FormatTemplate.money(2)
percentage = FormatTemplate.percentage(2)
integer = Format(precision=2, scheme=Scheme.decimal_integer)
percentage = FormatTemplate.percentage(2)


# Dataloading
sp3years_df = pd.read_csv('maindf.csv')
sp3years_df['Trading_Date'] = pd.to_datetime(sp3years_df['Trading_Date'])

# VARIABLES

# Year data
years = [2020,2021,2022]
# Contract price
CFD1buy = 100
CFD1sell = 200
CFD2buy = 200
CFD2sell = 270

# capacity per trading period (MWh)
cap_per_tp = 0.2


timeslots ={
# Morning buy
'zero_130' : ['00:00','00:30','01:00'],
'zero30_2' : ['00:30','01:00','01:30'],
'one_230' : ['01:00','01:30','02:00'],
'one30_3' : ['01:30','02:00','02:30'],
'two_330' : ['02:00','02:30','03:00'],
'two30_4' : ['02:30','03:00','03:30'],
'three_430' : ['03:00','03:30','04:00'],
'three30_5' : ['03:30','04:00','04:30'],
'four_530' : ['04:00','04:30','05:00'],
'four30_6' : ['04:30','05:00','05:30'],
'five_630' : ['05:00','05:30','06:00'],
'five30_7' : ['05:30','06:00','06:30'],
# Morning sell
'seven_830' : ['07:00','07:30','08:00'],
'seven30_9' : ['07:30','08:00','08:30'],
'eight_930' : ['08:00','08:30','09:00'],
'eight30_10' : ['08:30','09:00','09:30'],
# Afternoon buy
'ten_1130' : ['10:00','10:30','11:00'],
'ten30_12' : ['10:30','11:00','11:30'],
'eleven_1230' : ['11:00','11:30','12:00'],
'eleven30_13' : ['11:30','12:00','12:30'],
'twelve_1330' : ['12:00','12:30','13:00'],
'twelve30_14' : ['12:30','13:00','13:30'],
'thirdteen_1430' : ['13:00','13:30','14:00'],
'thirdteen30_15' : ['13:30','14:00','14:30'],
'fourteen_1530' : ['14:00','14:30','15:00'],
'fourteen30_16' : ['14:30','15:00','15:30'],
'fifteen_1630' : ['15:00','15:30','16:00'],
'fifteen30_17' : ['15:30','16:00','16:30'],
'sixteen_1730' : ['16:00','16:30','17:00'],
'sixteen30_18' : ['16:30','17:00','17:30'],
# Evening sell
'eighteen_1930' : ['18:00','18:30','19:00'],
'eighteen30_20' : ['18:30','19:00','19:30'],
'nineteen_2030' : ['19:00','19:30','20:00'],
'nineteen30_21' : ['19:30','20:00','20:30'],
}



# colors
col1 = '#578ca1'
col2 = '#5dc8c3'
col3 = '#bcd0d9'
col4 = '#c4eae6'

LOGO = 'cfdanalysis/assets/logo.jpg'

navbar = dbc.NavbarSimple(
    brand= dbc.Container(
                dbc.Row(
                    [
                        dbc.Col(html.Img(src=LOGO, height="30px",style={'justify':'end'})),
                        dbc.Col(html.H4('NICK NGUYEN', className="ms-2", 
                                        style={
                                               'color' :'#444444'})),
                    ],
                    align="end",
                    className="g-0 px-0",
                    style={'padding-left':'0px'},
                ),fluid=True,
            ),
    
    brand_href='https://nicknguyen.me',
    color='white',
    sticky='top',
    dark=False,
    fluid=True,
    class_name='px-0 shadow-sm p-2 mb-5 bg-white',
)

# Functions
# Year selection func
def year_selection(df,year):
    filtered_df = df[pd.to_datetime(df['Trading_Date']).dt.year==year]
    return filtered_df

# Asset running conditions
def compute(asset,cfd,threshold):
    if (asset > threshold):
        return cfd + asset
    else:
        return cfd

# Asset running count
def asset_run_count(asset,cfd,threshold):
    if (asset > threshold):
        return 1
    else:
        return 0

def df_preparation(year,threshold,buy1,sell1,buy2,sell2):
    # Filter by year
    df = year_selection(sp3years_df,year)

    # Marking trading times  
    df['mbuy'] = np.where(df['Trading_Period'].isin (timeslots[f'{buy1}']),1,0)
    df['msell'] = np.where(df['Trading_Period'].isin (timeslots[f'{sell1}']),1,0)
    df['abuy'] = np.where(df['Trading_Period'].isin (timeslots[f'{buy2}']),1,0)
    df['esell'] = np.where(df['Trading_Period'].isin (timeslots[f'{sell2}']),1,0)

    # Asset runing values - using ISL2201
    df['Asset_mbuy($)'] = df['ISL($/MWh)']*df['mbuy']*cap_per_tp
    df['Asset_msell($)'] = df['ISL($/MWh)']*df['msell']*cap_per_tp
    df['Asset_abuy($)'] = df['ISL($/MWh)']*df['abuy']*cap_per_tp
    df['Asset_esell($)'] = df['ISL($/MWh)']*df['esell']*cap_per_tp

    # CFD1 and CFD2 values - using OTA2201
    df['CFD1_mbuy_bCFD'] =  CFD1buy*df['mbuy']*cap_per_tp
    df['CFD1_mbuy_sSpot'] =  df['OTA($/MWh)']*df['mbuy']*cap_per_tp
    df['CFD1_msell_sCFD'] =  CFD1sell*df['msell']*cap_per_tp
    df['CFD1_msell_bSpot'] =  df['OTA($/MWh)']*df['msell']*cap_per_tp

    df['CFD2_abuy_bCFD'] =  CFD2buy*df['abuy']*cap_per_tp
    df['CFD2_abuy_sSpot'] =  df['OTA($/MWh)']*df['abuy']*cap_per_tp
    df['CFD2_esell_sCFD'] =  CFD2sell*df['esell']*cap_per_tp
    df['CFD2_esell_bSpot'] =  df['OTA($/MWh)']*df['esell']*cap_per_tp

    temp = df.groupby('Trading_Date',as_index=False).sum(numeric_only=True)
    day_df = temp[['Trading_Date','Asset_mbuy($)','Asset_msell($)','Asset_abuy($)',
                   'Asset_esell($)','CFD1_mbuy_bCFD','CFD1_mbuy_sSpot','CFD1_msell_sCFD',
                   'CFD1_msell_bSpot','CFD2_abuy_bCFD','CFD2_abuy_sSpot',
                   'CFD2_esell_sCFD','CFD2_esell_bSpot']].copy()
    
    #Compute Phrases values
    day_df['Asset_p1($)'] = day_df['Asset_msell($)'] - day_df['Asset_mbuy($)']
    day_df['Asset_p2($)'] = day_df['Asset_esell($)'] - day_df['Asset_abuy($)']
    day_df['CFD1($)'] = day_df['CFD1_mbuy_sSpot'] - day_df['CFD1_mbuy_bCFD'] + day_df['CFD1_msell_sCFD'] - day_df['CFD1_msell_bSpot']
    day_df['CFD2($)'] = day_df['CFD2_abuy_sSpot'] - day_df['CFD2_abuy_bCFD'] + day_df['CFD2_esell_sCFD'] - day_df['CFD2_esell_bSpot']

    day_df['Phrase1($)'] = day_df.apply(lambda x: compute(x['Asset_p1($)'],x['CFD1($)'],
                                                              threshold),axis =1)
    day_df['Ph1_Asset_run'] = day_df.apply(
        lambda x: asset_run_count(x['Asset_p1($)'], x['CFD1($)'],threshold),axis =1
        )
    day_df['Phrase2($)'] = day_df.apply(lambda x: compute(x['Asset_p2($)'], x['CFD2($)'],
                                                              threshold),axis =1)
    day_df['Ph2_Asset_run'] = day_df.apply(
        lambda x: asset_run_count(x['Asset_p2($)'], x['CFD2($)'],threshold),axis =1)
    
    return day_df

def df_preparation2(year,threshold,buy1,sell1,buy2,sell2):
    # Filter by year
    df = year_selection(sp3years_df,year)

    # Marking trading times  
    df['mbuy'] = np.where(df['Trading_Period'].isin (timeslots[f'{buy1}']),1,0)
    df['msell'] = np.where(df['Trading_Period'].isin (timeslots[f'{sell1}']),1,0)
    df['abuy'] = np.where(df['Trading_Period'].isin (timeslots[f'{buy2}']),1,0)
    df['esell'] = np.where(df['Trading_Period'].isin (timeslots[f'{sell2}']),1,0)

    # Asset runing values - using ISL2201
    df['Asset_mbuy($)'] = df['ISL($/MWh)']*df['mbuy']*cap_per_tp
    df['Asset_msell($)'] = df['ISL($/MWh)']*df['msell']*cap_per_tp
    df['Asset_abuy($)'] = df['ISL($/MWh)']*df['abuy']*cap_per_tp
    df['Asset_esell($)'] = df['ISL($/MWh)']*df['esell']*cap_per_tp

    # CFD1 and CFD2 values - using OTA2201
    df['CFD1_msell_sCFD'] =  CFD1sell*df['msell']*cap_per_tp
    df['CFD1_msell_bSpot'] =  df['OTA($/MWh)']*df['msell']*cap_per_tp

    df['CFD2_esell_sCFD'] =  CFD2sell*df['esell']*cap_per_tp
    df['CFD2_esell_bSpot'] =  df['OTA($/MWh)']*df['esell']*cap_per_tp

    temp = df.groupby('Trading_Date',as_index=False).sum(numeric_only=True)
    day_df = temp[['Trading_Date','Asset_mbuy($)','Asset_msell($)','Asset_abuy($)',
                   'Asset_esell($)','CFD1_msell_sCFD','CFD1_msell_bSpot',
                   'CFD2_esell_sCFD','CFD2_esell_bSpot']].copy()
    
    #Compute Phrases values
    day_df['Asset_p1($)'] = day_df['Asset_msell($)'] - day_df['Asset_mbuy($)']
    day_df['Asset_p2($)'] = day_df['Asset_esell($)'] - day_df['Asset_abuy($)']
    day_df['CFD1($)'] = day_df['CFD1_msell_sCFD'] - day_df['CFD1_msell_bSpot']
    day_df['CFD2($)'] = day_df['CFD2_esell_sCFD'] - day_df['CFD2_esell_bSpot']

    day_df['Phrase1($)'] = day_df.apply(lambda x: compute(x['Asset_p1($)'],x['CFD1($)'],
                                                              threshold),axis =1)
    day_df['Ph1_Asset_run'] = day_df.apply(
        lambda x: asset_run_count(x['Asset_p1($)'], x['CFD1($)'],threshold),axis =1
        )
    day_df['Phrase2($)'] = day_df.apply(lambda x: compute(x['Asset_p2($)'], x['CFD2($)'],
                                                              threshold),axis =1)
    day_df['Ph2_Asset_run'] = day_df.apply(
        lambda x: asset_run_count(x['Asset_p2($)'], x['CFD2($)'],threshold),axis =1)
    
    return day_df

# Layout

tab1 = html.Div([
    dbc.Row([
        html.Div('Option 1 - Scenario Assumption',style={'font-size':'25px',
                                                         'padding-bottom':'20px'}),
        
        dbc.Col([
            dbc.Row([
                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.P('Select year for analysing',
                            style={'font-weight':'bold','font-size':'12px',
                                    'text-transform':'uppercase'}),
                        dcc.Dropdown(id='year_sel', multi=False,clearable=False,
                                    options = [
                                    {"label": "2022", "value": 2022},
                                    {"label": "2021", "value": 2021},
                                    {"label": "2020", "value": 2020},
                                ]
                                ,value=2022),
                    ]),
                ]),width=6),

                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.P('Input cost per asset cycle',
                            style={'font-weight':'bold','font-size':'12px',
                                    'text-transform':'uppercase'}),
                        dcc.Input(id='threshold', type='number', 
                            placeholder=0,min=0,value=0,style={'height':'35px',
                                                               'width':'220px'}),
                    ]),
                ]),width=6),
            ]),
        ],width=4,style={'padding':'20px'}),


        dbc.Col([
            dbc.Row([
                html.P('CfD 1: Charging 1:00 - 4:00 & Discharging 7:00 - 10:00', 
                       style={'font-size':'16px','text-transform':'uppercase',
                              'color':'#444', 'text-align':'center',
                              'font-weight':'bold'}),
                dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.P('Select charging timeframe',
                            style={'font-weight':'bold','font-size':'12px',
                                        'text-transform':'uppercase'}),
                        dcc.Dropdown(id='buy_sel1', multi=False,clearable=False,
                                   options = [
                                       {"label": "01:00-02:30", "value": 'one_230'},
                                       {"label": "01:30-03:00", "value": 'one30_3'},
                                       {"label": "02:00-03:30", "value": 'two_330'},
                                       {"label": "02:30-04:00", "value": 'two30_4'},
                                   ],
                                    value='one_230',
                                   ),
                        ]),
                    ]),
                ],width=6),
                
                dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.P('Select discharging timeframe',
                            style={'font-weight':'bold','font-size':'12px',
                                        'text-transform':'uppercase'}),
                        dbc.Select(id='sell_sel1', 
                                   options = [
                                       {"label": "07:00-08:30", "value": 'seven_830'},
                                       {"label": "07:30-09:00", "value": 'seven30_9'},
                                       {"label": "08:00-09:30", "value": 'eight_930'},
                                       {"label": "08:30-10:00", "value": 'eight30_10'},
                                   ],
                                    value='seven_830',
                                   ),
                        ]),
                    ]),
                ],width=6),
            ]),
        ],width=4,style={'border-left':'1px solid lightgray','padding':'20px'}),

        dbc.Col([
            dbc.Row([
                html.P('CfD 2: Charging 11:00 - 14:00 & Discharging 18:00 - 21:00', 
                       style={'font-size':'16px','text-transform':'uppercase',
                              'color':'#444', 'text-align':'center',
                              'font-weight':'bold'}),
             dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.P('Select charging timeframe',
                            style={'font-weight':'bold','font-size':'12px',
                                        'text-transform':'uppercase'}),
                        dbc.Select(id='buy_sel2', 
                                   options = [
                                       {"label": "11:00-12:30", "value": 'eleven_1230'},
                                       {"label": "11:30-13:00", "value": 'eleven30_13'},
                                       {"label": "12:00-13:30", "value": 'twelve_1330'},
                                       {"label": "12:30-14:00", "value": 'twelve30_14'},
                                   ],
                                    value='eleven_1230',
                                   ),
                        ]),
                    ]),
                ],width=6),

                dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.P('Select discharging timeframe',
                            style={'font-weight':'bold','font-size':'12px',
                                        'text-transform':'uppercase'}),
                        dbc.Select(id='sell_sel2', 
                                   options = [
                                       {"label": "18:00-19:30", "value": 'eighteen_1930'},
                                       {"label": "18:30-20:00", "value": 'eighteen30_20'},
                                       {"label": "19:00-20:30", "value": 'nineteen_2030'},
                                       {"label": "19:30-21:00", "value": 'nineteen30_21'},
                                   ],
                                    value='eighteen_1930',
                                   ),
                        ]),
                    ]),
                ],width=6),


            ]),
        ],width=4,style={'border-left':'1px solid lightgray','padding':'20px'}),

    ],align='end',style={'margin-bottom':'0px','padding-bottom':'0px',
                         'margin-top':'0px','padding-top':'0px'}),

    dbc.Row([
        dbc.Row([
            dbc.Col(html.Div('Analysis & Summary',style={'font-size':'25px'})
                    ,width=3, align='center',),
        ],style={'padding-bottom':'20px'}),
        
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Row([
                        html.Div(id='analysis_sum',children={}),
                    ],style={'padding-top':'10px'}),
                 
                ],style={'padding-bottom':'20px'}),

            ]),
        ]),
    ],style={'padding-top':'40px','padding-left':'10px','padding-right':'10px'}),

    dbc.Row([
        html.Div('Daily Data Table', 
                 style={'font-size':'25px','padding-top':'10px','padding-bottom':'20px'}),
        dcc.Loading(id='general_loading',children=
            [dbc.Card(
                html.Div(id='daily_table',children={},style={'padding':'5px'}),
            )],
            type = 'default',
        ),
    ],style={'padding-top':'30px'}),
    html.Br(),
    html.Br(),
]),

tab2 = html.Div([
    dbc.Row([
        html.Div('Option 2 - Scenario Assumption',style={'font-size':'25px',
                                                         'padding-bottom':'20px'}),
        dbc.Col([
            dbc.Row([
                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.P('Select year for analysing',
                            style={'font-weight':'bold','font-size':'12px',
                                    'text-transform':'uppercase'}),
                        dcc.Dropdown(id='year_sel_tab2', multi=False,clearable=False,
                                    options = [
                                    {"label": "2022", "value": 2022},
                                    {"label": "2021", "value": 2021},
                                    {"label": "2020", "value": 2020},
                                ]
                                ,value=2022),
                    ]),
                ]),width=6),

                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.P('Input cost per asset cycle',
                            style={'font-weight':'bold','font-size':'12px',
                                    'text-transform':'uppercase'}),
                        dcc.Input(id='threshold_tab2', type='number', 
                            placeholder=0,min=0,value=0,style={'height':'35px',
                                                               'width':'220px'}),
                    ]),
                ]),width=6),
            ]),
        ],width=4,style={'padding':'20px'}),

        dbc.Col([
            dbc.Row([
                html.P('CfD 1: DISCHARGING 7:00 - 10:00', 
                       style={'font-size':'16px','text-transform':'uppercase',
                              'color':'#444', 'text-align':'center',
                              'font-weight':'bold'}),
                dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.P('Select charging timeframe',
                            style={'font-weight':'bold','font-size':'12px',
                                        'text-transform':'uppercase'}),
                        dcc.Dropdown(id='buy_sel1_tab2', multi=False,clearable=False,
                                   options = [
                                       {"label": "00:00-01:30", "value": 'zero_130'},
                                       {"label": "00:30-02:00", "value": 'zero30_2'},                                       
                                       {"label": "01:00-02:30", "value": 'one_230'},
                                       {"label": "01:30-03:00", "value": 'one30_3'},
                                       {"label": "02:00-03:30", "value": 'two_330'},
                                       {"label": "02:30-04:00", "value": 'two30_4'},
                                       {"label": "03:00-04:30", "value": 'three_430'},
                                       {"label": "03:30-05:00", "value": 'three30_5'},
                                       {"label": "04:00-05:30", "value": 'four_530'},
                                       {"label": "04:30-06:00", "value": 'four30_6'},
                                       {"label": "05:00-06:30", "value": 'five_630'},
                                       {"label": "05:30-07:00", "value": 'five30_7'},
                                   ],
                                    value='one_230',
                                   ),
                        ]),
                    ]),
                ],width=6),
                
                dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.P('Select discharging timeframe',
                            style={'font-weight':'bold','font-size':'12px',
                                        'text-transform':'uppercase'}),
                        dbc.Select(id='sell_sel1_tab2', 
                                   options = [
                                       {"label": "07:00-08:30", "value": 'seven_830'},
                                       {"label": "07:30-09:00", "value": 'seven30_9'},
                                       {"label": "08:00-09:30", "value": 'eight_930'},
                                       {"label": "08:30-10:00", "value": 'eight30_10'},
                                   ],
                                    value='seven_830',
                                   ),
                        ]),
                    ]),
                ],width=6),
            ]),
        ],width=4,style={'border-left':'1px solid lightgray','padding':'20px'}),

        dbc.Col([
            dbc.Row([
                html.P('CfD 2:  DISCHARGING 18:00 - 21:00', 
                       style={'font-size':'16px','text-transform':'uppercase',
                              'color':'#444', 'text-align':'center',
                              'font-weight':'bold'}),
             dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.P('Select charging timeframe',
                            style={'font-weight':'bold','font-size':'12px',
                                        'text-transform':'uppercase'}),
                        dbc.Select(id='buy_sel2_tab2', 
                                   options = [
                                       {"label": "10:00-11:30", "value": 'ten_1130'},
                                       {"label": "10:30-12:00", "value": 'ten30_12'},
                                       {"label": "11:00-12:30", "value": 'eleven_1230'},
                                       {"label": "11:30-13:00", "value": 'eleven30_13'},
                                       {"label": "12:00-13:30", "value": 'twelve_1330'},
                                       {"label": "12:30-14:00", "value": 'twelve30_14'},
                                       {"label": "13:00-14:30", "value": 'thirdteen_1430'},
                                       {"label": "13:30-15:00", "value": 'thirdteen30_15'},
                                       {"label": "14:00-15:30", "value": 'fourteen_1530'},
                                       {"label": "14:30-16:00", "value": 'fourteen30_16'},
                                       {"label": "15:00-16:30", "value": 'fifteen_1630'},
                                       {"label": "15:30-17:00", "value": 'fifteen30_17'},
                                       {"label": "16:00-17:30", "value": 'sixteen_1730'},
                                       {"label": "16:30-18:00", "value": 'sixteen30_18'},
                                   ],
                                    value='eleven_1230',
                                   ),
                        ]),
                    ]),
                ],width=6),

                dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.P('Select discharging timeframe',
                            style={'font-weight':'bold','font-size':'12px',
                                        'text-transform':'uppercase'}),
                        dbc.Select(id='sell_sel2_tab2', 
                                   options = [
                                       {"label": "18:00-19:30", "value": 'eighteen_1930'},
                                       {"label": "18:30-20:00", "value": 'eighteen30_20'},
                                       {"label": "19:00-20:30", "value": 'nineteen_2030'},
                                       {"label": "19:30-21:00", "value": 'nineteen30_21'},
                                   ],
                                    value='eighteen_1930',
                                   ),
                        ]),
                    ]),
                ],width=6),


            ]),
        ],width=4,style={'border-left':'1px solid lightgray','padding':'20px'}),

    ],align='end',style={'margin-bottom':'0px','padding-bottom':'0px',
                         'margin-top':'0px','padding-top':'0px'}),

    dbc.Row([
        dbc.Row([
            dbc.Col(html.Div('Analysis & Summary',style={'font-size':'25px'})
                    ,width=3, align='center',),
        ],style={'padding-bottom':'20px'}),
        
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Row([
                        html.Div(id='analysis_sum_tab2',children={}),
                    ],style={'padding-top':'10px'}),
                 
                ],style={'padding-bottom':'20px'}),

            ]),
        ]),
    ],style={'padding-top':'40px','padding-left':'10px','padding-right':'10px'}),

    dbc.Row([
        html.Div('Daily Data Table', 
                 style={'font-size':'25px','padding-top':'10px','padding-bottom':'20px'}),
        dcc.Loading(id='general_loading',children=
            [dbc.Card(
                html.Div(id='daily_table_tab2',children={},style={'padding':'5px'}),
            )],
            type = 'default',
        ),
    ],style={'padding-top':'30px'}),
    html.Br(),
    html.Br(),
]),

dashapp.layout = dbc.Container([
    navbar,
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
    dbc.Row([
        html.H1('Electricity CfD Analysis',style={'text-align':'center'}),
    ],style={'padding-top':'30px','padding-bottom':'20px'}),

    dcc.Tabs(id="tabs-charts", value='tab-1', children=[
        dcc.Tab(label='CFD OPTION 1', value='tab-1',style={'font-weight':'bold',
                                                          'font-size':'15px',
                                                          'color':'orange',}),
        dcc.Tab(label='CFD OPTION 2', value='tab-2',style={'font-weight':'bold',
                                                          'font-size':'15px',
                                                          'color':'orange',}),
    ]),
    html.Div(id='tabs-content'),
    ],fluid=True,style={'backgroundColor':'white'})


# ------------------------------------------------------------------------------
# Callback

@callback(Output('tabs-content', 'children'),
              Input('tabs-charts', 'value'))
def render_content(tab):
    if tab == 'tab-1':
        return tab1
    elif tab == 'tab-2':
        return tab2

# Tab 1
@callback(
    Output(component_id='analysis_sum', component_property='children'),
    Input(component_id='year_sel', component_property='value'),
    Input(component_id='threshold', component_property='value'),
    Input(component_id='buy_sel1', component_property='value'),
    Input(component_id='sell_sel1', component_property='value'),
    Input(component_id='buy_sel2', component_property='value'),
    Input(component_id='sell_sel2', component_property='value'),
)
def analysis_sum_update(year,threshold,buy1,sell1,buy2,sell2):
    threshold = float(threshold)
    df = df_preparation(year,threshold,buy1,sell1,buy2,sell2)
    summary = dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H4('Phrase 1')
            ],width=3),
            dbc.Col([
                html.Div(f'',),
            ],width=1,style={'text-align':'left',}),
            dbc.Col(html.Div(),width=1),
            dbc.Col([
                html.H4('Phrase 2')
            ],width=3),
            dbc.Col([
                html.Div(f'',),
            ],width=1,style={'text-align':'left',}),
            dbc.Col([
                html.H4(f'Total',),
            ],width=2,style={'text-align':'right',}),
        ]),

        html.Br(),
        html.H5('Asset Running Summary'),

        dbc.Row([
            dbc.Col([
                html.H6('Revenue from running asset on monring phrase only')
            ],width=3),
            dbc.Col([
                html.Div(f'$ {df["Asset_p1($)"].sum():,.2f}',),
            ],width=1,style={'text-align':'left',}),
            dbc.Col(html.Div(),width=1),
            dbc.Col([
                html.H6('Revenue from running asset on afternoon phrase only')
            ],width=3),
            dbc.Col([
                html.Div(f'$ {df["Asset_p2($)"].sum():,.2f}',),
            ],width=1,style={'text-align':'left',}),
            dbc.Col([
                html.Div(f'$ {df["Asset_p1($)"].sum()+df["Asset_p2($)"].sum():,.2f}',),
            ],width=2,style={'text-align':'right',}),
        ]),
        
        dbc.Row([
            dbc.Col([
                html.H6('Cost from running asset on monring phrase only')
            ],width=3),
            dbc.Col([
                html.Div(f'$ {365*threshold:,.2f}',),
            ],width=1,style={'text-align':'left','text-decoration': 'underline'}),
            dbc.Col(html.Div(),width=1),
            dbc.Col([
                html.H6('Cost from running asset on afternoon phrase only')
            ],width=3),
            dbc.Col([
                html.Div(f'$ {365*threshold:,.2f}',),
            ],width=1,style={'text-align':'left','text-decoration': 'underline'}),
            dbc.Col([
                html.Div(f'$ {365*threshold*2:,.2f}',),
            ],width=2,style={'text-align':'right',}),
        ]),

   
        dbc.Row([
            dbc.Col([
                html.H6('Profit from running asset on monring phrase only',style={'font-weight':'bold'})
            ],width=3),
            dbc.Col([
                html.Div(f'$ {df["Asset_p1($)"].sum()-(365*threshold):,.2f}',),
            ],width=1,style={'text-align':'left','font-weight':'bold'}),
            dbc.Col(html.Div(),width=1),
            dbc.Col([
                html.H6('Profit from running asset on afternoon phrase only',style={'font-weight':'bold'})
            ],width=3),
            dbc.Col([
                html.Div(f'$ {df["Asset_p2($)"].sum()-(365*threshold):,.2f}',),
            ],width=1,style={'text-align':'left','font-weight':'bold'}),
            dbc.Col([
                html.Div(f'$ {(df["Asset_p1($)"].sum()-(365*threshold)) + (df["Asset_p2($)"].sum()-(365*threshold)):,.2f}',),
            ],width=2,style={'text-align':'right','font-weight':'bold'}),
        ]),

        dbc.Row([
            dbc.Col([
                html.H6('Number of Asset run cycle on monring phrase only')
            ],width=3),
            dbc.Col([
                html.Div(f'365',),
            ],width=1,style={'text-align':'left',}),
            dbc.Col(html.Div(),width=1),
            dbc.Col([
                html.H6('Number of Asset run cycle on afternoon phrase only')
            ],width=3),
            dbc.Col([
                html.Div(f'365',),
            ],width=1,style={'text-align':'left',}),
            dbc.Col([
                html.Div(f'{365*2}',),
            ],width=2,style={'text-align':'right',}),
        ]),

        html.Br(),
        html.H5('CfD Summary'),

        dbc.Row([
            dbc.Col([
                html.H6('Profit from CFD1 only',style={'font-weight':'bold'})
            ],width=3),
            dbc.Col([
                html.Div(f'$ {df["CFD1($)"].sum():,.2f}',),
            ],width=1,style={'text-align':'left','font-weight':'bold'}),
            dbc.Col(html.Div(),width=1),
            dbc.Col([
                html.H6('Profit from CFD2 only',style={'font-weight':'bold'})
            ],width=3),
            dbc.Col([
                html.Div(f'$ {df["CFD2($)"].sum():,.2f}',),
            ],width=1,style={'text-align':'left','font-weight':'bold'}),
            dbc.Col([
                html.Div(f'$ {df["CFD1($)"].sum() + df["CFD2($)"].sum():,.2f}',),
            ],width=2,style={'text-align':'right','font-weight':'bold'}),
        ]),

        html.Br(),
        html.H5('Asset & CfD Combination Summary'),

        dbc.Row([
            dbc.Col([
                html.H6('Profit from CFD1 and Asset running every morning',style={'font-weight':'bold'})
            ],width=3),
            dbc.Col([
                html.Div(f'$ {df["CFD1($)"].sum()+(df["Asset_p1($)"].sum()-(365*threshold)):,.2f}',),
            ],width=1,style={'text-align':'left','font-weight':'bold'}),
            dbc.Col(html.Div(),width=1),
            dbc.Col([
                html.H6('Profit from CFD2 and Asset running every afternoon',style={'font-weight':'bold'})
            ],width=3),
            dbc.Col([
                html.Div(f'$ {df["CFD2($)"].sum()+(df["Asset_p2($)"].sum()-(365*threshold)):,.2f}',),
            ],width=1,style={'text-align':'left','font-weight':'bold'}),
            dbc.Col([
                html.Div(f'$ {df["CFD1($)"].sum() + df["CFD2($)"].sum()+(df["Asset_p1($)"].sum()-(365*threshold))+(df["Asset_p2($)"].sum()-(365*threshold)):,.2f}',),
            ],width=2,style={'text-align':'right','font-weight':'bold'}),
        ]),

        html.Br(),
        html.H5('Asset & CfD Optimisation Summary'),

        dbc.Row([
            dbc.Col([
                html.H6('Number of Asset run cycle on monring phrase only')
            ],width=3),
            dbc.Col([
                html.Div(f'{df["Ph1_Asset_run"].sum()}',),
            ],width=1,style={'text-align':'left',}),
            dbc.Col(html.Div(),width=1),
            dbc.Col([
                html.H6('Number of Asset run cycle on afternoon phrase only')
            ],width=3),
            dbc.Col([
                html.Div(f'{df["Ph2_Asset_run"].sum()}',),
            ],width=1,style={'text-align':'left',}),
            dbc.Col([
                html.Div(f'{df["Ph1_Asset_run"].sum()+df["Ph2_Asset_run"].sum()}',),
            ],width=2,style={'text-align':'right',}),
        ]),

        dbc.Row([
            dbc.Col([
                html.H6('Revenue from Optimised CFD1 and Asset morning phrase')
            ],width=3),
            dbc.Col([
                html.Div(f'$ {df["Phrase1($)"].sum():,.2f}',),
            ],width=1,style={'text-align':'left',}),
            dbc.Col(html.Div(),width=1),
            dbc.Col([
                html.H6('Revenue from Optimised CFD2 and Asset afternoon phrase')
            ],width=3),
            dbc.Col([
                html.Div(f'$ {df["Phrase2($)"].sum():,.2f}',),
            ],width=1,style={'text-align':'left',}),
            dbc.Col([
                html.Div(f'$ {df["Phrase1($)"].sum()+df["Phrase2($)"].sum():,.2f}',),
            ],width=2,style={'text-align':'right',}),
        ]),

        dbc.Row([
            dbc.Col([
                html.H6('Cost from running asset on monring phrase')
            ],width=3),
            dbc.Col([
                html.Div(f'$ {df["Ph1_Asset_run"].sum()*threshold:,.2f}',),
            ],width=1,style={'text-align':'left','text-decoration': 'underline'}),
            dbc.Col(html.Div(),width=1),
            dbc.Col([
                html.H6('Cost from running asset on afternoon phrase')
            ],width=3),
            dbc.Col([
                html.Div(f'$ {df["Ph2_Asset_run"].sum()*threshold:,.2f}',),
            ],width=1,style={'text-align':'left','text-decoration': 'underline'}),
            dbc.Col([
                html.Div(f'$ {(df["Ph1_Asset_run"].sum()*threshold)+(df["Ph2_Asset_run"].sum()*threshold):,.2f}',),
            ],width=2,style={'text-align':'right',}),
        ]),

        dbc.Row([
            dbc.Col([
                html.H6('Profit from Optimised CFD1 and Asset morning phrase',style={'font-weight':'bold'})
            ],width=3),
            dbc.Col([
                html.Div(f'$ {df["Phrase1($)"].sum()-(df["Ph1_Asset_run"].sum()*threshold):,.2f}',),
            ],width=1,style={'text-align':'left','font-weight':'bold'}),
            dbc.Col(html.Div(),width=1),
            dbc.Col([
                html.H6('Profit from Optimised CFD2 and Asset afternoon phrase',style={'font-weight':'bold'})
            ],width=3),
            dbc.Col([
                html.Div(f'$ {df["Phrase2($)"].sum()-(df["Ph2_Asset_run"].sum()*threshold):,.2f}',),
            ],width=1,style={'text-align':'left','font-weight':'bold'}),
            dbc.Col([
                html.Div(f'$ {(df["Phrase1($)"].sum()-(df["Ph1_Asset_run"].sum()*threshold))+(df["Phrase2($)"].sum()-(df["Ph2_Asset_run"].sum()*threshold)):,.2f}',),
            ],width=2,style={'text-align':'right','font-weight':'bold'}),
        ]),

        html.Br(),html.Br(),
        html.H5('The optimisation algorithm is as follow:'),
        html.Div('+ Asset run value above Cost per Cycle: Combine CfD with Asset run.',style={'font-style': 'italic','color':'blue'}),
        html.Div('+ Asset run value below Cost per Cycle: Only use CfD, no asset run.',style={'font-style': 'italic','color':'blue'}),
        
    ],fluid=True)
    return summary

@callback(
    Output(component_id='daily_table', component_property='children'),
    Input(component_id='year_sel', component_property='value'),
    Input(component_id='threshold', component_property='value'),
    Input(component_id='buy_sel1', component_property='value'),
    Input(component_id='sell_sel1', component_property='value'),
    Input(component_id='buy_sel2', component_property='value'),
    Input(component_id='sell_sel2', component_property='value'),
)
def daily_table_update(year,threshold,buy1,sell1,buy2,sell2):
    threshold = float(threshold)
    df = df_preparation(year,threshold,buy1,sell1,buy2,sell2)
    df['Trading_Date'] = df['Trading_Date'].dt.date
    datatbl = dash_table.DataTable(
        id='datatable',
        columns=[
            {"name": i, "id": i, "deletable": False, "selectable": True, "hideable": False, "type":"any"}
            # if i == "Trading_Date"
            if i == 'Ph1_Asset_run' or i == 'Ph2_Asset_run' or i == "Trading_Date"
            else {"name": i, "id": i, "deletable": False, "selectable": True, 
                  "hideable": True, "type":"numeric", "format":money}
            for i in df.columns
        ],
        data=df.to_dict('records'),  # the contents of the table
        editable=False,              # allow editing of data inside all cells
        filter_action="native",     # allow filtering of data by user ('native') or not ('none')
        sort_action="native",       # enables data to be sorted per-column by user or not ('none')
        sort_mode="multi",         # sort across 'multi' or 'single' columns
        column_selectable="multi",  # allow users to select 'multi' or 'single' columns
        row_selectable="multi",     # allow users to select 'multi' or 'single' rows
        row_deletable=False,         # choose if user can delete a row (True) or not (False)
        selected_columns=[],        # ids of columns that user selects
        selected_rows=[],           # indices of rows that user selects
        page_action="none",       # all data is passed to the table up-front or not ('none')
        fixed_rows={'headers': True},
        hidden_columns=['Asset_mbuy($)','Asset_msell($)','Asset_abuy($)','Asset_esell($)',
                        'CFD1_mbuy_bCFD','CFD1_mbuy_sSpot','CFD1_msell_sCFD','CFD1_msell_bSpot',
                        'CFD2_abuy_bCFD','CFD2_abuy_sSpot','CFD2_esell_sCFD','CFD2_esell_bSpot'],
        # page_current=0,             # page number that user is on
        # page_size=6,                # number of rows visible per page
        style_table={'height': '600px','overflowY': 'auto','overflowX': 'auto'},
        style_header={'backgroundColor': '#347deb','color': 'white','font-weight':'bold'},
        style_cell={                # ensure adequate header width when text is shorter than cell's text
            'font-family':'sans-serif', 'minWidth': 85, 'maxWidth': 85, 'width': 85
        },
        style_data={                # overflow cells' content into multiple lines
            'whiteSpace': 'normal',
            'height': 'auto'
        }
    ),
    return datatbl


# Tab 2
@callback(
    Output(component_id='analysis_sum_tab2', component_property='children'),
    Input(component_id='year_sel_tab2', component_property='value'),
    Input(component_id='threshold_tab2', component_property='value'),
    Input(component_id='buy_sel1_tab2', component_property='value'),
    Input(component_id='sell_sel1_tab2', component_property='value'),
    Input(component_id='buy_sel2_tab2', component_property='value'),
    Input(component_id='sell_sel2_tab2', component_property='value'),
)
def analysis_sum_update_tab2(year,threshold,buy1,sell1,buy2,sell2):
    threshold = float(threshold)
    df = df_preparation2(year,threshold,buy1,sell1,buy2,sell2)
    summary = dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H4('Phrase 1')
            ],width=3),
            dbc.Col([
                html.Div(f'',),
            ],width=1,style={'text-align':'left',}),
            dbc.Col(html.Div(),width=1),
            dbc.Col([
                html.H4('Phrase 2')
            ],width=3),
            dbc.Col([
                html.Div(f'',),
            ],width=1,style={'text-align':'left',}),
            dbc.Col([
                html.H4(f'Total',),
            ],width=2,style={'text-align':'right',}),
        ]),

        html.Br(),
        html.H5('Asset Running Summary'),

        dbc.Row([
            dbc.Col([
                html.H6('Revenue from running asset on monring phrase only')
            ],width=3),
            dbc.Col([
                html.Div(f'$ {df["Asset_p1($)"].sum():,.2f}',),
            ],width=1,style={'text-align':'left',}),
            dbc.Col(html.Div(),width=1),
            dbc.Col([
                html.H6('Revenue from running asset on afternoon phrase only')
            ],width=3),
            dbc.Col([
                html.Div(f'$ {df["Asset_p2($)"].sum():,.2f}',),
            ],width=1,style={'text-align':'left',}),
            dbc.Col([
                html.Div(f'$ {df["Asset_p1($)"].sum()+df["Asset_p2($)"].sum():,.2f}',),
            ],width=2,style={'text-align':'right',}),
        ]),
        
        dbc.Row([
            dbc.Col([
                html.H6('Cost from running asset on monring phrase only')
            ],width=3),
            dbc.Col([
                html.Div(f'$ {365*threshold:,.2f}',),
            ],width=1,style={'text-align':'left','text-decoration': 'underline'}),
            dbc.Col(html.Div(),width=1),
            dbc.Col([
                html.H6('Cost from running asset on afternoon phrase only')
            ],width=3),
            dbc.Col([
                html.Div(f'$ {365*threshold:,.2f}',),
            ],width=1,style={'text-align':'left','text-decoration': 'underline'}),
            dbc.Col([
                html.Div(f'$ {365*threshold*2:,.2f}',),
            ],width=2,style={'text-align':'right',}),
        ]),

   
        dbc.Row([
            dbc.Col([
                html.H6('Profit from running asset on monring phrase only',style={'font-weight':'bold'})
            ],width=3),
            dbc.Col([
                html.Div(f'$ {df["Asset_p1($)"].sum()-(365*threshold):,.2f}',),
            ],width=1,style={'text-align':'left','font-weight':'bold'}),
            dbc.Col(html.Div(),width=1),
            dbc.Col([
                html.H6('Profit from running asset on afternoon phrase only',style={'font-weight':'bold'})
            ],width=3),
            dbc.Col([
                html.Div(f'$ {df["Asset_p2($)"].sum()-(365*threshold):,.2f}',),
            ],width=1,style={'text-align':'left','font-weight':'bold'}),
            dbc.Col([
                html.Div(f'$ {(df["Asset_p1($)"].sum()-(365*threshold)) + (df["Asset_p2($)"].sum()-(365*threshold)):,.2f}',),
            ],width=2,style={'text-align':'right','font-weight':'bold'}),
        ]),

        dbc.Row([
            dbc.Col([
                html.H6('Number of Asset run cycle on monring phrase only')
            ],width=3),
            dbc.Col([
                html.Div(f'365',),
            ],width=1,style={'text-align':'left',}),
            dbc.Col(html.Div(),width=1),
            dbc.Col([
                html.H6('Number of Asset run cycle on afternoon phrase only')
            ],width=3),
            dbc.Col([
                html.Div(f'365',),
            ],width=1,style={'text-align':'left',}),
            dbc.Col([
                html.Div(f'{365*2}',),
            ],width=2,style={'text-align':'right',}),
        ]),

        html.Br(),
        html.H5('CfD Summary'),

        dbc.Row([
            dbc.Col([
                html.H6('Profit from CFD1 only',style={'font-weight':'bold'})
            ],width=3),
            dbc.Col([
                html.Div(f'$ {df["CFD1($)"].sum():,.2f}',),
            ],width=1,style={'text-align':'left','font-weight':'bold'}),
            dbc.Col(html.Div(),width=1),
            dbc.Col([
                html.H6('Profit from CFD2 only',style={'font-weight':'bold'})
            ],width=3),
            dbc.Col([
                html.Div(f'$ {df["CFD2($)"].sum():,.2f}',),
            ],width=1,style={'text-align':'left','font-weight':'bold'}),
            dbc.Col([
                html.Div(f'$ {df["CFD1($)"].sum() + df["CFD2($)"].sum():,.2f}',),
            ],width=2,style={'text-align':'right','font-weight':'bold'}),
        ]),

        html.Br(),
        html.H5('Asset & CfD Combination Summary'),

        dbc.Row([
            dbc.Col([
                html.H6('Profit from CFD1 and Asset running every morning',style={'font-weight':'bold'})
            ],width=3),
            dbc.Col([
                html.Div(f'$ {df["CFD1($)"].sum()+(df["Asset_p1($)"].sum()-(365*threshold)):,.2f}',),
            ],width=1,style={'text-align':'left','font-weight':'bold'}),
            dbc.Col(html.Div(),width=1),
            dbc.Col([
                html.H6('Profit from CFD2 and Asset running every afternoon',style={'font-weight':'bold'})
            ],width=3),
            dbc.Col([
                html.Div(f'$ {df["CFD2($)"].sum()+(df["Asset_p2($)"].sum()-(365*threshold)):,.2f}',),
            ],width=1,style={'text-align':'left','font-weight':'bold'}),
            dbc.Col([
                html.Div(f'$ {df["CFD1($)"].sum() + df["CFD2($)"].sum()+(df["Asset_p1($)"].sum()-(365*threshold))+(df["Asset_p2($)"].sum()-(365*threshold)):,.2f}',),
            ],width=2,style={'text-align':'right','font-weight':'bold'}),
        ]),

        html.Br(),
        html.H5('Asset & CfD Optimisation Summary'),

        dbc.Row([
            dbc.Col([
                html.H6('Number of Asset run cycle on monring phrase only')
            ],width=3),
            dbc.Col([
                html.Div(f'{df["Ph1_Asset_run"].sum()}',),
            ],width=1,style={'text-align':'left',}),
            dbc.Col(html.Div(),width=1),
            dbc.Col([
                html.H6('Number of Asset run cycle on afternoon phrase only')
            ],width=3),
            dbc.Col([
                html.Div(f'{df["Ph2_Asset_run"].sum()}',),
            ],width=1,style={'text-align':'left',}),
            dbc.Col([
                html.Div(f'{df["Ph1_Asset_run"].sum()+df["Ph2_Asset_run"].sum()}',),
            ],width=2,style={'text-align':'right',}),
        ]),

        dbc.Row([
            dbc.Col([
                html.H6('Revenue from Optimised CFD1 and Asset morning phrase')
            ],width=3),
            dbc.Col([
                html.Div(f'$ {df["Phrase1($)"].sum():,.2f}',),
            ],width=1,style={'text-align':'left',}),
            dbc.Col(html.Div(),width=1),
            dbc.Col([
                html.H6('Revenue from Optimised CFD2 and Asset afternoon phrase')
            ],width=3),
            dbc.Col([
                html.Div(f'$ {df["Phrase2($)"].sum():,.2f}',),
            ],width=1,style={'text-align':'left',}),
            dbc.Col([
                html.Div(f'$ {df["Phrase1($)"].sum()+df["Phrase2($)"].sum():,.2f}',),
            ],width=2,style={'text-align':'right',}),
        ]),

        dbc.Row([
            dbc.Col([
                html.H6('Cost from running asset on monring phrase')
            ],width=3),
            dbc.Col([
                html.Div(f'$ {df["Ph1_Asset_run"].sum()*threshold:,.2f}',),
            ],width=1,style={'text-align':'left','text-decoration': 'underline'}),
            dbc.Col(html.Div(),width=1),
            dbc.Col([
                html.H6('Cost from running asset on afternoon phrase')
            ],width=3),
            dbc.Col([
                html.Div(f'$ {df["Ph2_Asset_run"].sum()*threshold:,.2f}',),
            ],width=1,style={'text-align':'left','text-decoration': 'underline'}),
            dbc.Col([
                html.Div(f'$ {(df["Ph1_Asset_run"].sum()*threshold)+(df["Ph2_Asset_run"].sum()*threshold):,.2f}',),
            ],width=2,style={'text-align':'right',}),
        ]),

        dbc.Row([
            dbc.Col([
                html.H6('Profit from Optimised CFD1 and Asset morning phrase',style={'font-weight':'bold'})
            ],width=3),
            dbc.Col([
                html.Div(f'$ {df["Phrase1($)"].sum()-(df["Ph1_Asset_run"].sum()*threshold):,.2f}',),
            ],width=1,style={'text-align':'left','font-weight':'bold'}),
            dbc.Col(html.Div(),width=1),
            dbc.Col([
                html.H6('Profit from Optimised CFD2 and Asset afternoon phrase',style={'font-weight':'bold'})
            ],width=3),
            dbc.Col([
                html.Div(f'$ {df["Phrase2($)"].sum()-(df["Ph2_Asset_run"].sum()*threshold):,.2f}',),
            ],width=1,style={'text-align':'left','font-weight':'bold'}),
            dbc.Col([
                html.Div(f'$ {(df["Phrase1($)"].sum()-(df["Ph1_Asset_run"].sum()*threshold))+(df["Phrase2($)"].sum()-(df["Ph2_Asset_run"].sum()*threshold)):,.2f}',),
            ],width=2,style={'text-align':'right','font-weight':'bold'}),
        ]),

        html.Br(),html.Br(),
        html.H5('The optimisation algorithm is as follow:'),
        html.Div('+ Asset run value above Cost per Cycle: Combine CfD with Asset run.',style={'font-style': 'italic','color':'blue'}),
        html.Div('+ Asset run value below Cost per Cycle: Only use CfD, no asset run.',style={'font-style': 'italic','color':'blue'}),
    ],fluid=True)
    return summary

@callback(
    Output(component_id='daily_table_tab2', component_property='children'),
    Input(component_id='year_sel_tab2', component_property='value'),
    Input(component_id='threshold_tab2', component_property='value'),
    Input(component_id='buy_sel1_tab2', component_property='value'),
    Input(component_id='sell_sel1_tab2', component_property='value'),
    Input(component_id='buy_sel2_tab2', component_property='value'),
    Input(component_id='sell_sel2_tab2', component_property='value'),
)
def daily_table_update_tab2(year,threshold,buy1,sell1,buy2,sell2):
    threshold = float(threshold)
    df = df_preparation2(year,threshold,buy1,sell1,buy2,sell2)
    df['Trading_Date'] = df['Trading_Date'].dt.date
    datatbl = dash_table.DataTable(
        id='datatable',
        columns=[
            {"name": i, "id": i, "deletable": False, "selectable": True, "hideable": False, "type":"any"}
            # if i == "Trading_Date"
            if i == 'Ph1_Asset_run' or i == 'Ph2_Asset_run' or i == "Trading_Date"
            else {"name": i, "id": i, "deletable": False, "selectable": True, 
                  "hideable": True, "type":"numeric", "format":money}
            for i in df.columns
        ],
        data=df.to_dict('records'),  # the contents of the table
        editable=False,              # allow editing of data inside all cells
        filter_action="native",     # allow filtering of data by user ('native') or not ('none')
        sort_action="native",       # enables data to be sorted per-column by user or not ('none')
        sort_mode="multi",         # sort across 'multi' or 'single' columns
        column_selectable="multi",  # allow users to select 'multi' or 'single' columns
        row_selectable="multi",     # allow users to select 'multi' or 'single' rows
        row_deletable=False,         # choose if user can delete a row (True) or not (False)
        selected_columns=[],        # ids of columns that user selects
        selected_rows=[],           # indices of rows that user selects
        page_action="none",       # all data is passed to the table up-front or not ('none')
        fixed_rows={'headers': True},
        hidden_columns=['Asset_mbuy($)','Asset_msell($)','Asset_abuy($)','Asset_esell($)',
                        'CFD1_msell_sCFD','CFD1_msell_bSpot','CFD2_esell_sCFD','CFD2_esell_bSpot'],
        # page_current=0,             # page number that user is on
        # page_size=6,                # number of rows visible per page
        style_table={'height': '600px','overflowY': 'auto','overflowX': 'auto'},
        style_header={'backgroundColor': '#347deb','color': 'white','font-weight':'bold'},
        style_cell={                # ensure adequate header width when text is shorter than cell's text
            'font-family':'sans-serif', 'minWidth': 85, 'maxWidth': 85, 'width': 85
        },
        style_data={                # overflow cells' content into multiple lines
            'whiteSpace': 'normal',
            'height': 'auto'
        }
    ),
    return datatbl

app = dashapp.server.wsgi_app

if __name__ == "__main__":
    dashapp.run_server(host='0.0.0.0', port=80, debug=False)
