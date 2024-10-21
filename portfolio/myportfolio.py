# from nsetools import Nse
import pandas as pd
import numpy as np
import requests
import jugaad_data as jd
import streamlit as st
from jugaad_data.nse import NSELive
import warnings; warnings.simplefilter('ignore')


n = NSELive()
# This script processes the holdings data from a CSV file.
# It reads the holdings data, sorts it based on the Profit & Loss (P&L) value in descending order.
# The sorted data is stored back in the original DataFrame, resetting the index.
print("loading holdings data")
my_holdings_org = pd.read_csv('.\\holdings.csv')
my_holdings_org.sort_values(['P&L'],ascending=False,inplace=True,ignore_index=True)

# This function retrieves the latest stock price, 52-week high and low, 
# and the sector of the given stock from a financial data source.
def get_stock_price(stock_name):
    try:
        quote=n.stock_quote(stock_name)
        latest_price=quote['priceInfo']['lastPrice']
        high_52w=quote['priceInfo']['weekHighLow']['max']
        low_52w=quote['priceInfo']['weekHighLow']['min']
        sector = n.stock_quote(stock_name)['industryInfo']['sector']
        if sector=='':
            sector = stock_name
        return latest_price,high_52w,low_52w,sector
    except:
        return None,None,None,None

# This code handles the manipulation of the user’s portfolio holdings.
# It creates a copy of the original holdings and filters to retain only specific columns. 
my_holdings=my_holdings_org.copy()
my_holdings=my_holdings[['Instrument','Qty.','Avg. cost']]

# This script retrieves the latest stock prices, 52-week highs, 52-week lows, and sector information for a list of instruments held in a portfolio.
# It handles errors gracefully by appending default values in case of exceptions.
print("Collecting stock prices")
latest_price_list=[]
high_52w_list=[]
low_52w_list=[]
sector_list=[]
for instrument in my_holdings['Instrument']:
    try:
        latest_price,high_52w,low_52w,sector= get_stock_price(instrument)
        latest_price_list.append(latest_price)
        high_52w_list.append(high_52w)
        low_52w_list.append(low_52w)
        sector_list.append(sector)
    except : 
        print(instrument)
        latest_price_list.append(0)
        high_52w_list.append(0)
        low_52w_list.append(0)
        sector_list.append(None)
my_holdings['sector']=sector_list


# Get the Latest price and calculate the P&L  
my_holdings.insert(len(my_holdings.columns),"LTP",latest_price_list)
my_holdings['Cur. val']= my_holdings['Qty.'] * my_holdings['LTP']
my_holdings['P&L'] = (my_holdings['Qty.'] * my_holdings['LTP'] ) - ( my_holdings['Qty.'] * my_holdings['Avg. cost'])
total_invested=np.matmul(my_holdings['Qty.'], my_holdings['Avg. cost'])
my_holdings['total_invested']=my_holdings['Qty.']* my_holdings['Avg. cost']
my_holdings['invested %'] =np.round((my_holdings['Qty.']* my_holdings['Avg. cost'])/total_invested * 100,2)

investment_df=my_holdings[['Instrument','sector','total_invested',  'Cur. val', 'P&L','invested %']].sort_values(by='total_invested',ascending=False).reset_index(drop=True)
sector_invst_df=investment_df.groupby('sector').sum('total_invested').sort_values(by=['P&L','invested %'],ascending=False).reset_index(drop=False)

print(sector_invst_df)
print(investment_df)

# Stocks that are above 52 Week High
## "Above 52w" Coloumn , +ve numbers mean that stock is above is 52w high and sellable
my_holdings.insert(len(my_holdings.columns),"High 52w price",high_52w_list)
my_holdings.insert(len(my_holdings.columns),"Low 52w price",low_52w_list)
my_holdings['Above 52w']= my_holdings['LTP']- my_holdings['High 52w price']
yesno=["YES" if v>0 else "NO" for v in list(my_holdings['Above 52w']) ]
my_holdings.insert(len(my_holdings.columns),"Any Above 52w",yesno)
wk52_high_df=my_holdings[my_holdings['P&L']>0][['Instrument','sector', 'Qty.','P&L', 'LTP', 'High 52w price', 'Above 52w','Any Above 52w']].sort_values(by='Above 52w',ascending=False)
wk52_high_df.reset_index(drop=True,inplace=True)    
print(wk52_high_df)


# Stocks that are Below 52 Week Low , to check if the stocks that have gone really bad
## "Below 52w" column -ve number means stock is below its 52w low and in bad state
my_holdings['Below 52w']=   my_holdings['LTP'] - my_holdings['Low 52w price']
yesno1=["YES" if v<0 else "NO" for v in list(my_holdings['Below 52w']) ]
my_holdings.insert(len(my_holdings.columns),"Any Below 52w",yesno1)
wk52_low_df=my_holdings[['Instrument','sector', 'Qty.','P&L', 'LTP', 'Low 52w price', 'Below 52w','Any Below 52w']].sort_values(by='Below 52w',ascending=True)
wk52_low_df.reset_index(drop=True,inplace=True)
print(wk52_low_df)

# # Top gainers ##
# headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"}
# res=requests.get(r"https://www.nseindia.com/api/live-analysis-variations?index=gainers",headers=headers)
# all_data=res.json()['NIFTY']['data']
# top_gainer_df=pd.DataFrame()
# def top_gainers(data):
#     d=dict((k, data[k]) for k in ['symbol','open_price','high_price','low_price','ltp','perChange'] if k in data)
#     return d
# for data in all_data:
#     dic= top_gainers(data)
#     top_gainer_df=top_gainer_df.append(dic,ignore_index=True)
# top_gainer_df=top_gainer_df[['symbol','ltp','high_price', 'low_price','open_price', 'perChange']]
# print(top_gainer_df)    