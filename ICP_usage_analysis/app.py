import dash                                     
from dash import Dash, dcc, html, Input, Output, callback,dash_table
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from datetime import date
from datetime import timedelta
import pandas as pd
import numpy as np
import os
import statsmodels.api as sm

dashapp = Dash(__name__,
    external_stylesheets=[dbc.themes.LUX, dbc.icons.FONT_AWESOME]
)

# Global Variables

# Images
LOGO = 'assets/logo.jpg'
ERROR404 = 'assets/AA-4.png'

#Colors 
COLR1 = '#E74E1C' # Orange
COLR2 = '#00A599' # Light Teal
COLR3 = '#EFA246' # Yellow
COLR4 = '#3F9C35' # Green
COLR5 = '#005B82' # Teal
COLR6 = '#A5ACAF' # Gray
COLR7 = '#6E267B' # Purple
COLR8 = '#404545' # DarkGray

# Year 2022 number of days
HC_WD = 131 # High consumption weekday
HC_WE = 53  # High consumption weekend
LC_WD = 129 # Low consumption weekday
LC_WE = 52  # Low consumption weekend


# profile path
dir_path = r'data/profiles/'
# list files
filenames = os.listdir(dir_path)
profile_vals =[]
for filename in filenames:
    number = filename.strip('icp.csv')
    val = filename.strip('.csv')
    profile_vals.append({'label':f'ICP Profile {number}', 'value':f'{val}'})

# Power plan variables
plan_vals =[
    {'label':'Contact BasicSimple', 'value':'ctct_1'},
    {'label':'Ecotricity Eco Saver', 'value':'ecot_1'},
    {'label':'Electric Kiwi Kiwi', 'value':'elik_2'},
    {'label':'Electric Kiwi Loyal', 'value':'elik_1'},
    {'label':'Electric Kiwi Move Master', 'value':'elik_3'},
    {'label':'Electric Kiwi Stay Ahead 200', 'value':'elik_4'},
    {'label':'Energy Online Day/Night', 'value':'geol_2'},
    {'label':'Energy Online Standard', 'value':'geol_1'},
    {'label':'Flick Flat', 'value':'flik_2'},
    {'label':'Flick OffPeak', 'value':'flik_1'},
    {'label':'Genesis Basic', 'value':'gene_1'},
    {'label':'Genesis Plus', 'value':'gene_2'},
    {'label':'Mercury 1yrFixed', 'value':'merc_2'},
    {'label':'Mercury 2yrFixed', 'value':'merc_3'},
    {'label':'Mercury OpenTerm', 'value':'merc_1'},
    {'label':'Meridian EV', 'value':'meri_2'},
    {'label':'Meridian Standard', 'value':'meri_1'},
    {'label':'Nova Standard', 'value':'nova_1'},
    {'label':'Pioneer Standard', 'value':'pion_1'},
    {'label':'PowerShop Standard', 'value':'psnz_1'},
    {'label':'Pulse Standard', 'value':'punz_1'},
    {'label':'TrustPower 24-hr', 'value':'trus_1'},
    {'label':'TrustPower Inclusive', 'value':'trus_2'},
    {'label':'Vocus Bundle', 'value':'swth_1'}
]

# Off-peak free hours variable 
hr_vals =[
    {'label':'00:00-01:00', 'value':'0,1'},
    {'label':'00:30-01:30', 'value':'1,2'},
    {'label':'01:00-02:00', 'value':'2,3'},
    {'label':'01:30-02:30', 'value':'3,4'},
    {'label':'02:00-03:00', 'value':'4,5'},
    {'label':'02:30-03:30', 'value':'5,6'},
    {'label':'03:00-04:00', 'value':'6,7'},
    {'label':'03:30-04:30', 'value':'7,8'},
    {'label':'04:00-05:00', 'value':'8,9'},
    {'label':'04:30-05:30', 'value':'9,10'},
    {'label':'05:00-06:00', 'value':'10,11'},
    {'label':'05:30-06:30', 'value':'11,12'},
    {'label':'06:00-07:00', 'value':'12,13'},
    {'label':'09:00-10:00', 'value':'18,19'},
    {'label':'09:30-10:30', 'value':'19,20'},
    {'label':'10:00-11:00', 'value':'20,21'},
    {'label':'10:30-11:30', 'value':'21,22'},
    {'label':'11:00-12:00', 'value':'22,23'},
    {'label':'11:30-12:30', 'value':'23,24'},
    {'label':'12:00-13:00', 'value':'24,25'},
    {'label':'12:30-13:30', 'value':'25,26'},    
    {'label':'13:00-14:00', 'value':'26,27'},
    {'label':'13:30-14:30', 'value':'27,28'},
    {'label':'14:00-15:00', 'value':'28,29'},
    {'label':'14:30-15:30', 'value':'29,30'},
    {'label':'15:00-16:00', 'value':'30,31'},
    {'label':'15:30-16:30', 'value':'31,32'},  
    {'label':'16:00-17:00', 'value':'32,33'},
    {'label':'21:00-22:00', 'value':'42,43'},
    {'label':'21:30-22:30', 'value':'43,44'},
    {'label':'22:00-23:00', 'value':'44,45'},
    {'label':'22:30-23:30', 'value':'45,46'},
    {'label':'23:00-00:00', 'value':'46,47'}
]

# Trading Period to Time
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
    45:'22:00', 46:'22:30',47:'23:00', 48:'23:30'     
}

#  Update trading period format  
tptime_fix = {
    '0:00':'00:00',  '0:30':'00:30', '1:00':'01:00', '1:30':'01:30',
    '2:00':'02:00',  '2:30':'02:30', '3:00':'03:00', '3:30':'03:30',
    '4:00':'04:00',  '4:30':'04:30','5:00':'05:00', '5:30':'05:30',
    '6:00':'06:00', '6:30':'06:30','7:00':'07:00', '7:30':'07:30',
    '8:00':'08:00', '8:30':'08:30','9:00':'09:00', '9:30':'09:30',
}

# Default Profile value
default_val = str(profile_vals[0]).split(', ',1)[1].strip("'value : '}")

# Profile selection dropbox
profile_dbox = dbc.Row([
    dbc.Col(html.H6("Select ICP's profile"),align='end',width=4, style={'padding-bottom':'5px'}),
        dbc.Col(dcc.Dropdown(id='profile_selector', multi=False, 
        value=default_val, options=profile_vals,clearable=False),width=4)
        ],justify='end')

# Heading row
heading_row = html.Div([
        dbc.Row(html.H2("ICP's Electricity Usage Analysis"),style={'text-align':'center'}),
        html.Br(),
        dbc.Row(dbc.Col(profile_dbox,width=5),justify='end'),

        # Data store
        dcc.Store(id='store-profile', data=[], storage_type='memory'),
        dcc.Store(id='store-plan', data=[], storage_type='memory')

    ],style={'padding-left':'43px','padding-right':'43px','padding-top':'30px'})

# ------------------------------------------------------------------------------
# Data Loading
def weather_cleaning():

    # Loading file
    ccweather = pd.read_csv('data/CC_weather20192023.csv',engine='python',
                            skiprows=15,skipfooter=7)

    # Drop unwanted columns
    ccweather = ccweather.drop(ccweather.columns[[3,5,6,7,8,9,10,11]],axis=1)

    # Convert missing value placeholder - to None

    ccweather.loc[ccweather['Tmax(C)']=='-','Tmax(C)']= None
    ccweather.loc[ccweather['Tmin(C)']=='-','Tmin(C)']= None

    # Convert string to float
    ccweather[['Tmax(C)','Tmin(C)']] = ccweather[['Tmax(C)','Tmin(C)']].astype(float)

    # Convert string to date
    ccweather['Date(NZST)'] = pd.to_datetime(ccweather['Date(NZST)']
                                            ,format = '%d/%m/%y').dt.date

    # Group by and calculate mean by date
    ccweather = ccweather.groupby('Date(NZST)',as_index=False).mean(numeric_only = True)

    # Compute the average temperature for each day
    ccweather['Tavg(C)'] = ccweather[['Tmax(C)','Tmin(C)']].mean(axis=1)
    ccweather = ccweather.drop('Station',axis=1)
    ccweather[['Tmax(C)','Tmin(C)','Tavg(C)']] = ccweather[['Tmax(C)','Tmin(C)',
        'Tavg(C)']].round(decimals = 2)

    return ccweather

ccweather = weather_cleaning()


# ------------------------------------------------------------------------------
# Functions

# Hex to RGB function
def hex_to_rgb(hex_color: str) -> tuple:
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = hex_color * 2
    return int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)

# Data preparation function
def detail_df(data): 
    # Convert data from JSON to pandas
    rawdf = pd.DataFrame(data)
    # Data preparation
    rawdf['Date'] = pd.to_datetime(rawdf['Date'])
    # Subset the maximum one year data 
    startdate = rawdf['Date'].max() - timedelta(days=364)
    df = rawdf[(rawdf['Date'] >= startdate) 
            & (rawdf['Date'] <= rawdf['Date'].max())]
    return df

# Data preparation function
def daily_df(data):
    df = detail_df(data)
    # Group dataframe by day
    df_daily = df.groupby('Date',as_index=False).sum()

    # Adding Day of Week column
    df_daily['DoW'] = df_daily['Date'].dt.day_name()

    # Adding color column to highlight weekend
    df_daily['WeekendC'] = [COLR3 if x in ['Saturday','Sunday'] else COLR6 for x in 
                            df_daily['DoW']]
    return df_daily

# Data preparation function
def weather_df(data):
    # Prepare data
    df = detail_df(data)
    #CC weather
    weatherdf = ccweather[(pd.to_datetime(ccweather['Date(NZST)']) >= df['Date'].min()) 
        & (pd.to_datetime(ccweather['Date(NZST)']) <= df['Date'].max())]
    return weatherdf

# Data preparation function
def cemission_df():
    # Function to create pattern dataframe
    def mmm(dataframe):
        def qtl(x):
            return x.quantile(0.35)
        dfdetail = dataframe.copy()
        dfdetail['isWE'] = False
        dfdetail.loc[dfdetail['Date'].dt.day_of_week >4,'isWE'] = True
        # dfdetail['isWE'] = dfdetail['Date'].dt.day_of_week >4
        dfdetail = (dfdetail.groupby(['isWE','Trading_Period'],as_index=False)
                    .agg({'Carbon_Intensity(g/KWh)':[qtl,'min','max']}))
        dfdetail.columns = dfdetail.columns.droplevel(0)
        dfdetail.columns = ['isWE','Trading_Period','CPattern','Min','Max']
        dfdetail[['CPattern','Min','Max']] = dfdetail[['CPattern','Min','Max']].round(decimals=3)
        return dfdetail
    
    
    # Load table from database
    carbon_int = pd.read_csv('data/daily_ems.csv')
    # Convert to datetime
    carbon_int['Trading_Date'] = pd.to_datetime(carbon_int['Trading_Date'])
    # Filter year 2022 only
    carbon_int = carbon_int[carbon_int['Trading_Date'].dt.year > 2021]
    # Take a subset of carbon intensity only
    carbon_int = carbon_int[['Trading_Date'] +
                (carbon_int.columns[carbon_int.columns.str.startswith('c_int')].to_list()) 
                ].copy()
    
    # Convert wide to long dataframe
    cbint_df = pd.melt(carbon_int,id_vars='Trading_Date',var_name= 'Trading_Period' ,
        value_name='Carbon_Intensity(g/KWh)', 
        value_vars=carbon_int.columns[carbon_int.columns.str.startswith('c_int')].to_list())
    # Convert trading period to integer
    cbint_df['Trading_Period'] = cbint_df['Trading_Period'].str.replace('c_int','')
    cbint_df['Trading_Period'] = cbint_df['Trading_Period'].astype(int)

    # Filter to 48 trading period only
    cbint_df = cbint_df[cbint_df['Trading_Period']<=48]
    # Convert trading period to time slot
    cbint_df = cbint_df.replace({'Trading_Period':tp_time})
    # Rename trading date to date
    cbint_df =  cbint_df.rename({'Trading_Date': 'Date'}, axis=1)

    # Create peak period dataframe
    cpeak_df = cbint_df[(cbint_df['Date'].dt.month>4)&(cbint_df['Date'].dt.month<11)]
    # Create trough period dataframe
    ctrough_df = cbint_df[(cbint_df['Date'].dt.month<=4)|(cbint_df['Date'].dt.month>=11)]

    cpeak_pattern = mmm(cpeak_df)
    ctrough_pattern = mmm(ctrough_df)

    return cpeak_pattern, ctrough_pattern

# Function to create Min Max Median dataframe 
def mmm_df(dataframe):
    def q60(x):
        return x.quantile(0.60)
    dfdetail = dataframe
    dfdetail['isWE'] = dfdetail['Date'].dt.day_of_week >4
    dfdetail = (dfdetail.groupby(['isWE','Trading_Period'],as_index=False)
                .agg({'Consumption(KWh)':[q60,'min','max']}))
    dfdetail.columns = dfdetail.columns.droplevel(0)
    dfdetail.columns = ['isWE','Trading_Period','Pattern','Min','Max']
    dfdetail[['Pattern','Min','Max']] = dfdetail[['Pattern','Min','Max']].round(decimals=3)
    return dfdetail

# Function to create Peak Dataframe
def peak_dataframe(df,df_daily):
    df_daily = df_daily[(df_daily['Date'].dt.month>4)&(df_daily['Date'].dt.month<11)]

    # List of days which consumption is in the range of 10%-90% of the 
    # distribution, so extrem values won't affect the pattern later
    filtered_date = (df_daily.loc[((df_daily['Consumption(KWh)']>= 
        np.quantile(df_daily['Consumption(KWh)'],0.25))&(df_daily['Consumption(KWh)']<= 
        np.quantile(df_daily['Consumption(KWh)'],0.75))), 'Date'])

    # Apply the filter to detail data to avoid the interference of holidays or extrem days
    May_Oct = df.merge(filtered_date, on='Date')
    return May_Oct

#Function to create Trough Dataframe
def trough_dataframe(df,df_daily):
    # Filter the daily dataframe (Nov to Apr) 
    df_daily = df_daily[(df_daily['Date'].dt.month<=4)|(df_daily['Date'].dt.month>=11)]

    # List of days which consumption is in the range of Quartile 1 - Q3 of the 
    # distribution
    filtered_date = (df_daily.loc[((df_daily['Consumption(KWh)']>= 
        np.quantile(df_daily['Consumption(KWh)'],0.25))&(df_daily['Consumption(KWh)']<= 
        np.quantile(df_daily['Consumption(KWh)'],0.75))), 'Date'])
    Nov_Apr = df.merge(filtered_date, on='Date')
    return Nov_Apr

# Create free hour dataframe
def fhour_df(hour):
    if hour is None:
        hr_list = [1]*48
        return pd.DataFrame(hr_list,columns=['Freehour'])
    else:
        hr_list = [1]*46
        fhs = hour.split(',')
        for fh in fhs:
            hr_list.insert(int(fh),0)
        return pd.DataFrame(hr_list,columns=['Freehour'])

# Function to create 4 periods dataframe
def split_df(data,plan):

    # Merge and split
    def mgsplt(data_df,plan_df,carbon_df):
        df = data_df.merge(plan_df,how='left',on=['isWE','Trading_Period'])
        df = df.merge(carbon_df,how='left',on=['isWE','Trading_Period'])

        mrgdf = df.iloc[:, [0,6,5,1,2,2]]
        mrgdf.columns = ['isWE','CI(g/KWh)','($/KWh)','Time','Pattern','Proposal']
        wd_df = mrgdf.loc[mrgdf['isWE']==False,['CI(g/KWh)','($/KWh)','Time',
                                                'Pattern','Proposal']]
        we_df = mrgdf.loc[mrgdf['isWE']==True,['CI(g/KWh)','($/KWh)','Time',
                                                'Pattern','Proposal']]

        return wd_df, we_df


    #Plan data processing
    plan_df = pd.DataFrame(plan)
    plan_df['isWE'] = plan_df['isWE'].astype(bool)

    #ICP data processing
    df = detail_df(data)
    df_daily = daily_df(data)

    peak_df = peak_dataframe(df,df_daily)
    peak_pattern = mmm_df(peak_df)

    trough_df = trough_dataframe(df,df_daily)
    trough_pattern = mmm_df(trough_df)

    # Carbon emission processing
    cpeak_df,ctrough_df = cemission_df()
    cpeak_df = cpeak_df[['isWE','Trading_Period','CPattern']].copy()
    ctrough_df = ctrough_df[['isWE','Trading_Period','CPattern']].copy()

    hcwd,hcwe = mgsplt(peak_pattern,plan_df,cpeak_df)
    lcwd,lcwe = mgsplt(trough_pattern,plan_df,ctrough_df)

    return hcwd,hcwe,lcwd,lcwe

# Functions to show summary cards
def indicators_card(df2):
    indicators = dbc.Col([
        dbc.Card([
            dbc.CardBody([
                html.P('Total Consumption',style={'textAlign':'center'}),
                html.H4(f"{df2['Consumption(KWh)'].sum():.3f} KWh",style={'textAlign':'center',
                    'color':COLR1})
                ])
        ]),

        html.Br(),

        dbc.Card([
            dbc.CardBody([
                html.P('Max Consumption',style={'textAlign':'center'}),
                html.H4(f"{df2['Consumption(KWh)'].max():.3f} KWh",style={'textAlign':'center',
                    'color':COLR1})
                ])
        ]),

        html.Br(),

        dbc.Card([
            dbc.CardBody([
                html.P('Min Consumption',style={'textAlign':'center'}),
                html.H4(f"{df2['Consumption(KWh)'].min():.3f} KWh",style={'textAlign':'center',
                    'color':COLR1})
                ])
        ])
    ])
    return indicators

# Function to plot the pattern charts
def grp_charts(dataframe):
    dfdetail = mmm_df(dataframe)

    xval_we = (dfdetail[dfdetail['isWE']==True])['Trading_Period']
    ymdn_we = (dfdetail[dfdetail['isWE']==True])['Pattern']
    ymin_we = (dfdetail[dfdetail['isWE']==True])['Min']
    ymax_we = (dfdetail[dfdetail['isWE']==True])['Max']

    xval_wd = (dfdetail[dfdetail['isWE']==False])['Trading_Period']
    ymdn_wd = (dfdetail[dfdetail['isWE']==False])['Pattern']
    ymin_wd = (dfdetail[dfdetail['isWE']==False])['Min']
    ymax_wd = (dfdetail[dfdetail['isWE']==False])['Max']


    fig = make_subplots(rows=2, cols=1, 
        subplot_titles=(f'Weekday Pattern - Total Consumption:{ymdn_wd.sum():.3f} KWh',
            f'Weekend Pattern - Total Consumption:{ymdn_we.sum():.3f} Kwh'),
        vertical_spacing=0.08,
        shared_xaxes=True)

    fig.add_trace(go.Scatter(
        name='Pattern', x=xval_wd, y=ymdn_wd,
        mode='lines+markers', 
        line=dict(color=COLR6),opacity= 1,
        marker=dict(symbol="diamond",size=4,color=COLR6)
    ),row =1,col =1)

    fig.add_trace(go.Scatter(
        name='Max Cons.',x=xval_wd,y=ymax_wd,
        mode='lines',marker=dict(color="#444"),line=dict(width=0),
        showlegend=False
    ),row =1,col =1)

    fig.add_trace(go.Scatter(
        name='Min Cons.',x=xval_wd,y=ymin_wd,
        mode='lines',marker=dict(color="#444"),line=dict(width=0),
        fillcolor=f'rgba{(*hex_to_rgb(COLR6), 0.1)}',
        fill='tonexty',showlegend=False
    ),row =1,col =1)
        
        
    fig.add_trace(go.Scatter(
        name='Pattern', x=xval_we, y=ymdn_we,
        mode='lines+markers', 
        line=dict(color=COLR3),opacity=0.7,
        marker=dict(symbol="diamond",size=4,color=COLR3)
    ),row =2,col =1)

    fig.add_trace(go.Scatter(
        name='Max Cons.',x=xval_we,y=ymax_we,
        mode='lines',marker=dict(color="#444"),line=dict(width=0),
        showlegend=False
    ),row =2,col =1)

    fig.add_trace(go.Scatter(
        name='Min Cons.',x=xval_we,y=ymin_we,
        mode='lines',marker=dict(color="#444"),line=dict(width=0),
        fillcolor=f'rgba{(*hex_to_rgb(COLR3), 0.1)}',
        fill='tonexty',showlegend=False
    ),row =2,col =1)

    for n in range (2):
        fig.layout.annotations[n].update(x=0,font_size=14,xanchor ='left') 
    fig.update_traces(xaxis='x2')
    fig.update_yaxes(title='Consumption(KWh)',showgrid=True, gridwidth=1, gridcolor='#f0f0f0')
    fig.update_layout(height = 600,
        xaxis_title = None,
        plot_bgcolor = '#FFFFFF',
        margin = dict(t=50,r=10),
        showlegend=False,
        hovermode='x unified',
        )

    return fig

# Function to plot the carbon emission pattern charts
def egrp_chart(dataframe):
    dfdetail = dataframe

    xval_we = (dfdetail[dfdetail['isWE']==True])['Trading_Period']
    ymdn_we = (dfdetail[dfdetail['isWE']==True])['CPattern']
    ymin_we = (dfdetail[dfdetail['isWE']==True])['Min']
    ymax_we = (dfdetail[dfdetail['isWE']==True])['Max']

    xval_wd = (dfdetail[dfdetail['isWE']==False])['Trading_Period']
    ymdn_wd = (dfdetail[dfdetail['isWE']==False])['CPattern']
    ymin_wd = (dfdetail[dfdetail['isWE']==False])['Min']
    ymax_wd = (dfdetail[dfdetail['isWE']==False])['Max']


    fig = make_subplots(rows=2, cols=1, 
        subplot_titles=('Weekday Pattern','Weekend Pattern'),
        vertical_spacing=0.08,
        shared_xaxes=True)

    fig.add_trace(go.Scatter(
        name='Emission Pattern', x=xval_wd, y=ymdn_wd,
        mode='lines+markers', 
        line=dict(color=COLR2),opacity= 0.5,
        marker=dict(symbol="diamond",size=4,color=COLR2)
    ),row =1,col =1)

    fig.add_trace(go.Scatter(
        name='Max Carbon Int.',x=xval_wd,y=ymax_wd,
        mode='lines',marker=dict(color="#444"),line=dict(width=0),
        showlegend=False
    ),row =1,col =1)

    fig.add_trace(go.Scatter(
        name='Min Carbon Int.',x=xval_wd,y=ymin_wd,
        mode='lines',marker=dict(color="#444"),line=dict(width=0),
        fillcolor=f'rgba{(*hex_to_rgb(COLR2), 0.1)}',
        fill='tonexty',showlegend=False
    ),row =1,col =1)
        
        
    fig.add_trace(go.Scatter(
        name='Emission Pattern', x=xval_we, y=ymdn_we,
        mode='lines+markers', 
        line=dict(color=COLR5),opacity=0.7,
        marker=dict(symbol="diamond",size=4,color=COLR5)
    ),row =2,col =1)

    fig.add_trace(go.Scatter(
        name='Max Carbon Int.',x=xval_we,y=ymax_we,
        mode='lines',marker=dict(color="#444"),line=dict(width=0),
        showlegend=False
    ),row =2,col =1)

    fig.add_trace(go.Scatter(
        name='Min Carbon Int.',x=xval_we,y=ymin_we,
        mode='lines',marker=dict(color="#444"),line=dict(width=0),
        fillcolor=f'rgba{(*hex_to_rgb(COLR5), 0.1)}',
        fill='tonexty',showlegend=False
    ),row =2,col =1)

    for n in range (2):
        fig.layout.annotations[n].update(x=0,font_size=14,xanchor ='left') 
    fig.update_traces(xaxis='x2')
    fig.update_yaxes(title='Carbon Intensity(g/KWh)',showgrid=True, gridwidth=1, gridcolor='#f0f0f0')
    fig.update_layout(height = 600,
        xaxis_title = None,
        plot_bgcolor = '#FFFFFF',
        margin = dict(t=50,r=10),
        showlegend=False,
        hovermode='x unified',
        )

    return fig

# Functions pattern adjust charts
def pattern_review(wddf,wedf):

    fig = make_subplots(rows=2, cols=1, 
        subplot_titles=('Weekday Pattern vs Proposal','Weekend Pattern vs vs Proposal'),
        vertical_spacing=0.15,
        shared_xaxes=True)

    fig.add_trace(go.Scatter(
        name='WD Pattern', x=wddf['Time'], y=wddf['Pattern'],
        mode='lines', fill='tozeroy', fillcolor= f'rgba{(*hex_to_rgb(COLR6), 0.1)}',
        line=dict(width = 0, color=COLR6)
    ),row =1,col =1)

    fig.add_trace(go.Scatter(
        name='WD Proposal', x=wddf['Time'], y=wddf['Proposal'],
        mode='lines+markers',
        line=dict(width = 1, color=COLR1),opacity= 1,
        marker=dict(symbol='triangle-down',size=6,color=COLR1),
    ),row =1,col =1)

    fig.add_trace(go.Scatter(
        name='WE Pattern', x=wedf['Time'], y=wedf['Pattern'],
        mode='lines', fill='tozeroy', fillcolor= f'rgba{(*hex_to_rgb(COLR3), 0.1)}',
        line=dict(width = 0, color=COLR3)
    ),row =2,col =1)

    fig.add_trace(go.Scatter(
        name='WE Proposal', x=wedf['Time'], y=wedf['Proposal'],
        mode='lines+markers',
        line=dict(width = 1, color=COLR3),opacity= 1,
        marker=dict(symbol='triangle-down',size=6,color=COLR3),
    ),row =2,col =1)

    for n in range (2):
        fig.layout.annotations[n].update(x=0,font_size=14,xanchor ='left') 
    fig.update_traces(xaxis='x2')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0')
    fig.update_layout(height = 500,
        xaxis_title = None,
        title = 'Usage Pattern vs Proposal Review',
        plot_bgcolor = '#FFFFFF',
        margin = dict(t=80,r=10),
        showlegend=True,
        legend=dict(orientation='h',yanchor='bottom',y=1.02,xanchor='right',x=1),
        hovermode='x unified',
        )

    return fig

# Data Table Function
def usage_adj_table(dataframe,name):
    df = dataframe
    table = dash_table.DataTable(
    id=f'dtable_{name}',
    columns=[
        {"name": i, "id": i, 'deletable': False, 'selectable': False, 
        'hideable': False,'editable':True} if i == "Proposal"
        else {"name": i, "id": i, 'deletable': False, 'selectable': False, 
        'hideable': False,'editable':False}
        for i in df.columns
    ],
    data=df.to_dict('records'), 
    fixed_rows={'headers': True}, 
    page_action='none',   
    style_table={'height': '302px', 'overflowY': 'auto'},
    style_header={'backgroundColor': f'rgba{(*hex_to_rgb(COLR6), 0.5)}',
                  'fontWeight': 'bold'},
    style_cell={   
        'fontSize':13, 'font-family':'sans-serif',      
        'minWidth': 30, 'maxWidth': 40, 'width': 35
    },
    style_cell_conditional=[    
        {
            'if': {'column_id': 'Time'},
            'textAlign': 'center',
            'font-weight': 'bold',
        },
        {
            'if': {'column_id': 'Proposal'},
            'backgroundColor':f'rgba{(*hex_to_rgb(COLR3), 0.2)}'
        },
    ],
    style_data={                
        'whiteSpace': 'normal',
        'height': 'auto'
    }
    )
    return table

# Summary computation function
def summ_comp(hcwd,hcwe,lcwd,lcwe,fh_df,col_name):

    # High Consumption period Carbon Intensity & Fee per weekday 
    hcwd_ci = (hcwd['CI(g/KWh)']*hcwd[col_name].astype(float)).sum()
    hcwd_con = (hcwd['($/KWh)']*hcwd[col_name].astype(float)*fh_df['Freehour']).sum()

    # High Consumption period Carbon Intensity & Fee per weekend 
    hcwe_ci = (hcwe['CI(g/KWh)']*hcwe[col_name].astype(float)).sum()
    hcwe_con = (hcwe['($/KWh)']*hcwe[col_name].astype(float)*fh_df['Freehour']).sum()

    # Low Consumption period Carbon Intensity & Fee per weekday 
    lcwd_ci = (lcwd['CI(g/KWh)']*lcwd[col_name].astype(float)).sum()
    lcwd_con = (lcwd['($/KWh)']*lcwd[col_name].astype(float)*fh_df['Freehour']).sum()
    
    # Low Consumption period Carbon Intensity & Fee per weekend 
    lcwe_ci = (lcwe['CI(g/KWh)']*lcwe[col_name].astype(float)).sum()
    lcwe_con = (lcwe['($/KWh)']*lcwe[col_name].astype(float)*fh_df['Freehour']).sum()

    # Total for year 2022
    total_ci = (hcwd_ci*HC_WD + hcwe_ci*HC_WE + lcwd_ci*LC_WD + lcwe_ci*LC_WE)/1000
    total_con = (hcwd_con*HC_WD + hcwe_con*HC_WE + lcwd_con*LC_WD + lcwe_con*LC_WE)
    
    return total_ci, total_con

epeak,etrough = cemission_df()



# ------------------------------------------------------------------------------
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
                    [html.I(className="fas fa-chart-line me-2"), html.Span("Overview")],
                    href="/",
                    active="exact",
                ),
                dbc.NavLink(
                    [
                        html.I(className="fas fa-magnifying-glass-chart me-2"),
                        html.Span("Usage Pattern"),
                    ],
                    href="/pattern",
                    active="exact",
                ),
                dbc.NavLink(
                    [
                        html.I(className="fas fa-sliders me-2"),
                        html.Span("Usage Adjustment"),
                    ],
                    href="/adjust",
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
            html.H5('ICP Electricity Consumption'),
            dcc.Loading(id='trentload',children=
                [dbc.Row(
                    dbc.Col([dbc.Card(dbc.Row(id='chart_ph1', children=[]))])
                    )],
                type='default'),
            html.Br(),

            dcc.Loading(id='gc1load',children=
                [dbc.Row(
                    dbc.Col(dbc.Card(dbc.Row(id='chart_ph2', children=[])))
                )],
                type='default'),
            html.Br(),
            dcc.Loading(id='dc1load',children=
                [
                    dbc.Row([
                        dbc.Col(id='indi_ph1', children=[],width=2),
                        dbc.Col(dbc.Card(id='chart_ph3', children=[]),
                            width=10)                       
                    ])
                ],
            type='default'),
        ])


# pattern page
pattern_page = html.Div([
            dcc.Loading(id='pattern_load',children=
                [dbc.Row([
                    dbc.Col([
                        html.H5('Pattern of the High Consumption (May to Oct)'),
                        dbc.Card(id='pttchart_ph1', children=[])
                        ]),

                    dbc.Col([
                        html.H5('Pattern of the Low Consumption (Nov to Apr)'),
                        dbc.Card(id='pttchart_ph2', children=[])
                        ])                    
                ])
                ],type='default'),

            html.Br(),html.Br(),
            dcc.Loading(id='cpattern_load',children=
                [dbc.Row([
                    dbc.Col([
                        html.H5('Emission Pattern of the High Consumption (May to Oct)'),
                        dbc.Card(id='cpttchart_ph1', children=[dcc.Graph(figure=egrp_chart(epeak))])
                        ]),

                    dbc.Col([
                        html.H5('Emission Pattern of the Low Consumption (Nov to Apr)'),
                        dbc.Card(id='cpttchart_ph2', children=[dcc.Graph(figure=egrp_chart(etrough))])
                        ])                    
                ])
                ],type='default')
        ])

# adjust_page
adjust_page = html.Div([
            html.H5('Eletricity Usage Pattern Adjustment'),
            dbc.Row([
                dbc.Col([
                    dbc.Row(dcc.Loading(id='adjust_load',children=[
                        html.Div(id='usage_adj')
                        ],type='default')),
                    dbc.Row(dcc.Loading(id='preview_load',children=[
                        dbc.Row(id='usage_preview')
                        ],type='default')),
                    html.Br(),html.Br(),
                    dbc.Row(dcc.Loading(id='adjust_load2',children=[
                        html.Div(id='usage_adj2')
                        ],type='default')),
                    dbc.Row(dcc.Loading(id='preview_load2',children=[
                        dbc.Row(id='usage_preview2')
                        ],type='default')),                               
                ],width=9,style={'padding-top':'20px'}),

                dbc.Col([
                    dbc.Card([
                        dbc.Row(html.H6('Select Power Plan')),
                        dbc.Row(dcc.Dropdown(id='plan_selector', multi=False, 
                                    value='ctct_1',options=plan_vals)),
                        dbc.Row(html.H6('Hour of Free Off-peak power'),style={'padding-top':'20px'}),
                        dbc.Row(dcc.Dropdown(id='fh_selector', multi=False, 
                                    placeholder='Select if applicable',
                                    options=hr_vals)),
                        ],style={'padding':'20px'}),

                    html.Br(),
                    dcc.Loading(id='side_load',children=[
                        html.Div(id='side_sum'),
                        ],type='default'),

                ],width=3),
                
              
                ])

        ])



content = html.Div(id='page-content', className='content')

dashapp.layout = html.Div([
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
        heading_row,
        content],               
    style={'backgroundColor':'#F5F5F5'})

# ------------------------------------------------------------------------------
# Callback

# Data store
@callback(
    Output('store-profile', 'data'),
    Input('profile_selector', 'value')
)
def store_profile(value):
    query = f'data/profiles/{value}.csv'
    dataset = pd.read_csv(query)
    
    return dataset.to_dict('records')

 
# plan store
@callback(
    Output('store-plan', 'data'),
    Input('plan_selector', 'value')
)
def store_plan(value):
    dataset = pd.read_csv('data/elc_plans.csv')
    dataset = dataset[['isWE','Trading_Period',f'{value}']].copy()
    dataset = dataset.replace({'Trading_Period':tptime_fix})
    return dataset.to_dict('records')

# set the content according to the current pathname
@callback(
        Output("page-content", "children"),
        Input("url", "pathname")
)

def render_page_content(pathname):
    if pathname == '/':
        return overview
    elif pathname == '/pattern':
        return pattern_page
    elif pathname == "/adjust":
        return adjust_page

# Trend chart Tab1
@callback(
    Output('chart_ph1', 'children'),
    Input('store-profile', 'data')
)
def trend_chart(data):
    # Prepare dataframe
    df_daily = daily_df(data)
    lowess = sm.nonparametric.lowess(df_daily['Consumption(KWh)'], 
        df_daily['Date'], frac=0.08)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_daily['Date'], y=df_daily['Consumption(KWh)'],
                    mode='markers',
                    name='Consumption',
                    hovertemplate = '%{y:,.3f} KWh',
                    opacity=0.5,
                    marker=dict(size=4, color=COLR1)
                    ))
    fig.add_trace(go.Scatter(x=df_daily['Date'], y=lowess[:,1],
                    mode='lines',
                    name='Trendline',
                    hovertemplate = '%{y:,.3f} KWh',
                    line=dict(color=COLR1)
                    ))

    # Add figure layout
    fig.update_layout(title_text=(f'<span style="font-size: 18px;"> Latest Electricity Usage Trend </span>'),
        hovermode='x unified',
        plot_bgcolor='#FFFFFF',
        xaxis_title = None,
        margin = dict(t=100,r=30),
        showlegend=True,
        legend=dict(orientation='h',yanchor='bottom',y=1.02,xanchor='right',x=1))
    fig.update_yaxes(title_text='Consumption(KWh)', title_font=dict(size=12),
        showgrid=True, gridwidth=1, gridcolor='#f0f0f0') 
    fig.update_xaxes(dtick="M1",type = 'date',tickformat="%d%b\n%Y",
        range=(df_daily['Date'].min(),df_daily['Date'].max()))

    return dcc.Graph(figure=fig)

# Group chart Tab1
@callback(
    Output('chart_ph2', 'children'),
    Input('store-profile', 'data')
)
def group_chart1(data):
    # Prepare dataframe
    df_daily = daily_df(data)
    weatherdf = weather_df(data)

    fig2 = make_subplots(rows=2, cols=1,shared_xaxes=True,
        subplot_titles=('Christchurch Temprature (C)','Daily Consumption(KWh)'),
                        vertical_spacing=0.1,
                        row_width=[0.6,0.4])

    # Chart 1 Temperature
    fig2.add_trace(
        go.Scatter(
            name='Avg Temp(C)',
            x=weatherdf['Date(NZST)'],
            y=weatherdf['Tavg(C)'],
            mode='lines',
            line=dict(color=COLR4)
            ),row=1,col=1)

    fig2.add_trace(
        go.Scatter(
            name='Max Temp(C)',
            x=weatherdf['Date(NZST)'],
            y=weatherdf['Tmax(C)'],
            mode='lines',
            marker=dict(color="#444"),
            line=dict(width=0),
            showlegend=False
            ),row=1,col=1)

    fig2.add_trace(
        go.Scatter(
            name='Min Temp(C)',
            x=weatherdf['Date(NZST)'],
            y=weatherdf['Tmin(C)'],
            marker=dict(color="#444"),
            line=dict(width=0),
            mode='lines',
            fillcolor=f'rgba{(*hex_to_rgb(COLR4), 0.1)}',
            fill='tonexty',
            showlegend=False
            ),row=1,col=1
        )

    # Chart 2 consumstion
    fig2.add_trace(
        go.Bar(
            x = df_daily['Date'], y = df_daily['Consumption(KWh)'], opacity=1,
            name='Consumption(KWh)',
            marker=dict(color=df_daily['WeekendC'],line = dict(width=0)),
            hovertemplate = '%{y:,.3f} KWh'),
            row=2,col=1
        )
    # Layout setting

    fig2.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0')
    fig2.update_traces(xaxis='x2')

    # Subplots title setting
    for n in range (2):
        fig2.layout.annotations[n].update(x=0,font_size=12,xanchor ='left') 

    fig2.update_layout(
        plot_bgcolor = '#FFFFFF',
        title_text=(f'<span style="font-size: 18px; "> Daily Electricity Consumption and Temperature</span>'),
        hovermode='x unified',
        xaxis4 = dict(tickangle = 0, tickfont =dict(size=10),showticklabels=True, 
            dtick ='M1', tickformat="%d\n%b%Y",type="date"),
        margin = dict(r=30),
        legend=dict(orientation='h',yanchor='bottom',y=1.02,xanchor='right',x=1))
    
    return dcc.Graph(id='group_chart1', clickData=None,figure=fig2)

# Detail chart Tab1
@callback(
    Output('chart_ph3', 'children'),
    Input('store-profile', 'data'),
    Input('group_chart1','clickData')
)
def detail_chart(data,clk_data):
    # Prepare dataframe
    df = detail_df(data)
    df_daily = daily_df(data)

    if clk_data is None:
        clk_date = df_daily['Date'].max()

        df2 =  df[(df['Date'] == clk_date)]

        fig3 = go.Figure(go.Bar(x = df2['Trading_Period'], y=df2['Consumption(KWh)'],
            name='Consumption',showlegend=False,
            hovertemplate = '%{y:,.3f} KWh',
            marker=dict(color=COLR1,opacity=0.6, line = dict(width=0))))

        # Add figure layout
        sel_date = str(clk_date).split(' ',1)[0]
        fig3.update_layout(height=376,
            title_text=(f'<span style="font-size: 18px;"> Electricity Consumption on {sel_date} </span>'),
            hovermode='x unified',
            plot_bgcolor='#FFFFFF',
            xaxis_title = None,
            margin = dict(r=30),
            showlegend=True,
            legend=dict(orientation='h',yanchor='bottom',y=1.02,xanchor='right',x=1))
        fig3.update_yaxes(title_text='Consumption(KWh)', title_font=dict(size=12),
            showgrid=True, gridwidth=1, gridcolor='#f0f0f0') 

        return dcc.Graph(figure=fig3)

    else:
        clk_date = clk_data['points'][0]['x']

        df2 =  df[(df['Date'] == clk_date)]

        fig3 = go.Figure(go.Bar(x = df2['Trading_Period'], y=df2['Consumption(KWh)'],
            name='Consumption',showlegend=False,
            hovertemplate = '%{y:,.3f} KWh',
            marker=dict(color=COLR1,opacity=0.6, line = dict(width=0))))

        # Add figure layout
        sel_date = str(clk_date).split(' ',1)[0]
        fig3.update_layout(height=376,
            title_text=(f'<span style="font-size: 18px;"> Electricity Consumption on {sel_date} </span>'),
            hovermode='x unified',
            plot_bgcolor='#FFFFFF',
            xaxis_title = None,
            margin = dict(r=30),
            showlegend=True,
            legend=dict(orientation='h',yanchor='bottom',y=1.02,xanchor='right',x=1))
        fig3.update_yaxes(title_text='Consumption(KWh)', title_font=dict(size=12),
            showgrid=True, gridwidth=1, gridcolor='#f0f0f0') 
        return dcc.Graph(figure=fig3)

# Summary cards Tab1
@callback(
    Output('indi_ph1', 'children'),
    Input('store-profile', 'data'),
    Input('group_chart1','clickData')
)
def summ_cards(data,clk_data):
    # Prepare dataframe
    df = detail_df(data)
    df_daily = daily_df(data)


    if clk_data is None:
        clk_date = df_daily['Date'].max()

        df2 =  df[(df['Date'] == clk_date)]

        indi_cards = indicators_card(df2)

        return dbc.Row(indi_cards)

    else:
        clk_date = clk_data['points'][0]['x']

        df2 =  df[(df['Date'] == clk_date)]
        
        indi_cards = indicators_card(df2)

        return dbc.Row(indi_cards)

# Peak period chart Tab2
@callback(
    Output('pttchart_ph1', 'children'),
    Input('store-profile', 'data'),
)
def peak_charts(data):
    # Prepare dataframe
    df = detail_df(data)
    df_daily = daily_df(data)

    May_Oct = peak_dataframe(df,df_daily)

    return dcc.Graph(figure=grp_charts(May_Oct))

# Trough period chart Tab2
@callback(
    Output('pttchart_ph2', 'children'),
    Input('store-profile', 'data'),
)
def trough_charts(data):
    # Prepare dataframe
    df = detail_df(data)
    df_daily = daily_df(data)

    Nov_Apr = trough_dataframe(df,df_daily)

    return dcc.Graph(figure=grp_charts(Nov_Apr))


# Usage adjustment datatable
@callback(
    Output('usage_adj', 'children'),
    Output('usage_adj2', 'children'),
    Input('store-profile', 'data'),
    Input('store-plan', 'data'),
)
def usage_adjustment(data,plan):
    # Prepare data
    hcwd,hcwe,lcwd,lcwe = split_df(data,plan)

    adj_content = dbc.Row([
        html.P('High Consumption Period May - Oct',style = {'font-size':19, 
            'font-weight': 'bold','textAlign':'center'}),       
        dbc.Col([
            html.H6('Weekday Proposal Adjustment'),
            dbc.Row(usage_adj_table(hcwd,'hcwd'))
            ],width=6),
        dbc.Col([
            html.H6('Weekend Proposal Adjustment'),
            dbc.Row(usage_adj_table(hcwe,'hcwe'))
            ],width=6),
        ])
    adj_content2 = dbc.Row([
        html.P('Low Consumption Period Jan - Apr & Nov - Dec',style = {
            'font-size':19, 'font-weight': 'bold','textAlign':'center'}),
        dbc.Col([
            html.H6('Weekday Proposal Adjustment'),
            dbc.Row(usage_adj_table(lcwd,'lcwd'))
            ],width=6),
        dbc.Col([
            html.H6('Weekend Proposal Adjustment'),
            dbc.Row(usage_adj_table(lcwe,'lcwe'))
            ],width=6),
        ])
    return adj_content,adj_content2


# Usage preview 1
@callback(
    Output('usage_preview', 'children'),
    Input('dtable_hcwd', 'derived_virtual_data'),
    Input('dtable_hcwe', 'derived_virtual_data'),
    Input('fh_selector', 'value'),
    Input('store-profile', 'data'),
    Input('store-plan', 'data'),
)
def usg_preview(hcwd_p,hcwe_p,fhour,data,plan):
    # Prepare data
    hcwd,hcwe,lcwd,lcwe = split_df(data,plan)

    hcwd_rec = pd.DataFrame(hcwd_p)
    if hcwd_rec.empty:
        hcwd_rec=hcwd.copy()

    hcwe_rec = pd.DataFrame(hcwe_p)
    if hcwe_rec.empty:
        hcwe_rec=hcwe.copy()

    fh_df = fhour_df(fhour)

    unAloc_wd = ((hcwd_rec['Pattern'].astype(float)).sum() - (hcwd_rec['Proposal'].astype(float)).sum())
    unAloc_we = ((hcwe_rec['Pattern'].astype(float)).sum() - (hcwe_rec['Proposal'].astype(float)).sum())

    # High Consumption period Carbon Intensity & Fee per weekday 
    hcwd_ci = (hcwd_rec['CI(g/KWh)']*hcwd_rec['Pattern'].astype(float)).sum()/1000
    hcwd_con = (hcwd_rec['($/KWh)']*hcwd_rec['Pattern'].astype(float)*fh_df['Freehour']).sum()
    hcwd_ci_p = (hcwd_rec['CI(g/KWh)']*hcwd_rec['Proposal'].astype(float)).sum()/1000
    hcwd_con_p = (hcwd_rec['($/KWh)']*hcwd_rec['Proposal'].astype(float)*fh_df['Freehour']).sum()

    # High Consumption period Carbon Intensity & Fee per weekend 
    hcwe_ci = (hcwe_rec['CI(g/KWh)']*hcwe_rec['Pattern'].astype(float)).sum()/1000
    hcwe_con = (hcwe_rec['($/KWh)']*hcwe_rec['Pattern'].astype(float)*fh_df['Freehour']).sum()
    hcwe_ci_p = (hcwe_rec['CI(g/KWh)']*hcwe_rec['Proposal'].astype(float)).sum()/1000
    hcwe_con_p = (hcwe_rec['($/KWh)']*hcwe_rec['Proposal'].astype(float)*fh_df['Freehour']).sum()


    preview_content = html.Div([ 
        dbc.Row([
            dbc.Col(html.P(f'Unallocated Load: {unAloc_wd:.3f} KWh',style={
                'font-size':13, 'font-weight':'bold', 'textAlign':'right',
                'margin-top':'5px'})),
            dbc.Col(html.P(f'Unallocated Load: {unAloc_we:.3f} KWh',style={
                'font-size':13, 'font-weight':'bold', 'textAlign':'right',
                'margin-top':'5px'})),
        ]),
        dbc.Row([
            dbc.Col(dbc.Row([
                dbc.Col(dbc.Card([
                    html.P('Expense Pattern/Proposal',style={'font-size':'14px',
                        'textAlign':'center' }),
                    html.H5(f'{hcwd_con:.3f} / {hcwd_con_p:.3f} $NZ',style={'textAlign':'center', 
                        'color':COLR1})
                    ],style={'padding':'5px'})),

                dbc.Col(dbc.Card([
                    html.P('Emission Pattern/Proposal',style={'font-size':'14px',
                        'textAlign':'center' }),
                    html.H5(f'{hcwd_ci:.3f} / {hcwd_ci_p:.3f} kgCO2',style={'textAlign':'center', 
                        'color':COLR7})
                    ],style={'padding':'5px'})),
                ])
            ),
            dbc.Col(dbc.Row([
                dbc.Col(dbc.Card([
                    html.P('Expense Pattern/Proposal',style={'font-size':'14px',
                        'textAlign':'center' }),
                    html.H5(f'{hcwe_con:.3f} / {hcwe_con_p:.3f} $NZ',style={'textAlign':'center', 
                        'color':COLR1})
                    ],style={'padding':'5px'})),

                dbc.Col(dbc.Card([
                    html.P('Emission Pattern/Proposal',style={'font-size':'14px',
                        'textAlign':'center' }),
                    html.H5(f'{hcwe_ci:.3f} / {hcwe_ci_p:.3f} kgCO2',style={'textAlign':'center', 
                        'color':COLR7})
                    ],style={'padding':'5px'})),
                ])
            ),
        ]),
        html.Br(),html.Br(),

        dbc.Card(dcc.Graph(figure=pattern_review(hcwd_rec,hcwe_rec)))
    ])
    return preview_content

# Usage preview 2
@callback(
    Output('usage_preview2', 'children'),
    Input('dtable_lcwd', 'derived_virtual_data'),
    Input('dtable_lcwe', 'derived_virtual_data'),
    Input('fh_selector', 'value'),
    Input('store-profile', 'data'),
    Input('store-plan', 'data'),       
)
def usg_preview2(lcwd_p,lcwe_p,fhour,data,plan):
    # Prepare data
    hcwd,hcwe,lcwd,lcwe = split_df(data,plan)

    lcwd_rec = pd.DataFrame(lcwd_p)
    if lcwd_rec.empty:
        lcwd_rec = lcwd.copy()

    lcwe_rec = pd.DataFrame(lcwe_p)
    if lcwe_rec.empty:
        lcwe_rec = lcwe.copy()

    fh_df = fhour_df(fhour)

    unAloc_wd = ((lcwd_rec['Pattern'].astype(float)).sum() - (lcwd_rec['Proposal'].astype(float)).sum())
    unAloc_we = ((lcwe_rec['Pattern'].astype(float)).sum() - (lcwe_rec['Proposal'].astype(float)).sum())

    # Low Consumption period Carbon Intensity & Fee per weekday 
    lcwd_ci = (lcwd_rec['CI(g/KWh)']*lcwd_rec['Pattern'].astype(float)).sum()/1000
    lcwd_con = (lcwd_rec['($/KWh)']*lcwd_rec['Pattern'].astype(float)*fh_df['Freehour']).sum()
    lcwd_ci_p = (lcwd_rec['CI(g/KWh)']*lcwd_rec['Proposal'].astype(float)).sum()/1000
    lcwd_con_p = (lcwd_rec['($/KWh)']*lcwd_rec['Proposal'].astype(float)*fh_df['Freehour']).sum()

    # Low Consumption period Carbon Intensity & Fee per weekend 
    lcwe_ci = (lcwe_rec['CI(g/KWh)']*lcwe_rec['Pattern'].astype(float)).sum()/1000
    lcwe_con = (lcwe_rec['($/KWh)']*lcwe_rec['Pattern'].astype(float)*fh_df['Freehour']).sum()
    lcwe_ci_p = (lcwe_rec['CI(g/KWh)']*lcwe_rec['Proposal'].astype(float)).sum()/1000
    lcwe_con_p = (lcwe_rec['($/KWh)']*lcwe_rec['Proposal'].astype(float)*fh_df['Freehour']).sum()


    preview_content = html.Div([
        dbc.Row([
            dbc.Col(html.P(f'Unallocated Load: {unAloc_wd:.3f} KWh',style={
                'font-size':13, 'font-weight':'bold', 'textAlign':'right',
                'margin-top':'5px'})),
            dbc.Col(html.P(f'Unallocated Load: {unAloc_we:.3f} KWh',style={
                'font-size':13, 'font-weight':'bold', 'textAlign':'right',
                'margin-top':'5px'})),
        ]),
        dbc.Row([
            dbc.Col(dbc.Row([
                dbc.Col(dbc.Card([
                    html.P('Expense Pattern/Proposal',style={'font-size':'14px',
                        'textAlign':'center' }),
                    html.H5(f'{lcwd_con:.3f} / {lcwd_con_p:.3f} $NZ',style={'textAlign':'center', 
                        'color':COLR1})
                    ],style={'padding':'5px'})),

                dbc.Col(dbc.Card([
                    html.P('Emission Pattern/Proposal',style={'font-size':'14px',
                        'textAlign':'center' }),
                    html.H5(f'{lcwd_ci:.3f} / {lcwd_ci_p:.3f} kgCO2',style={'textAlign':'center', 
                        'color':COLR7})
                    ],style={'padding':'5px'})),
                ])
            ),
            dbc.Col(dbc.Row([
                dbc.Col(dbc.Card([
                    html.P('Expense Pattern/Proposal',style={'font-size':'14px',
                        'textAlign':'center' }),
                    html.H5(f'{lcwe_con:.3f} / {lcwe_con_p:.3f} $NZ',style={'textAlign':'center', 
                        'color':COLR1})
                    ],style={'padding':'5px'})),

                dbc.Col(dbc.Card([
                    html.P('Emission Pattern/Proposal',style={'font-size':'14px',
                        'textAlign':'center' }),
                    html.H5(f'{lcwe_ci:.3f} / {lcwe_ci_p:.3f} kgCO2',style={'textAlign':'center', 
                        'color':COLR7})
                    ],style={'padding':'5px'})),
                ])
            ),
        ]),
        html.Br(), html.Br(), 
        dbc.Card(dcc.Graph(figure=pattern_review(lcwd_rec,lcwe_rec)))
    ])
    return preview_content


@callback(
    Output('side_sum', 'children'),
    Input('fh_selector', 'value'),
    Input('dtable_hcwd', 'derived_virtual_data'),
    Input('dtable_hcwe', 'derived_virtual_data'),  
    Input('dtable_lcwd', 'derived_virtual_data'),
    Input('dtable_lcwe', 'derived_virtual_data'),
    Input('store-profile', 'data'),
    Input('store-plan', 'data'),  
)
def side_content(fhour,hcwd_p,hcwe_p,lcwd_p,lcwe_p,data,plan):
    # Prepare data
    hcwd_backup,hcwe_backup,lcwd_backup,lcwe_backup = split_df(data,plan)

    fh_df = fhour_df(fhour)

    hcwd = pd.DataFrame(hcwd_p)
    if hcwd.empty:
        hcwd = hcwd_backup.copy()

    hcwe = pd.DataFrame(hcwe_p)
    if hcwe.empty:
        hcwe = hcwe_backup.copy()

    lcwd = pd.DataFrame(lcwd_p)
    if lcwd.empty:
        lcwd = lcwd_backup.copy()

    lcwe = pd.DataFrame(lcwe_p)
    if lcwe.empty:
        lcwe = lcwe_backup.copy()

    # Compute values for display
    total_ci,total_con = summ_comp(hcwd,hcwe,lcwd,lcwe,fh_df,'Pattern')
    total_ci_p, total_con_p = summ_comp(hcwd,hcwe,lcwd,lcwe,fh_df,'Proposal')

    side_content = dbc.Col([
        dbc.Card([
            html.P('Total Carbon Emission 2022',style={'textAlign':'Center',
                'font-size':17,'font-weight':'500'
                }),
            dbc.Row([
                dbc.Col(html.P('Pattern:',style={'font-size':16,'textAlign':'right'}),
                    width=4),
                dbc.Col(html.H4(f'{total_ci:,.2f} kgCO2',style={'color':COLR6,
                    'textAlign':'left'}),width=8),
            ]),  
            dbc.Row([
                dbc.Col(html.P('Proposal:',style={'font-size':16,'textAlign':'right'}),
                    width=4),
                dbc.Col(html.H4(f'{total_ci_p:,.2f} kgCO2',style={'color':COLR7,
                    'textAlign':'left'}),width=8),
            ]),  
            ],style={'padding':'20px'}),
        html.Br(),
        dbc.Card([
            html.P('Total Electricity Expense 2022(*)',style={'textAlign':'Center',
                'font-size':17,'font-weight':'500'
                }),
            dbc.Row([
                dbc.Col(html.P('Pattern:',style={'font-size':16,'textAlign':'right'}),
                    width=4),
                dbc.Col(html.H4(f'{total_con:,.2f} $NZ',style={'color':COLR6,
                    'textAlign':'left'}),width=8),
            ]),  
            dbc.Row([
                dbc.Col(html.P('Proposal:',style={'font-size':16,'textAlign':'right'}),
                    width=4),
                dbc.Col(html.H4(f'{total_con_p:,.2f} $NZ',style={'color':COLR1,
                    'textAlign':'left'}),width=8),
            ]),  
            ],style={'padding':'20px'}),
        html.Br(),
        html.P('(*)The expense only includes the charge for KWh usage, and \
            excluded all other fees', style={'font-size':12,'font-style':'italic'}),
        html.P('The computation above based on the pattern of ICP Consumption \
            applied to year 2022 and Carbon Emssion Pattern of year 2022',
            style={'font-size':12,'font-style':'italic'}),
    ])

    return side_content

app = dashapp.server.wsgi_app

if __name__ == "__main__":
    dashapp.run_server(host='0.0.0.0', port=80, debug=False)