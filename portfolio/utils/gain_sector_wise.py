import pandas as pd
import numpy as np
from  utils.investement_sector_wise import sector_invst_df
from utils.get_holdings_add_features import my_holdings
import matplotlib.pyplot as plt

# investment_df=pd.read_csv(".\\holdings_with_features.csv")

print("Loading sector wise investment data")
investment_df=my_holdings
# Sector wise P&L
sector_pl_df=investment_df[['Instrument','sector', 'total_invested', 'Cur. val', 'P&L']].groupby('sector').agg({'total_invested':'sum','Cur. val':'sum','P&L':'sum','Instrument':'count'}).reset_index(drop=False)
sector_pl_df['P&L %']=np.round((sector_pl_df['P&L'] / sector_pl_df['total_invested'] ) * 100,2)
sector_pl_df=sector_pl_df.sort_values(by='P&L %',ascending=False).reset_index(drop=True)
# print(sector_pl_df.columns)

# Sector wise invested % and P&L %
sector_invst_gain_df=sector_pl_df.merge(sector_invst_df,on=['sector'], how='inner')
# print("After merge", sector_invst_gain_df.columns)
# print(sector_invst_gain_df)
sector_invst_gain_df.rename(columns={'P&L %_x':'P&L %'},inplace=True)
sector_invst_gain_df=sector_invst_gain_df[['sector', 'Instrument','P&L %', 'invested %']]

# print(sector_invst_gain_df)

# bar graph for sector wise investment and P&L %
def sector_invst_gain_bar_chart():
    # Extract data from the DataFrame
    sector_name = sector_invst_gain_df['sector'].values
    invested_percent = sector_invst_gain_df['invested %'].values
    pl_percent = sector_invst_gain_df['P&L %'].values

    # Sort by 'Invested (%)' or 'P&L (%)'
    sorted_indices = np.argsort(pl_percent)  # Sort by 'Invested (%)' (or pl_percent for P&L sorting)

    # Re-arrange data based on sorted indices
    sector_name = sector_name[sorted_indices]
    invested_percent = invested_percent[sorted_indices]
    pl_percent = pl_percent[sorted_indices]

    category = {
        'Invested (%)': invested_percent,
        'P&L (%)': pl_percent,
    }

    y = np.arange(len(sector_name)) * 2  # Multiply by 2 to increase spacing between groups
    height = 0.3  # Bar height
    multiplier = 0

    # Set the figsize to increase the chart size (width, height)
    fig, ax = plt.subplots(figsize=(12, 8), layout='constrained')  # Adjust as needed

    # Adjust spacing between bars within the same group
    spacing_factor_within = 1.5  # Increase this value to add more space between bars

    for attribute, measurement in category.items():
        offset = height * multiplier * spacing_factor_within
        # Add edgecolor to give demarcation between bars
        rects = ax.barh(y + offset, measurement, height, label=attribute, edgecolor='black')
        ax.bar_label(rects, padding=3)
        multiplier += 1

    # Add some text for labels, title, and custom y-axis tick labels
    ax.set_title('Investment and P&L by Sector (Sorted)')
    ax.set_yticks(y + height / 2 * spacing_factor_within)
    ax.set_yticklabels(sector_name)
    ax.legend(loc='center right')
    ax.set_xlim(0, pl_percent.max() * 1.1)  # Increase limit by 10%
    return plt  