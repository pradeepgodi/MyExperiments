import matplotlib.pyplot as plt
import pandas as pd
from utils.get_holdings_add_features import my_holdings

print("Loading investment data")
# investment_df=pd.read_csv(".\\holdings_with_features.csv")
# investment_df=enrich_holdings()
investment_df=my_holdings
sector_invst_df=investment_df.groupby('sector').sum('total_invested').sort_values(by=['invested %'],ascending=False).reset_index(drop=False)

def investement_sector_wise_table_plot():
    # Sort the dataframe by 'invested %'
    sector_invst_df_sorted = sector_invst_df.sort_values(by='invested %', ascending=True)
    # Extract the sorted sector names and invested values
    sector_names = sector_invst_df_sorted['sector']
    invested_values = sector_invst_df_sorted['invested %']
    # Create the figure and axis
    fig, ax = plt.subplots()
    # Create a horizontal bar plot
    bar_container = ax.barh(sector_names, invested_values, height=0.6)  # Reduce height for spacing
    # Add labels to the bars
    # ax.bar_label(bar_container, fmt=lambda x: f'{x * 1:.1f} %', padding=3)  # Add padding for better readability
    ax.bar_label(bar_container)  # Add padding for better readability
    # Set the x-axis label
    ax.set_xlabel('%')
    ax.set_xlim(0, invested_values.max() * 1.1)  # Increase limit by 10%
    return plt