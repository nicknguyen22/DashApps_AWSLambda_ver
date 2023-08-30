import dash                                     
from dash import Dash, dcc, html, Input, Output, callback, dash_table
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from datetime import date
import pandas as pd

dashapp = Dash(__name__,
           external_stylesheets=[
                dbc.themes.BOOTSTRAP, 
                dbc.icons.FONT_AWESOME
                ])

LOGO = 'isviz/assets/logo.jpg'

# Loading data
solar_df = pd.read_csv('solar_df.csv')
solar_df2 = pd.read_csv('solar_df2.csv')

solar_df3 = pd.read_csv('solar_df3.csv')
solar_df3['Trading_Date'] = pd.to_datetime(solar_df3['Trading_Date'])

isaac_df = pd.read_csv('isaac_df.csv')
isaac_df['Trading_Date'] = pd.to_datetime(isaac_df['Trading_Date'])

spotprice_df = pd.read_csv('spotprice.csv')
spotprice_df['Trading_Date'] = pd.to_datetime(spotprice_df['Trading_Date'])

ci_df = pd.read_csv('isaac_ems.csv')
ci_df['Trading_Date'] = pd.to_datetime(ci_df['Trading_Date'])

sys_vals = [
    {"label": "20 Degree Sys", "value": "A20"},
    {"label": "25 Degree Sys", "value": "A25"},
    {"label": "31 Degree Sys", "value": "A31"},
    {"label": "34 Degree Sys", "value": "A34"},
    {"label": "39 Degree Sys", "value": "A39"},
                ]

# Dataframe compute
def sol_df(size,size2):
    solar_detail = solar_df.copy()
    solar_detail2 = solar_df2.copy()

    solar_detail['Trading_Date'] = pd.to_datetime(solar_detail['Trading_Date'])
    solar_detail2['Trading_Date'] = pd.to_datetime(solar_detail2['Trading_Date'])

    solar_detail['East_Total(kWh)'] = solar_detail['East(kW/m2)']*(size/2)
    solar_detail['West_Total(kWh)'] = solar_detail['West(kW/m2)']*(size/2)
    solar_detail['E/W_Total(kWh)'] = solar_detail['East_Total(kWh)'] + solar_detail['West_Total(kWh)']

    solar_detail2['North_Total(kWh)'] = solar_detail2['North(kW/m2)']*size2
    return solar_detail,solar_detail2


# Chart functions

def summary_cards(size,size2):
    solar_tp,solar_tp2 = sol_df(size,size2)
    isaac_tp = isaac_df.copy()
    sp_tp = spotprice_df.copy()

    isaac_tp['Electricity_Cost($)'] = (
        round(isaac_tp['Consumption(kWh)']*isaac_tp['Contract_Price($)'],3))
    
    total_df = (isaac_tp.merge(solar_tp, on = ['Trading_Date','Trading_Period'])
                .merge(solar_tp2, on = ['Trading_Date','Trading_Period'])
                .merge(sp_tp, on =['Trading_Date','Trading_Period']))
    total_df['Net_consum'] = (total_df['Consumption(kWh)']-(total_df['E/W_Total(kWh)'])-
                              (total_df['North_Total(kWh)'])
                              )

    # Cost with Solar
    total_df['Cost_wSolar'] = total_df['Net_consum']*total_df['Contract_Price($)']
    total_df.loc[total_df['Cost_wSolar']<0,'Cost_wSolar'] = 0

    # Revenue of export
    total_df['Revenue'] = -((total_df['Net_consum']/1000)*total_df['$/MWh'])
    total_df.loc[total_df['Revenue']<0,'Revenue'] =  0

    cards = dbc.Row([
        dbc.Card([
            dbc.CardBody([
                html.H6('Electricity Cost w/o Solar',style={'textAlign':'center','marginBottom':'15px'}),
                html.H4(f"${isaac_tp['Electricity_Cost($)'].sum():,.2f}",style={'textAlign':'center',
                    'color':'orange'})
                ])
            ],style={'width':'290px','marginLeft':'12px'}),

        dbc.Card([
            dbc.CardBody([
                html.H6('Electricity Cost with Solar',style={'textAlign':'center','marginBottom':'15px'}),
                html.H4(f"${total_df['Cost_wSolar'].sum():,.2f}",style={'textAlign':'center',
                    'color':'gray'})
                ])
            ],style={'width':'290px','marginLeft':'12px'}),
        
        dbc.Card([
            dbc.CardBody([
                html.H6('Revenue from exporting Solar',style={'textAlign':'center','marginBottom':'15px'}),
                html.H4(f"${total_df['Revenue'].sum():,.2f}",style={'textAlign':'center',
                    'color':'#346888'})
                ])
            ],style={'width':'290px','marginLeft':'12px'}),

        dbc.Card([
            dbc.CardBody([
                html.H6('Final Electricity Cost',style={'textAlign':'center','marginBottom':'15px'}),
                html.H4(f"${((total_df['Cost_wSolar'].sum()) - (total_df['Revenue'].sum())):,.2f}",
                        style={'textAlign':'center','color':'brown'})
                ])
            ],style={'width':'290px','marginLeft':'12px'}),
    ])
    return cards

def ems_summary_cards(df):
    cards = dbc.Row([
        dbc.Card([
            dbc.CardBody([
                html.H6('Yearly Carbon Emission w/o Solar',style={'textAlign':'center','marginBottom':'15px'}),
                html.H4(f"{df['Carbon_Emission_wo_Solar(t)'].sum():,.3f} ton",style={'textAlign':'center',
                    'color':'rgb(73,73,73)'})
                ])
            ],style={'width':'290px','marginLeft':'12px'}),

        dbc.Card([
            dbc.CardBody([
                html.H6('Yearly Carbon Emission with Solar',style={'textAlign':'center','marginBottom':'15px'}),
                html.H4(f"{df['Carbon_Emission_w_Solar(t)'].sum():,.3f} ton",style={'textAlign':'center',
                    'color':'green'})
                ])
            ],style={'width':'290px','marginLeft':'12px'}),
    ])
    return cards

def main_chart(isaac_daily,solar_daily,sp_daily,total_daily):
    fig = make_subplots(rows=3, cols=1,
        shared_xaxes=True,
        subplot_titles=('Median Daily Spot Price of ISL2201 ($c/kWh)',
            'Daily Electricity Consumption & Solar Generation (kWh)',
            'Cost & Revenue breakdown ($)'),
        vertical_spacing=0.1,
        row_width=[0.4,0.4,0.2])
    
    fig.add_trace(
        go.Scatter(x=sp_daily['Trading_Date'], y=(sp_daily['$c/kWh']), 
                    name='ISL2201 Median Spotprice ($c/kWh)',
                    hoverinfo='x+y',
                    mode='lines',
                    line=dict(width=1.5, color='rgba(205,0,0,1)'),
                    hovertemplate = '%{y:,.2f} $c'),row=1,col=1
    )

    fig.add_trace(
        go.Scatter(x=solar_daily['Trading_Date'], y=-(solar_daily['East_Total(kWh)']), 
                    name='East-Side Solar Generation(kWh)',
                    hoverinfo='x+y',
                    mode='lines',
                    stackgroup='one',
                    line=dict(width=0.5, color='rgba(255,177,57,1)'),
                    hovertemplate = '%{y:,.2f} kWh'),row=2,col=1
    )

    fig.add_trace(
        go.Scatter(x=solar_daily['Trading_Date'], y=-(solar_daily['West_Total(kWh)']), 
                    name='West-Side Solar Generation(kWh)',
                    hoverinfo='x+y',
                    mode='lines',
                    stackgroup='one',
                    line=dict(width=0.5, color='rgba(255,199,117,1)'),
                    hovertemplate = '%{y:,.2f} kWh'),row=2,col=1
    )

    fig.add_trace(
        go.Scatter(x=solar_daily['Trading_Date'], y=-(solar_daily['North_Total(kWh)']), 
                    name='North-Side Solar Generation(kWh)',
                    hoverinfo='x+y',
                    mode='lines',
                    stackgroup='one',
                    line=dict(width=0.5, color='rgba(155,199,117,1)'),
                    hovertemplate = '%{y:,.2f} kWh'),row=2,col=1
    ) 

    fig.add_trace(
        go.Scatter( x=solar_daily['Trading_Date'], 
                    y=-(solar_daily['E/W_Total(kWh)']),
                    name='Total East & West Solar Generation(kWh)',
                    marker=dict(size=0, symbol='line-ew', line=dict(width=0.0, color='#FFFFFF')),
                    mode="markers",
                    showlegend=False,
                    hovertemplate = '%{y:,.2f} kWh'),row=2,col=1
    )

    fig.add_trace(
        go.Scatter( x=solar_daily['Trading_Date'], 
                    y=-(solar_daily['E/W_Total(kWh)']+solar_daily['North_Total(kWh)']),
                    name='Total Solar Generation(kWh)',
                    marker=dict(size=0, symbol='line-ew', line=dict(width=0.0, color='#FFFFFF')),
                    mode="markers",
                    showlegend=False,
                    hovertemplate = '%{y:,.2f} kWh'),row=2,col=1
    )

    fig.add_trace(
        go.Scatter(x=isaac_daily['Trading_Date'], y=isaac_daily['Consumption(kWh)'], name='Consumption(kWh)',
            hoverinfo='x+y',
            mode='lines',
            line=dict(width=0.5, color='rgba(128,128,128,0.3)'),
            stackgroup='two',
            hovertemplate = '%{y:,.2f} kWh'),row=2,col=1
    )

    fig.add_trace(
        go.Bar(x=total_daily['Trading_Date'], y=total_daily['Electricity_Cost($)'], 
                    name='Cost w/o Solar($)',
                    marker=dict(color='rgba(193, 231, 255, 1)',line = dict(width=0)),
                    hovertemplate = '$%{y:,.2f}'),row=3,col=1
    )

    fig.add_trace(
        go.Bar(x=total_daily['Trading_Date'], y=total_daily['Cost_wSolar'], 
                    name='Cost with Solar($)',
                    marker=dict(color='rgba(157, 198, 224, 1)',line = dict(width=0)),
                    hovertemplate = '$%{y:,.2f}'),row=3,col=1
    )

    fig.add_trace(
        go.Bar(x=total_daily['Trading_Date'], y= -(total_daily['Revenue']),
                    name='Revenue from Export',
                    marker=dict(color='rgba(122, 166, 194, 1)',line = dict(width=0)),
                    hovertemplate = '$%{y:,.2f}'),row=3,col=1
    )

    # Add figure layout
    for n in range (3):
        fig.layout.annotations[n].update(x=0,font_size=14,xanchor ='left',)
    fig.update_layout(title_text= 'Daily ISL2201 Average Spotprice, Electricity Consumption & Solar Generation',
        height = 1000,
        barmode = 'overlay',
        title_yanchor='top',
        hovermode="x unified",
        plot_bgcolor='#FFFFFF',
        margin = dict(r=20,t=170),
        xaxis = dict(tickmode = 'linear',dtick = 'M1'),
        legend=dict(orientation='h',yanchor='bottom',y=1.02,xanchor='right',x=1,)
        )
    
    # Styling
    # fig.update_layout(
    #     title = dict(font = dict(size = 20,
    #                             #  color = 'blue'
    #                              )),
    #     legend = dict(font = dict(size = 15,
        
    #     )),
    # )

    fig.update_yaxes(row=1, col=1, title='Price ($c/kWh)',showgrid=True, gridwidth=1, gridcolor='#f0f0f0',
                 title_font_size=12,tickfont=dict(size=12)
                 )
    fig.update_yaxes(row=2, col=1, title='Consumption(kWh)',showgrid=True, gridwidth=1, gridcolor='#f0f0f0',
                 title_font_size=12,tickfont=dict(size=12)
                 )
    fig.update_yaxes(row=3, col=1, title='$NZ',showgrid=True, gridwidth=1, gridcolor='#f0f0f0',
                 title_font_size=12,tickfont=dict(size=12)
                 )
    fig.update_traces(xaxis='x3')
    fig.update_xaxes(showgrid=False, gridwidth=1, title_font_size=12,tickfont=dict(size=12), dtick='M1')

    return fig

def group_charts(isaac_detail,solar_detail,sp_detail,total_detail,clk_date):
    fig = make_subplots(rows=4, cols=1,
        shared_xaxes=True,
        subplot_titles=('Electricity Consumption & Solar Generation (kWh)',
            'Net Electricity Consumption (kWh)',
            'ISL2201 Spot Price ($c/kWh)',
            'Electricity Cost($)'),
        vertical_spacing=0.1,
        row_width=[0.4,0.2,0.2,0.3])

    fig.add_trace(
        go.Scatter(x=solar_detail['Trading_Period'], y=-(solar_detail['East_Total(kWh)']), 
                    name='East Solar Generation(kWh)',
                    hoverinfo='x+y',
                    mode='lines',
                    stackgroup='one',
                    line=dict(width=0.5, color='rgba(255,177,57,1)'),
                    hovertemplate = '%{y:,.2f} kWh'),row=1,col=1
    )

    fig.add_trace(
        go.Scatter(x=solar_detail['Trading_Period'], y=-(solar_detail['West_Total(kWh)']), 
                    name='West-Side Solar Generation(kWh)',
                    hoverinfo='x+y',
                    mode='lines',
                    stackgroup='one',
                    line=dict(width=0.5, color='rgba(255,199,117,1)'),
                    hovertemplate = '%{y:,.2f} kWh'),row=1,col=1
    )

    fig.add_trace(
        go.Scatter(x=solar_detail['Trading_Period'], y=-(solar_detail['North_Total(kWh)']), 
                    name='North-Side Solar Generation(kWh)',
                    hoverinfo='x+y',
                    mode='lines',
                    stackgroup='one',
                    line=dict(width=0.5, color='rgba(155,199,117,1)'),
                    hovertemplate = '%{y:,.2f} kWh'),row=1,col=1
    ) 

    fig.add_trace(
        go.Scatter(x=solar_detail['Trading_Period'], y=-(solar_detail['E/W_Total(kWh)']),
                    name='Total East & West Solar Generation(kWh)',
                    marker=dict(size=0, symbol='line-ew', line=dict(width=0.0, color='#FFFFFF')),
                    mode="markers",
                    showlegend=False,
                    hovertemplate = '%{y:,.2f} kWh'),row=1,col=1
    )

    fig.add_trace(
        go.Scatter(x=solar_detail['Trading_Period'], y=-(solar_detail['E/W_Total(kWh)']+solar_detail['North_Total(kWh)']),
                    name='Total Solar Generation(kWh)',
                    marker=dict(size=0, symbol='line-ew', line=dict(width=0.0, color='#FFFFFF')),
                    mode="markers",
                    showlegend=False,
                    hovertemplate = '%{y:,.2f} kWh'),row=1,col=1
    )

    fig.add_trace(
        go.Scatter(x=isaac_detail['Trading_Period'], y=isaac_detail['Consumption(kWh)'], 
                    name='Consumption(kWh)',
                    hoverinfo='x+y',
                    mode='lines',
                    line=dict(width=0.5, color='rgba(128,128,128,0.3)'),
                    stackgroup='two',
                    hovertemplate = '%{y:,.2f} kWh'),row=1,col=1
    )

    fig.add_trace(
        go.Scatter(x=total_detail['Trading_Period'], 
                   y=total_detail['Consumption(kWh)']-(total_detail['E/W_Total(kWh)']+total_detail['North_Total(kWh)']),
                    name='Net Consumption (kWh)',
                    hoverinfo='x+y',
                    mode='lines',
                    fill='tozeroy',
                    line=dict(width=2, color='rgba(255,215,0,1)'),
                    hovertemplate = '%{y:,.2f} kWh'),
                    row=2,col=1
    )

    fig.add_trace(
        go.Scatter(x=sp_detail['Trading_Period'], y=(sp_detail['$c/kWh']), 
                    name='ISL2201 Spotprice ($c/kWh)',
                    hoverinfo='x+y',
                    mode='lines+markers',
                    line=dict(width=2, color='rgba(205,0,0,1)'),
                    hovertemplate = '%{y:,.2f} $c'),row=3,col=1
    )

    fig.add_trace(
        go.Bar(x=total_detail['Trading_Period'], y=total_detail['Electricity_Cost($)'], 
                    name='Cost w/o Solar($)',
                    marker=dict(color='rgba(193, 231, 255, 1)',line = dict(width=0)),
                    hovertemplate = '$%{y:,.2f}'),row=4,col=1
    )

    fig.add_trace(
        go.Bar(x=total_detail['Trading_Period'], y=total_detail['Cost_wSolar'], 
                    name='Cost with Solar($)',
                    marker=dict(color='rgba(157, 198, 224, 1)',line = dict(width=0)),
                    hovertemplate = '$%{y:,.2f}'),row=4,col=1
    )

    fig.add_trace(
        go.Bar(x=total_detail['Trading_Period'], y= -(total_detail['Revenue']),
                    name='Revenue from Export($)',
                    marker=dict(color='rgba(122, 166, 194, 1)',line = dict(width=0)),
                    hovertemplate = '$%{y:,.2f}'),row=4,col=1
    )

    # Add figure layout
    for n in range (4):
        fig.layout.annotations[n].update(x=0,font_size=14,xanchor ='left')
    fig.update_xaxes(type='category', categoryorder='category ascending')
    fig.update_traces(xaxis='x4')
    fig.update_layout(title_text=(f'Electricity Consumption & Solar Generation on {clk_date}'),
        title_yanchor='top',
        height = 1000,
        hovermode="x unified",
        plot_bgcolor='#FFFFFF',
        barmode = 'overlay',
        margin = dict(r=20,t=170),
        # xaxis = dict(tickangle = -45, tickfont =dict(size=10),showticklabels=True),
        legend=dict(orientation='h',yanchor='bottom',y=1.02,xanchor='right',x=1,)
        )
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0',
                     title_font_size=12,tickfont=dict(size=12))
    fig.update_yaxes(row = 1, col = 1, title='Consumption (kWh)')
    fig.update_yaxes(row = 2, col = 1, title='Consumption (kWh)')
    fig.update_yaxes(row = 3, col = 1, title='Spot Price ($c/kWh)')
    fig.update_yaxes(row = 4, col = 1, title='$NZ')
    fig.update_xaxes(showticklabels=True,tickangle= -60, showgrid=False, gridwidth=1, 
                     title_font_size=12,tickfont=dict(size=12))

    return fig

def daily_ems_charts(daily_ems):

    fig = make_subplots(rows=2, cols=1,
        shared_xaxes=True,
        subplot_titles=('Carbon Intensity (g/kWh)',
            'Carbon Emission with and without Solar (ton)'),
        vertical_spacing=0.1,
        row_width=[0.6,0.4])
    
    fig.add_trace(
        go.Scatter(x=daily_ems['Trading_Date'], y=daily_ems['Carbon_Intensity(g/KWh)'], 
                    name='Carbon Intensity (g/kWh)',
                    hoverinfo='x+y',
                    mode='lines',
                    line=dict(width=1.5, dash='dot', color='rgba(116, 100, 175,1)'),
                    hovertemplate = '%{y:,.2f} g/kWh'),row=1,col=1
    )

    fig.add_trace(
        go.Bar(x=daily_ems['Trading_Date'], y=daily_ems['Carbon_Emission_wo_Solar(t)'], 
                    name='Carbon Emission without Solar(t)',
                    marker=dict(color='rgba(183, 183, 183, 1)',line = dict(width=0)),
                    hovertemplate = '%{y:,.3f} ton'),row=2,col=1
    )

    fig.add_trace(
        go.Bar(x=daily_ems['Trading_Date'], y=daily_ems['Carbon_Emission_w_Solar(t)'], 
                    name='Carbon Emission with Solar(t)',
                    marker=dict(color='rgba(155,199,117, 1)',line = dict(width=0)),
                    hovertemplate = '%{y:,.3f} ton'),row=2,col=1
    )

    # Add figure layout
    for n in range (2):
        fig.layout.annotations[n].update(x=0,font_size=14,xanchor ='left')
    fig.update_layout(title_text= 'Daily Average Carbon Intensity & Carbon Emission from Isaac power consumption',
        height = 600,
        barmode = 'overlay',
        title_yanchor='top',
        hovermode="x unified",
        plot_bgcolor='#FFFFFF',
        margin = dict(r=20,t=170),
        xaxis = dict(tickmode = 'linear',dtick = 'M1'),
        legend=dict(orientation='h',yanchor='bottom',y=1.02,xanchor='right',x=1)
        )
    fig.update_yaxes(row=1, col=1, title='Carbon Intensity (g/kWh)',showgrid=True, gridwidth=1, gridcolor='#f0f0f0',
                 title_font_size=12,tickfont=dict(size=12)
                 )
    fig.update_yaxes(row=2, col=1, title='Carbon Emission (t)',showgrid=True, gridwidth=1, gridcolor='#f0f0f0',
                 title_font_size=12,tickfont=dict(size=12)
                 )
    fig.update_traces(xaxis='x2')
    fig.update_xaxes(showgrid=False, gridwidth=1, title_font_size=12,tickfont=dict(size=12), dtick='M1')
    return fig

def detail_ems_charts(detail_ems,clk_date):
    fig = make_subplots(rows=2, cols=1,
        shared_xaxes=True,
        subplot_titles=('Carbon Intensity (g/kWh)',
            'Carbon Emission with and without Solar (kg)'),
        vertical_spacing=0.1,
        row_width=[0.6,0.4])
    
    fig.add_trace(
        go.Scatter(x=detail_ems['Trading_Period'], y=detail_ems['Carbon_Intensity(g/KWh)'], 
                    name='Carbon Intensity (g/kWh)',
                    hoverinfo='x+y',
                    mode='lines+markers',
                    line=dict(width=1.5, dash='dash', color='rgba(116, 100, 175,1)'),
                    hovertemplate = '%{y:,.2f} g/kWh'),row=1,col=1
    )

    fig.add_trace(
        go.Bar(x=detail_ems['Trading_Period'], y=detail_ems['Carbon_Emission_wo_Solar(kg)'], 
                    name='Carbon Emission without Solar(kg)',
                    marker=dict(color='rgba(183, 183, 183, 1)',line = dict(width=0)),
                    hovertemplate = '%{y:,.3f} kg'),row=2,col=1
    )

    fig.add_trace(
        go.Bar(x=detail_ems['Trading_Period'], y=detail_ems['Carbon_Emission_w_Solar(kg)'], 
                    name='Carbon Emission with Solar(kg)',
                    marker=dict(color='rgba(155,199,117, 1)',line = dict(width=0)),
                    hovertemplate = '%{y:,.3f} kg'),row=2,col=1
    )

    # Add figure layout
    for n in range (2):
        fig.layout.annotations[n].update(x=0,font_size=14,xanchor ='left')
    fig.update_layout(title_text= f'Carbon Intensity & Carbon Emission from Isaac power consumption on {clk_date}',
        height = 600,
        barmode = 'overlay',
        title_yanchor='top',
        hovermode="x unified",
        plot_bgcolor='#FFFFFF',
        margin = dict(r=20,t=170),
        xaxis = dict(tickmode = 'linear',dtick = 'M1'),
        legend=dict(orientation='h',yanchor='bottom',y=1.02,xanchor='right',x=1)
        )
    fig.update_yaxes(row=1, col=1, title='Carbon Intensity (g/kWh)',showgrid=True, gridwidth=1, gridcolor='#f0f0f0',
                 title_font_size=12,tickfont=dict(size=12)
                 )
    fig.update_yaxes(row=2, col=1, title='Carbon Emission (kg)',showgrid=True, gridwidth=1, gridcolor='#f0f0f0',
                 title_font_size=12,tickfont=dict(size=12)
                 )
    fig.update_traces(xaxis='x2')
    fig.update_xaxes(showgrid=False, gridwidth=1, title_font_size=12,tickfont=dict(size=12), dtick='M1')
    return fig

def compare_cards(size3,syss):
    solar_detail= solar_df3.copy()
    isaac_tp = isaac_df.copy()
    sp_tp = spotprice_df.copy()
    comp_sum = pd.DataFrame(
        columns=['North Solar System','Electricity Cost w/o Solar',
                 'Electricity Generated by Solar','Electricity Cost with Solar',
                 'Revenue from exporting Solar','Final Electricity Cost'
                                     ])

    for sys in syss:

        solar_detail[f'{sys}_Total(kWh)'] = solar_detail[f'{sys}']*(size3)
        
        total_df = (isaac_tp.merge(solar_detail, on = ['Trading_Date','Trading_Period'])
                .merge(sp_tp, on =['Trading_Date','Trading_Period']))
            
        total_df['Electricity_Cost($)'] = (
            round(total_df['Consumption(kWh)']*total_df['Contract_Price($)'],3))
            
        # Net comsumption for each case
        total_df[f'Net_consum_{sys}'] = (total_df['Consumption(kWh)']-
                                        (total_df[f'{sys}_Total(kWh)'])
                                    )

        # Cost with Solar for each case
        total_df[f'Cost_wSolar_{sys}'] = total_df[f'Net_consum_{sys}']*total_df['Contract_Price($)']
        total_df.loc[total_df[f'Cost_wSolar_{sys}']<0,f'Cost_wSolar_{sys}'] = 0

        # Revenue of export
        total_df[f'Revenue_{sys}'] = -((total_df[f'Net_consum_{sys}']/1000)*total_df['$/MWh'])
        total_df.loc[total_df[f'Revenue_{sys}']<0,f'Revenue_{sys}'] =  0

        new_row = [sys,f"${total_df['Electricity_Cost($)'].sum():,.2f}",
                   f"{total_df[f'{sys}_Total(kWh)'].sum():,.2f} kWh",
                   f"${total_df[f'Cost_wSolar_{sys}'].sum():,.2f}",
                   f"${total_df[f'Revenue_{sys}'].sum():,.2f}",
                   f"${((total_df[f'Cost_wSolar_{sys}'].sum()) - (total_df[f'Revenue_{sys}'].sum())):,.2f}"
                   ]

        comp_sum.loc[len(comp_sum)] = new_row

    return dash_table.DataTable(comp_sum.to_dict('records'), [{"name": i, "id": i} for i in comp_sum.columns],
                                style_cell={'fontSize':18, 'font-family':'arial','text-align': 'center',})

def compare_charts(isaac_daily,solar_daily,total_daily,chart):

    fig = make_subplots(rows=2, cols=1,
        shared_xaxes=True,
        subplot_titles=('Daily Electricity Consumption & Solar Generation (kWh)',
            f'{chart} Deg Sys Cost & Revenue breakdown ($)'),
        vertical_spacing=0.1,
        row_width=[0.5,0.5])
    
    fig.add_trace(
        go.Scatter(x=solar_daily['Trading_Date'], y=-(solar_daily[f'{chart}_Total(kWh)']), 
                    name=f'{chart}Deg Solar System Generation(kWh)',
                    mode='lines',
                    fill='tozeroy',
                    line=dict(width=0.5, dash='dash', color='blue'),
                    hovertemplate = '%{y:,.2f} kWh'),row=1,col=1
    )

    fig.add_trace(
        go.Scatter(x=isaac_daily['Trading_Date'], y=isaac_daily['Consumption(kWh)'], name='Consumption(kWh)',
            mode='lines',
            fill='tozeroy',
            line=dict(width=0.5, color='black'),
            hovertemplate = '%{y:,.2f} kWh'),row=1,col=1
    )

    fig.add_trace(
        go.Bar(x=total_daily['Trading_Date'], y=total_daily['Electricity_Cost($)'], 
                    name='Cost w/o Solar($)',
                    marker=dict(color='rgba(128,128,128,0.3)',line = dict(width=0)),
                    hovertemplate = '$%{y:,.2f}'),row=2,col=1
    )

    fig.add_trace(
        go.Bar(x=total_daily['Trading_Date'], y=total_daily[f'Cost_wSolar_{chart}'], 
                    name=f'Cost with {chart} Deg Solar-sys($)',
                    marker=dict(color='rgba(140, 158, 202, 1)',line = dict(width=0)),
                    hovertemplate = '$%{y:,.2f}'),row=2,col=1
    )

    fig.add_trace(
        go.Bar(x=total_daily['Trading_Date'], y= -(total_daily[f'Revenue_{chart}']),
                    name=f'Revenue from Export {chart} Deg sys',
                    marker=dict(color='rgba(66, 114, 186, 1)',line = dict(width=0)),
                    hovertemplate = '$%{y:,.2f}'),row=2,col=1
    )

    # Add figure layout
    for n in range (2):
        fig.layout.annotations[n].update(x=0,font_size=22,xanchor ='left')
    fig.update_layout(title_text= f'{chart} System Visualisation Charts',
        height = 800,
        barmode = 'overlay',
        # title_yanchor='top',
        hovermode="x unified",
        plot_bgcolor='#FFFFFF',
        margin = dict(r=20, t=240),
        xaxis = dict(tickmode = 'linear',dtick = 'M1'),
        legend=dict(orientation='h',yanchor='bottom',y=1.05,xanchor='right',x=1)
        )
    fig.update_layout(
        # title = dict(font = dict(size = 20,
        #                         #  color = 'blue'
        #                          )),
        legend = dict(font = dict(size = 18,
        )),
        title = dict(font = dict(size =20)),
    )
    # fig.update_yaxes(row=1, col=1, title='kWh',showgrid=True, gridwidth=1, gridcolor='#f0f0f0',
    #              title_font_size=12,tickfont=dict(size=18),
    #              )
    # fig.update_yaxes(row=2, col=1, title='$NZ',showgrid=True, gridwidth=1, gridcolor='#f0f0f0',
    #              title_font_size=12,tickfont=dict(size=18)
    #              )

    fig.update_traces(xaxis='x2')
    fig.update_xaxes(showgrid=False, gridwidth=1, title_font_size=12,
                     tickfont=dict(size=18), dtick='M1')

    return fig

def comp_detail_charts(solar_detail,total_detail,chart,clk_date):

    fig = make_subplots(rows=4, cols=1,
        shared_xaxes=True,
        subplot_titles=('Electricity Consumption & Solar Generation (kWh)',
            'Net Electricity Consumption (kWh)',
            'ISL2201 Spot Price ($c/kWh)',
            'Electricity Cost ($)'),
        vertical_spacing=0.1,
        row_width=[0.4,0.2,0.2,0.3])

    fig.add_trace(
        go.Scatter(x=solar_detail['Trading_Period'], y=(solar_detail[f'{chart}_Total(kWh)']), 
                    name=f'{chart} Solar Generation(kWh)',
                    hoverinfo='x+y',
                    mode='lines',
                    stackgroup='one',
                    line=dict(width=0.5, color='blue'),
                    hovertemplate = '%{y:,.2f} kWh'),row=1,col=1
    )

    fig.add_trace(
        go.Scatter(x=total_detail['Trading_Period'], y=total_detail['Consumption(kWh)'], 
                    name='Consumption(kWh)',
                    hoverinfo='x+y',
                    mode='lines',
                    line=dict(width=0.5, color='black'),
                    stackgroup='two',
                    hovertemplate = '%{y:,.2f} kWh'),row=1,col=1
    )

    fig.add_trace(
        go.Scatter(x=total_detail['Trading_Period'], 
                   y=total_detail['Consumption(kWh)']-(total_detail[f'{chart}_Total(kWh)']),
                    name='Net Consumption (kWh)',
                    hoverinfo='x+y',
                    mode='lines',
                    fill='tozeroy',
                    line=dict(width=2, color='#ffa600'),
                    hovertemplate = '%{y:,.2f} kWh'),
                    row=2,col=1
    )

    fig.add_trace(
        go.Scatter(x=total_detail['Trading_Period'], y=(total_detail['$c/kWh']), 
                    name='ISL2201 Spotprice ($c/kWh)',
                    hoverinfo='x+y',
                    mode='lines+markers',
                    line=dict(width=2, color='rgba(205,0,0,1)'),
                    hovertemplate = '%{y:,.2f} $c'),row=3,col=1
    )

    fig.add_trace(
        go.Bar(x=total_detail['Trading_Period'], y=total_detail['Electricity_Cost($)'], 
                    name='Cost w/o Solar($)',
                    marker=dict(color='rgba(128,128,128,0.3)',line = dict(width=0)),
                    hovertemplate = '$%{y:,.2f}'),row=4,col=1
    )

    fig.add_trace(
        go.Bar(x=total_detail['Trading_Period'], y=total_detail[f'Cost_wSolar_{chart}'], 
                    name=f'Cost with {chart} Deg Solar-sys($)',
                    marker=dict(color='rgba(140, 158, 202, 1)',line = dict(width=0)),
                    hovertemplate = '$%{y:,.2f}'),row=4,col=1
    )

    fig.add_trace(
        go.Bar(x=total_detail['Trading_Period'], y= -(total_detail[f'Revenue_{chart}']),
                    name=f'Revenue from Export {chart} Deg sys',
                    marker=dict(color='rgba(66, 114, 186, 1)',line = dict(width=0)),
                    hovertemplate = '$%{y:,.2f}'),row=4,col=1
    )

    # Add figure layout
    for n in range (4):
        fig.layout.annotations[n].update(x=0,font_size=22,xanchor ='left')
    fig.update_xaxes(type='category', categoryorder='category ascending')
    fig.update_traces(xaxis='x4')
    fig.update_layout(title_text=(f'Electricity Consumption & Solar Generation of {chart} System on {clk_date}'),
        title_yanchor='top',
        height = 1000,
        hovermode="x unified",
        plot_bgcolor='#FFFFFF',
        barmode = 'overlay',
        margin = dict(r=20,t=240),
        # xaxis = dict(tickangle = -45, tickfont =dict(size=10),showticklabels=True),
        legend=dict(orientation='h',yanchor='bottom',y=1.05,xanchor='right',x=1,)
        )
        # Styling
    fig.update_layout(
        # title = dict(font = dict(size = 20,
        #                         #  color = 'blue'
        #                          )),
        legend = dict(font = dict(size = 18,
        )),
        title = dict(font = dict(size =20)),
    )
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0',
                     title_font_size=12,tickfont=dict(size=18))
    # fig.update_yaxes(row = 1, col = 1, title='Consumption (kWh)')
    # fig.update_yaxes(row = 2, col = 1, title='Spot Price ($c/kWh)')
    # fig.update_yaxes(row = 3, col = 1, title='Consumption (kWh)')
    # fig.update_yaxes(row = 4, col = 1, title='$NZ')
    fig.update_xaxes(showticklabels=True,tickangle= -60, showgrid=False, gridwidth=1, 
                     title_font_size=12,tickfont=dict(size=18))

    return fig

# Layout

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

tab1 = html.Div([
    html.Br(),html.Br(),
    dbc.Row([dbc.Col([
                dbc.Card([
                dbc.Row(html.H6('Select the size of West and East Solar System',
                                style={'marginBottom':'15px','font-weight':'bold'}),),
                dbc.Row([
                dbc.Col(dcc.Input(
                        id='input_size', type='number', 
                        placeholder=1700,min=0,value=1700,style={'width':'95%'}),width=4),
                dbc.Col(html.P('m2 (kW)')),        
                    ]),
                ],style={'padding':'10px','width':'85%'}),
            ],width=4),
            dbc.Col([
                dbc.Card([
                dbc.Row(html.H6('Select the size of North Solar System',
                                style={'marginBottom':'15px','font-weight':'bold'}),),
                dbc.Row([
                dbc.Col(dcc.Input(
                        id='input_size2', type='number', 
                        placeholder=250,min=0,value=250,style={'width':'95%'}),width=4),
                dbc.Col(html.P('m2 (kW)')),        
                    ]),
                ],style={'padding':'10px','width':'85%'}),
            ],width=4),
        ]),

    html.Br(),html.Br(),
    html.H3('Electricity Consumption & Solar System Generation Charts'),
    html.Br(),
    dbc.Row(html.Div(id='summary',children={})),
    html.Br(),
    dbc.Row([
        dcc.Loading(id='main_loading',children=
                    [dbc.Card(dcc.Graph(id='overview-graph', figure={},
                                        clickData=None, 
                                        hoverData=None))],
            ),
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
    html.Br(),html.Br(),html.Br(),
    html.H3('Carbon Intensity and Carbon Emission Charts'),
    html.Br(),
    dbc.Row(html.Div(id='ems-summary',children={})),
    html.Br(),
    dbc.Row([  
        dcc.Loading(id='ems_loading',children=
            [dbc.Card(dcc.Graph(id='ems-graph', figure={}, clickData=None, 
                hoverData=None)
            )],
            type = 'default',
        )
    ]),
    html.Br(),
    dbc.Row([  
        dcc.Loading(id='ems_detail_loading',children=
            [dbc.Card(dcc.Graph(id='ems-detail-graph', figure={}, clickData=None, 
                hoverData=None)
            )],
            type = 'default',
        )
    ]),

    ])

tab2 = html.Div([
    html.Br(),html.Br(),
    dbc.Row([
            dbc.Col([
                dbc.Card([
                dbc.Row(html.H6('Select the size of North Solar System',
                                style={'marginBottom':'15px','font-weight':'bold'}),),
                dbc.Row([
                dbc.Col(dcc.Input(
                        id='input_size3', type='number', 
                        placeholder=250,min=0,value=250,style={'width':'95%'}),width=4),
                dbc.Col(html.P('m2 (kW)')),        
                    ]),
                ],style={'padding':'10px','width':'85%'}),
            ],width=4),
            dbc.Col([
                dbc.Card([
                dbc.Row(html.H6('Choose the North Solar System for comparision',
                                style={'marginBottom':'15px','font-weight':'bold'}),),
                dbc.Row([dcc.Dropdown(
                    options=sys_vals,
                    multi=True,
                    clearable=False,
                    value=['A31'],
                    id="sys-checkbox")
                ]),
            ],style={'padding':'10px'}),
            ],width=6),
        ]),

    html.Br(), html.Br(),
    html.H4('Comparison Summary'),
    html.Br(),
    dbc.Row(html.Div(id='compare-summary',children={})),
    html.Br(),html.Br(),
    html.Hr(),html.Br(),
    dbc.Row([
            dbc.Col([
                dbc.Card([
                dbc.Row(html.H6('Choose the North Solar System for visualisation',
                                style={'marginBottom':'15px','font-weight':'bold'}),),
                dbc.Row([dcc.Dropdown(
                    options= sys_vals,
                    clearable=False,
                    value='A31',
                    id="chart-checkbox")
                ]),
            ],style={'padding':'10px'}),
            ],width=3),
        ]),
    html.Br(),html.Br(),
    dbc.Row([  
        dcc.Loading(id='comp_loading',children=
            [dbc.Card(dcc.Graph(id='compare-graph', figure={}, clickData=None, 
                hoverData=None)
            )],
            type = 'default',
        )
    ]),
    html.Br(),html.Br(),
    dbc.Row([  
        dcc.Loading(id='detail_comp_loading',children=
            [dbc.Card(dcc.Graph(id='detail-compare-graph', figure={}, clickData=None, 
                hoverData=None)
            )],
            type = 'default',
        )
    ]),
])

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
    html.H2("AAAAA Construction Visualisation", style={'font-family':'arial','textAlign':'center'}),
    html.Br(),html.Br(),
       
    dcc.Tabs(id="tabs-charts", value='tab-1', children=[
        dcc.Tab(label='DETAIL VISUALISATION', value='tab-1'),
        dcc.Tab(label='NORTH FACING SOLAR ARRAYS COMPARISON', value='tab-2'),
    ]),
    html.Div(id='tabs-content')
],style={ 'padding':'15px'},fluid=True)


# Callback

@callback(Output('tabs-content', 'children'),
              Input('tabs-charts', 'value'))
def render_content(tab):
    if tab == 'tab-1':
        return tab1
    elif tab == 'tab-2':
        return tab2



@callback(
    Output(component_id='summary', component_property='children'),
    Input(component_id='input_size', component_property='value'),
    Input(component_id='input_size2', component_property='value')
)
def summary_cards_update(size,size2):
    return summary_cards(size,size2)


@callback(
    Output(component_id='overview-graph', component_property='figure'),
    Input(component_id='input_size', component_property='value'),
    Input(component_id='input_size2', component_property='value')
)
def update_mainchart(size,size2):
    soldf,soldf2 = sol_df(size,size2)
    

    total_df = (isaac_df.merge(soldf, on = ['Trading_Date','Trading_Period'])
                .merge(soldf2, on = ['Trading_Date','Trading_Period'])
                .merge(spotprice_df, on =['Trading_Date','Trading_Period'])
                )
    total_df['Electricity_Cost($)'] = (
        round(total_df['Consumption(kWh)']*total_df['Contract_Price($)'],3))
    total_df['Net_consum'] = (total_df['Consumption(kWh)']-
                              (total_df['E/W_Total(kWh)'])-(total_df['North_Total(kWh)'])
                              )
    # Cost with Solar
    total_df['Cost_wSolar'] = total_df['Net_consum']*total_df['Contract_Price($)']
    total_df.loc[total_df['Cost_wSolar']<0,'Cost_wSolar'] = 0
    # Revenue of export
    total_df['Revenue'] = -((total_df['Net_consum']/1000)*total_df['$/MWh'])
    total_df.loc[total_df['Revenue']<0,'Revenue'] =  0

    total_daily = total_df.groupby('Trading_Date',as_index=False)[['Electricity_Cost($)','Cost_wSolar','Revenue']].sum()


    isaac_daily = isaac_df.groupby('Trading_Date',as_index=False).sum(numeric_only = True)

    solar_daily = soldf.merge(soldf2, on = ['Trading_Date','Trading_Period'])
    solar_daily = solar_daily.groupby('Trading_Date',as_index=False).sum(numeric_only = True)
    solar_daily = solar_daily.iloc[:,[0,3,4,5,7]].copy()

    sp_daily = spotprice_df.groupby('Trading_Date',as_index=False).median(numeric_only = True)
    sp_daily['$c/kWh'] = round(sp_daily['$/MWh']/10,2)

    fig = main_chart(isaac_daily,solar_daily,sp_daily,total_daily)

    return fig        

@callback(
    Output(component_id='detail-graph', component_property='figure'),
    Input(component_id='input_size', component_property='value'),
    Input(component_id='input_size2', component_property='value'),
    Input(component_id='overview-graph', component_property='clickData')
)
def update_group_charts(size,size2,clk_data):
    soldf,soldf2 = sol_df(size,size2)
    solar_detail = soldf.merge(soldf2, on = ['Trading_Date','Trading_Period'])

    total_df = (isaac_df.merge(soldf, on = ['Trading_Date','Trading_Period'])
                .merge(soldf2, on = ['Trading_Date','Trading_Period'])
                .merge(spotprice_df, on =['Trading_Date','Trading_Period'])
                )
    total_df['Electricity_Cost($)'] = (
        round(total_df['Consumption(kWh)']*total_df['Contract_Price($)'],3))
    total_df['Net_consum'] = (total_df['Consumption(kWh)'] - 
                              (total_df['E/W_Total(kWh)'] + total_df['North_Total(kWh)'])
                            )
    # Cost with Solar
    total_df['Cost_wSolar'] = total_df['Net_consum']*total_df['Contract_Price($)']
    total_df.loc[total_df['Cost_wSolar']<0,'Cost_wSolar'] = 0
    # Revenue of export
    total_df['Revenue'] = -((total_df['Net_consum']/1000)*total_df['$/MWh'])
    total_df.loc[total_df['Revenue']<0,'Revenue'] =  0
    

    if clk_data is None:
        default = '2022-02-01'
        clk_date = default
        df2 = isaac_df[isaac_df['Trading_Date'] == clk_date]
        df3 = solar_detail[solar_detail['Trading_Date'] == clk_date]
        df4 = spotprice_df[spotprice_df['Trading_Date'] == clk_date]
        df4['$c/kWh'] = round(df4['$/MWh']/10,2)
        df5 = total_df[total_df['Trading_Date'] == clk_date]
        fig2 = group_charts(df2,df3,df4,df5,clk_date)

        return fig2
    else:

        clk_date = clk_data['points'][0]['x']
        df2 = isaac_df[isaac_df['Trading_Date'] == clk_date]
        df3 = solar_detail[solar_detail['Trading_Date'] == clk_date]
        df4 = spotprice_df[spotprice_df['Trading_Date'] == clk_date]
        df4['$c/kWh'] = round(df4['$/MWh']/10,2)
        df5 = total_df[total_df['Trading_Date'] == clk_date]

        fig2 = group_charts(df2,df3,df4,df5,clk_date)
        
        return fig2        


@callback(
    Output(component_id='ems-summary', component_property='children'),
    Input(component_id='input_size', component_property='value'),
    Input(component_id='input_size2', component_property='value')
)
def ems_cards_update(size,size2):
    soldf,soldf2 = sol_df(size,size2)

    grp_df = (isaac_df.merge(soldf, on = ['Trading_Date','Trading_Period'])
              .merge(ci_df, on =['Trading_Date','Trading_Period'])
              .merge(soldf2, on = ['Trading_Date','Trading_Period'])
              )
    grp_df['Carbon_Emission_wo_Solar(t)'] = (
        round(grp_df['Consumption(kWh)']*grp_df['Carbon_Intensity(g/KWh)']/1000000,3))
    grp_df['Net_consum(kWh)'] = (grp_df['Consumption(kWh)']-(grp_df['E/W_Total(kWh)'])
                                 - (grp_df['North_Total(kWh)'])
                                 )
    # Cost with Solar
    grp_df['Carbon_Emission_w_Solar(t)'] = (
        round(grp_df['Net_consum(kWh)']*grp_df['Carbon_Intensity(g/KWh)']/1000000,3))
    grp_df.loc[grp_df['Carbon_Emission_w_Solar(t)']<0,'Carbon_Emission_w_Solar(t)'] = 0


    daily_df = (grp_df.groupby('Trading_Date',as_index=False)
                .agg({'Carbon_Emission_wo_Solar(t)':'sum','Carbon_Emission_w_Solar(t)':'sum',
                      'Carbon_Intensity(g/KWh)':'mean'})
                .reset_index()
                )
    return ems_summary_cards(daily_df)


@callback(
    Output(component_id='ems-graph', component_property='figure'),
    Input(component_id='input_size', component_property='value'),
    Input(component_id='input_size2', component_property='value')
)
def update_emschart(size,size2):
    soldf,soldf2 = sol_df(size,size2)

    grp_df = (isaac_df.merge(soldf, on = ['Trading_Date','Trading_Period'])
                .merge(soldf2, on = ['Trading_Date','Trading_Period'])
                .merge(ci_df, on =['Trading_Date','Trading_Period'])
                )
    grp_df['Carbon_Emission_wo_Solar(t)'] = (
        round(grp_df['Consumption(kWh)']*grp_df['Carbon_Intensity(g/KWh)']/1000000,3))
    grp_df['Net_consum(kWh)'] = (grp_df['Consumption(kWh)']-
                                 (grp_df['E/W_Total(kWh)'] + grp_df['North_Total(kWh)']))
    # Cost with Solar
    grp_df['Carbon_Emission_w_Solar(t)'] = (
        round(grp_df['Net_consum(kWh)']*grp_df['Carbon_Intensity(g/KWh)']/1000000,3))
    grp_df.loc[grp_df['Carbon_Emission_w_Solar(t)']<0,'Carbon_Emission_w_Solar(t)'] = 0


    daily_df = (grp_df.groupby('Trading_Date',as_index=False)
                .agg({'Carbon_Emission_wo_Solar(t)':'sum','Carbon_Emission_w_Solar(t)':'sum',
                      'Carbon_Intensity(g/KWh)':'mean'})
                .reset_index()
                )

    fig = daily_ems_charts(daily_df)

    return fig        

@callback(
    Output(component_id='ems-detail-graph', component_property='figure'),
    Input(component_id='input_size', component_property='value'),
    Input(component_id='input_size2', component_property='value'),
    Input(component_id='ems-graph', component_property='clickData'),
)
def update_emsdetailchart(size,size2,clk_data):
    soldf,soldf2 = sol_df(size,size2)

    grp_df = (isaac_df.merge(soldf, on = ['Trading_Date','Trading_Period'])
              .merge(soldf2, on = ['Trading_Date','Trading_Period'])
              .merge(ci_df, on =['Trading_Date','Trading_Period'])
              )
    grp_df['Carbon_Emission_wo_Solar(kg)'] = (
        round(grp_df['Consumption(kWh)']*grp_df['Carbon_Intensity(g/KWh)']/1000,3))
    grp_df['Net_consum(kWh)'] = (grp_df['Consumption(kWh)']-
                                (grp_df['E/W_Total(kWh)'] + grp_df['North_Total(kWh)'])
                                )
    # Cost with Solar
    grp_df['Carbon_Emission_w_Solar(kg)'] = (
        round(grp_df['Net_consum(kWh)']*grp_df['Carbon_Intensity(g/KWh)']/1000,3))
    grp_df.loc[grp_df['Carbon_Emission_w_Solar(kg)']<0,'Carbon_Emission_w_Solar(kg)'] = 0

    detail_ems = grp_df.copy()

    if clk_data is None:
        default = '2022-02-01'
        clk_date = default
        detail_ems = grp_df[grp_df['Trading_Date'] == clk_date]
        fig2 = detail_ems_charts(detail_ems,clk_date)
        return fig2
    
    else:
        clk_date = clk_data['points'][0]['x']
        detail_ems = grp_df[grp_df['Trading_Date'] == clk_date]
        fig2 = detail_ems_charts(detail_ems,clk_date)
        return fig2

@callback(
    Output(component_id='compare-summary', component_property='children'),
    Input(component_id='input_size3', component_property='value'),
    Input(component_id='sys-checkbox', component_property='value'),
)
def compare_summary_update(size3,syss):
    return compare_cards(size3,syss)

@callback(
    Output(component_id='compare-graph', component_property='figure'),
    Input(component_id='input_size3', component_property='value'),
    Input(component_id='chart-checkbox', component_property='value'),
)
def update_comp_chart(size3,chart):
    solar_detail= solar_df3.copy()
    solar_detail[f'{chart}_Total(kWh)'] = solar_detail[f'{chart}']*(size3)

    total_df = (isaac_df.merge(solar_detail, on = ['Trading_Date','Trading_Period'])
                .merge(spotprice_df, on =['Trading_Date','Trading_Period'])
                )
    total_df['Electricity_Cost($)'] = (
        round(total_df['Consumption(kWh)']*total_df['Contract_Price($)'],3))
    
    total_df[f'Net_consum_{chart}'] = (total_df['Consumption(kWh)']-
                              (total_df[f'{chart}_Total(kWh)'])
                              )
    
    # Cost with Solar
    total_df[f'Cost_wSolar_{chart}'] = total_df[f'Net_consum_{chart}']*total_df['Contract_Price($)']
    total_df.loc[total_df[f'Cost_wSolar_{chart}']<0,f'Cost_wSolar_{chart}'] = 0

    # Revenue of export
    total_df[f'Revenue_{chart}'] = -((total_df[f'Net_consum_{chart}']/1000)*total_df['$/MWh'])
    total_df.loc[total_df[f'Revenue_{chart}']<0,f'Revenue_{chart}'] =  0


    total_daily = total_df.groupby('Trading_Date',as_index=False)[['Electricity_Cost($)',
                    f'Cost_wSolar_{chart}',f'Revenue_{chart}']].sum()


    isaac_daily = isaac_df.groupby('Trading_Date',as_index=False).sum(numeric_only = True)

    solar_daily = solar_detail.groupby('Trading_Date',as_index=False).sum(numeric_only = True)

    fig = compare_charts(isaac_daily,solar_daily,total_daily,chart)

    return fig        

@callback(
    Output(component_id='detail-compare-graph', component_property='figure'),
    Input(component_id='input_size3', component_property='value'),
    Input(component_id='chart-checkbox', component_property='value'),
    Input(component_id='compare-graph', component_property='clickData')
)
def update_comp_detail_charts(size3,chart,clk_data):

    solar_detail= solar_df3.copy()
    solar_detail[f'{chart}_Total(kWh)'] = solar_detail[f'{chart}']*(size3)

    total_df = (isaac_df.merge(solar_detail, on = ['Trading_Date','Trading_Period'])
                .merge(spotprice_df, on =['Trading_Date','Trading_Period'])
                )
    total_df['Electricity_Cost($)'] = (
        round(total_df['Consumption(kWh)']*total_df['Contract_Price($)'],3))
    
    total_df[f'Net_consum_{chart}'] = (total_df['Consumption(kWh)']-
                              (total_df[f'{chart}_Total(kWh)'])
                              )
        
    # Cost with Solar
    total_df[f'Cost_wSolar_{chart}'] = total_df[f'Net_consum_{chart}']*total_df['Contract_Price($)']
    total_df.loc[total_df[f'Cost_wSolar_{chart}']<0,f'Cost_wSolar_{chart}'] = 0

    # Revenue of export
    total_df[f'Revenue_{chart}'] = -((total_df[f'Net_consum_{chart}']/1000)*total_df['$/MWh'])
    total_df.loc[total_df[f'Revenue_{chart}']<0,f'Revenue_{chart}'] =  0
  
    if clk_data is None:
        default = '2022-02-01'
        clk_date = default
        df1 = solar_detail[solar_detail['Trading_Date'] == clk_date]
        df2 = total_df[total_df['Trading_Date'] == clk_date]
        df2['$c/kWh'] = round(df2['$/MWh']/10,2)

        fig2 = comp_detail_charts(df1,df2,chart,clk_date)

        return fig2
    else:

        clk_date = clk_data['points'][0]['x']
      
        df1 = solar_detail[solar_detail['Trading_Date'] == clk_date]
        df2 = total_df[total_df['Trading_Date'] == clk_date]
        df2['$c/kWh'] = round(df2['$/MWh']/10,2)

        fig2 = comp_detail_charts(df1,df2,chart,clk_date)
        
        return fig2        

app = dashapp.server.wsgi_app

if __name__ == "__main__":
    dashapp.run_server(host='0.0.0.0',port=80,debug=False)