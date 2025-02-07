import requests
import pandas as pd
import json

print("Fetching top gainers from NSE website")

# Top gainers ##
headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"}
res=requests.get(r"https://www.nseindia.com/api/live-analysis-variations?index=gainers",headers=headers)
if res.status_code==200:
    all_data=res.json()['NIFTY']['data']
    top_gainer_df=pd.DataFrame()
    def top_gainers(data):
        d=dict((k, data[k]) for k in ['symbol','open_price','high_price','low_price','ltp','perChange'] if k in data)
        return d
    for data in all_data:
        dic= top_gainers(data)
        # top_gainer_df=top_gainer_df.append(dic,ignore_index=True)
        # Convert the dictionary to a DataFrame and use concat
        dic_df = pd.DataFrame([dic])
        top_gainer_df = pd.concat([top_gainer_df, dic_df], ignore_index=True)
    top_gainer_df=top_gainer_df[['symbol','ltp','high_price', 'low_price','open_price', 'perChange']]
else:
    top_gainer_df = pd.DataFrame()


# print(top_gainer_df)  