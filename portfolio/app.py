import streamlit as st
import utils.investement_sector_wise as sector_invst
from utils.gain_sector_wise import sector_invst_gain_df,sector_invst_gain_bar_chart
from utils.wk52_high_low import wk52_high_df,wk52_low_df
from utils.top_gainers import top_gainer_df


def display_dataframe(df):
    st.dataframe(df,use_container_width=True)

# # Define tabs
sector_tab, investment_tab,sector_gain_tab,sector_gain_per_tab, wk52_high_tab, wk52_low_tab,top_gainers_tab= \
    st.tabs(["Investement by Sector", "Stocks", "Sector P&L", "Sector P&L %","52 week high", "52 week low","Top Gainers"])
with sector_tab:
    with st.container(border=True):
        st.pyplot(sector_invst.investement_sector_wise_table_plot())


with investment_tab:
    with st.container(border=True):
        st.spinner('Loading Invested Amount...')
        display_dataframe(sector_invst.investment_df)

with sector_gain_tab:
    with st.container(border=True):
        display_dataframe(sector_invst_gain_df)

with sector_gain_per_tab:
    with st.container(border=True):
        st.pyplot(sector_invst_gain_bar_chart())


with wk52_high_tab:
    st.spinner('Loading 52 week high...')
    display_dataframe(wk52_high_df)

with wk52_low_tab:
    st.spinner('Loading 52 week low...')
    display_dataframe(wk52_low_df)


with top_gainers_tab:
     display_dataframe(top_gainer_df)


