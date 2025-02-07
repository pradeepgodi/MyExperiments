import pandas as pd
import numpy as np
import jugaad_data as jd
from jugaad_data.nse import NSELive


n = NSELive()

print("loading holdings data")
my_holdings = pd.read_csv('.\\holdings.csv')
my_holdings.sort_values(['P&L'],ascending=False,inplace=True,ignore_index=True)
my_holdings=my_holdings[['Instrument','Qty.','Avg. cost']]

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

print("Collecting stock prices")
latest_price_list=[]
high_52w_list=[]
low_52w_list=[]
sector_list=[]

# def enrich_holdings():
for instrument in my_holdings['Instrument']:
    data = n.stock_quote(instrument)
    # print(instrument)
    # print(data)
    try:
        latest_price,high_52w,low_52w,sector= get_stock_price(instrument)
        latest_price_list.append(latest_price)
        high_52w_list.append(high_52w)
        low_52w_list.append(low_52w)
        sector_list.append(sector)
    except : 
        latest_price_list.append(0)
        high_52w_list.append(0)
        low_52w_list.append(0)
        sector_list.append(None)
# print(sector_list)        
my_holdings['sector']=sector_list

my_holdings.insert(len(my_holdings.columns),"LTP",latest_price_list)
my_holdings['Cur. val']= my_holdings['Qty.'] * my_holdings['LTP']
my_holdings['P&L'] = (my_holdings['Qty.'] * my_holdings['LTP'] ) - ( my_holdings['Qty.'] * my_holdings['Avg. cost'])
total_invested=np.matmul(my_holdings['Qty.'], my_holdings['Avg. cost'])
my_holdings['total_invested']=my_holdings['Qty.']* my_holdings['Avg. cost']
my_holdings['P&L %'] =np.round(my_holdings['P&L']/(my_holdings['Qty.']* my_holdings['Avg. cost']) * 100,2)
my_holdings['invested %'] =np.round((my_holdings['Qty.']* my_holdings['Avg. cost'])/total_invested * 100,2)
my_holdings[['Instrument','sector','total_invested',  'Cur. val', 'P&L','P&L %','invested %']].sort_values(by='total_invested',ascending=False).reset_index(drop=True)
    # return my_holdings    

# enriched_df=enrich_holdings()
# enriched_df=enriched_df[['Instrument','sector','total_invested',  'Cur. val', 'P&L','P&L %','invested %']].sort_values(by='total_invested',ascending=False).reset_index(drop=True)
# print(my_holdings)
# enriched_df.to_csv('.\\holdings_with_features.csv',index=False)