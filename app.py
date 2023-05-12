import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

menu = pd.read_csv('data/menu.csv')
menu_prices = pd.read_csv('data/menu_prices.csv')
menu_prices['datetime'] = pd.to_datetime(menu_prices['datetime'])
menu_prices = menu_prices.merge(menu[['id', 'menu_name']], on='id')

items = pd.read_csv('data/items.csv')
fulldata = pd.read_csv('data/fulldata.csv')
fulldata['datetime'] = pd.to_datetime(fulldata['datetime'])
fulldata = fulldata.merge(items[['series_id', 'item_name']], on='series_id')

predictable_items = pd.read_csv('data/predictable_items.csv')

datapredictions = pd.read_csv('data/datapredictions.csv')
datapredictions['datetime'] = pd.to_datetime(datapredictions['datetime'])

from dash import Dash, dcc, html, Input, Output
import plotly.express as px
from datetime import date
import dash_bootstrap_components as dbc

def get_first_day(date):
    return date.replace(day=1)

app = Dash(__name__)

server = app.server

menu_dropdown_component = html.Div([
    html.Div('Entree'),
    dcc.Dropdown(options=[{'label': i, 'value': i} for i in menu.query('category=="entree"')['menu_name'].unique()], value='Ham Egg and Cheese Melt', id='entree-dropdown'),
    html.Div('Drink'),
    dcc.Dropdown(options=[{'label': i, 'value': i} for i in menu.query('category=="drink"')['menu_name'].unique()], value='Cup of Orange Juice', id='drink-dropdown'),
    html.Div('Side'),
    dcc.Dropdown(options=[{'label': i, 'value': i} for i in menu.query('category=="side"')['menu_name'].unique()], value='2 Stips of Bacon', id='side-dropdown'),
], style={'columnCount': 3,'textAlign': 'center', 'width': '90%', 'margin': 'auto'})

menu_component = html.Div([
    html.H2('What do you want to eat for breakfast?'),
    menu_dropdown_component,
], style={'textAlign': 'center'})

price_readout = html.Div([
        html.Div([
        html.H2('The price of your meal cost 0.00$ (0%) more than before!', id='delta-price-readout', style={'textAlign': 'center'}),
        html.A('From 0.00$ in ', id='start-date-price-readout'),
        dcc.DatePickerSingle(
            id='picker-start-range',
            min_date_allowed=date(1993, 3, 1),
            max_date_allowed=date(2023, 3, 1),
            date=date(2003, 3, 1),
            display_format='MMMM Y',
            number_of_months_shown= 3,
            day_size= 30,
        ),
        html.A(' to 0.00$ in ', id='end-date-price-readout'),
        dcc.DatePickerSingle(
            id='picker-end-range',
            min_date_allowed=date(1993, 3, 1),
            max_date_allowed=date(2023, 3, 1),
            date=date(2023, 3, 1),
            display_format='MMMM Y',
            style={'text-align': 'center'},
            number_of_months_shown= 3,
            day_size= 30,    
        ),
    ]),
], style={'textAlign': 'center'})

methodology = html.Div([
    html.Div([
        html.Details([html.Summary('Methodolgy'),
                      html.Plaintext('*No entree was picked', id='entree-methodology', style={'font-size': '8px'}), html.Div(), 
                      html.Plaintext('*No drink was picked', id='drink-methodology', style={'font-size': '8px'}), html.Div(), 
                      html.Plaintext('*No side was picked', id='side-methodology', style={'font-size': '8px'})], open=False),
    ], style={'textAlign': 'left', 'font-size': '12px', 'width': '90%', 'margin': 'auto'}),
])

# Full Inspection

full_dropdown_component = html.Div([
    dcc.Dropdown(options=[{'label': i, 'value': i} for i in items['item_name'].unique()], value=['Eggs, grade A, large, per doz.'], id='full-item', multi=True),
], style={'textAlign': 'center', 'width': '90%', 'margin': 'auto'})

data_source = html.Div([
    html.Div([
        html.Details([html.Summary('Methodolgy'),
                      dcc.Markdown('''
                                    Data collected from the [Food](https://download.bls.gov/pub/time.series/ap/) section of [Average Price Data](https://www.bls.gov/data/) from US Bureau of Labor Statistics (BLS) Website.
                                    '''
                                    , style={'font-size': '8px'}), html.Div(), 
                      ], open=False),
    ], style={'textAlign': 'left', 'font-size': '12px', 'width': '90%', 'margin': 'auto'}),
])

hist_price_inflation_toggle = html.Div([
    dcc.Checklist(
        ['Inflation Adjusted Price'],
        value=['historical'],
        id = 'historical',
        labelStyle={'display': 'inline-block'}
    )
], style={'textAlign': 'left', 'width': '90%', 'margin': 'auto'})

# Predictions

prediction_dropdown_component = html.Div([
    dcc.Dropdown(options=[{'label': i, 'value': i} for i in predictable_items['item_name'].unique()], value='All Uncooked Beef Steaks, per lb. (453.6 gm)', id='prediction-item'),
], style={'textAlign': 'center', 'width': '90%', 'margin': 'auto'})

prediction_methodology = html.Div([
    html.Div([
        html.Details([html.Summary('Methodolgy'),
                      html.Plaintext('USDA Grocery Prediction: 6% monthly growth based on "Food at Home" price forcasting (April 2023) [ Predicted Price = LastMonth*(1 + 0.03)^(Month) ]', style={'font-size': '8px'}), html.Div(), 
                      html.Plaintext('Continued Average: Average monthly growth of previous year [ Predicted Price = LastMonth*(1 + AverageChange)^(Month) ]', style={'font-size': '8px'}), html.Div(), 
                      html.Plaintext('Simple Regression: Using RandomForestRegressor from SciKit-Learn', style={'font-size': '8px'})], open=False),
    ], style={'textAlign': 'left', 'font-size': '12px', 'width': '90%', 'margin': 'auto'}),
])

# large compile
Intro = html.Div([
    html.H1('Breakfast and Rising Food Prices'),
], style={'textAlign': 'center'})

Breakfast = html.Div([
    menu_component,
    price_readout,
    dcc.Graph(id="menu-graph"),
    methodology
])

full_inspection = html.Div([
    html.H2('Everythings been getting more expensive!', style={'textAlign': 'center'}),
    full_dropdown_component,
    dcc.Graph(id="full-graph"),
    data_source,
    hist_price_inflation_toggle
])

predictions = html.Div([
    dcc.Markdown('''
                 ## The USDA predicts that food prices will continue to rise [6.6%](https://www.ers.usda.gov/data-products/food-price-outlook/)
                    ''', style={'textAlign': 'center'}),
    prediction_dropdown_component,
    dcc.Graph(id="predictions-graph"),
    prediction_methodology
])

app.layout = html.Div([
    Intro,
    Breakfast,
    full_inspection,
    predictions
])

@app.callback(
    Output("menu-graph", "figure"), 
    Output("start-date-price-readout", "children"),
    Output("end-date-price-readout", "children"),
    Output("delta-price-readout", "children"),
    Output("entree-methodology", "children"),
    Output("drink-methodology", "children"),
    Output("side-methodology", "children"),
    Input("picker-start-range", "date"),
    Input("picker-end-range", "date"),
    Input("entree-dropdown", "value"),
    Input("drink-dropdown", "value"),
    Input("side-dropdown", "value"),
    )

def update_bar_chart(start_date, end_date, entree, drink, side):
    start_date = get_first_day(pd.to_datetime(start_date))
    end_date = get_first_day(pd.to_datetime(end_date))
    df = menu_prices.query("menu_name in {}".format([entree, drink, side]))
    df = df.query("'{}'<=datetime<='{}'".format(start_date, end_date))
    
    fig = px.area(df, x="datetime", y="price", color="menu_name", title="Historical Prices of Your Breakfast")
    fig.update_layout(legend=dict(orientation="h",yanchor="bottom",y=1,
        xanchor="left",
        x=0,
        title='Your Order:',
    ), xaxis_title='', yaxis_title=None, yaxis_tickprefix='$', yaxis_tickformat=',.2f', title_x=0.5, margin = dict(t=100, b=0, l=100, r=100)
    )
    
    st = df.query("datetime=='{}'".format(start_date))
    nd = df.query("datetime=='{}'".format(end_date))
    startsum = st['price'].sum()
    endsum = nd['price'].sum()
    deltasum = endsum - startsum
    percentchange = endsum/startsum*100
    start = 'From {:.2f}$ in '.format(startsum)
    end = ' to {:.2f}$ in '.format(endsum)
    delta = 'The price of your meal cost {:.2f}$ ({:.1f}%) more than before!'.format(deltasum, percentchange)
    
    df1 = menu.query("menu_name in {}".format([entree, drink, side]))
    
    ent_meth = ''
    ent = df1.query("category=='entree'")['methodology'].tolist()
    if len(ent) > 0:
        ent_meth = ent[0]
    else:
        ent_meth = 'No entree was picked'
    
    drk_met = ''
    drk = df1.query("category=='drink'")['methodology'].tolist()
    if len(drk) > 0:
        drk_met = drk[0]
    else:
        drk_met = 'No drink was picked'
        
    sid_met = ''
    sid = df1.query("category=='side'")['methodology'].tolist()
    if len(sid) > 0:
        sid_met = sid[0]
    else:
        sid_met = 'No side was picked'
    
    entree_methodology = '*For {}: {}'.format(entree, ent_meth)
    drink_methodology = '*For {}: {}'.format(drink, drk_met)
    side_methodology = '*For {}: {}'.format(side, sid_met)
    
    return fig, start, end, delta, entree_methodology, drink_methodology, side_methodology

@app.callback(
    Output("full-graph", "figure"),
    Input("full-item", "value"),
    Input("historical", "value"),
    )
def full_inspection(items, inflation):
    
    dfa = fulldata.query("item_name in {}".format(items))
    
    fig = px.line(dfa, x="datetime", y="adjusted_value", color="item_name", title="Historical Prices of Groceries")
    
    if inflation == ['historical']:
        fig = px.line(dfa, x="datetime", y="value", color="item_name", title="Historical Prices of Groceries")
    
    fig.update_layout(legend=dict(orientation="h",yanchor="bottom",y=1,
        xanchor="left",
        x=0,
        title='',
    ), xaxis_title='', yaxis_title=None, yaxis_tickprefix='$', yaxis_tickformat=',.2f', title_x=0.5, margin = dict(t=100, b=0, l=100, r=100)
    )
    fig.update_xaxes(rangeslider_visible=True)
    return fig

@app.callback(
    Output("predictions-graph", "figure"),
    Input("prediction-item", "value"),
    )
def predictions(item):
    start_date = '2020-04-01'
    end_date = '2024-04-01'
    dfa = fulldata.query("item_name == '{}'".format(item))
    dfb = datapredictions.query("item_name == '{}'".format(item))
    fig = px.line(dfb, x="datetime", y=['usda grocery prediction', 'continued average', 'simple regression'], title="Historical Prices of {}".format(item), range_x=[start_date, end_date])
    fig.add_scatter(x=dfa.datetime, y=dfa.value, mode='lines', name='actual')
    fig.update_xaxes(rangeslider_visible=True)
    fig.update_layout(legend=dict(orientation="h",yanchor="bottom",y=1,
        xanchor="left",
        x=0,
        title='Prediction Methods',
    ), xaxis_title='', yaxis_title=None, yaxis_tickprefix='$', yaxis_tickformat=',.2f', title_x=0.5, margin = dict(t=100, b=0, l=100, r=100)
    )
    return fig



if __name__ == '__main__':
    app.run_server()