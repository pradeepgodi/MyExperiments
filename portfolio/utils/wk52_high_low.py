from utils.get_holdings_add_features import my_holdings,high_52w_list,high_52w_list,low_52w_list

print("Getting 52w high and low")

# Stocks that are above 52 Week High
## "Above 52w" Coloumn , +ve numbers mean that stock is above is 52w high and sellable
my_holdings.insert(len(my_holdings.columns),"High 52w price",high_52w_list)
my_holdings.insert(len(my_holdings.columns),"Low 52w price",low_52w_list)
my_holdings['Above 52w']= my_holdings['LTP']- my_holdings['High 52w price']
yesno=["YES" if v>0 else "NO" for v in list(my_holdings['Above 52w']) ]
my_holdings.insert(len(my_holdings.columns),"Any Above 52w",yesno)
# wk52_high_df=my_holdings[my_holdings['P&L']>0][['Instrument','sector', 'Qty.','P&L', 'LTP', 'High 52w price', 'Above 52w','Any Above 52w']].sort_values(by='Above 52w',ascending=False)
wk52_high_df=my_holdings[my_holdings['P&L']>0][['Instrument','Qty.','P&L', 'LTP', 'High 52w price', 'Above 52w','Any Above 52w']].sort_values(by='Above 52w',ascending=False)
wk52_high_df.reset_index(drop=True,inplace=True)    
# print(wk52_high_df)


# Stocks that are Below 52 Week Low , to check if the stocks that have gone really bad
## "Below 52w" column -ve number means stock is below its 52w low and in bad state
my_holdings['Below 52w']=   my_holdings['LTP'] - my_holdings['Low 52w price']
yesno1=["YES" if v<0 else "NO" for v in list(my_holdings['Below 52w']) ]
my_holdings.insert(len(my_holdings.columns),"Any Below 52w",yesno1)
wk52_low_df=my_holdings[['Instrument','Qty.','P&L', 'LTP', 'Low 52w price', 'Below 52w','Any Below 52w']].sort_values(by='Below 52w',ascending=True)
wk52_low_df.reset_index(drop=True,inplace=True)
# print(wk52_low_df)