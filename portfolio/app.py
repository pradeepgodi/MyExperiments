import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import myportfolio as mp


    

# with st.sidebar.container(border=True):
#     # st.title("Upload your file")
#     uploaded_file = st.file_uploader("Upload a new Holdings CSV file", type=["csv"],help="Upload a new holddings csv file if available,ignore if already provided.")

# if uploaded_file is not None:
#     # Load the uploaded CSV file into a DataFrame
# df = pd.read_csv(uploaded_file)

# df = pd.DataFrame()

def display_dataframe(df):
    st.dataframe(df,use_container_width=True)

# Define tabs
sector_tab, investment_tab,sector_gain_tab,sector_gain_per_tab, wk52_high_tab, wk52_low_tab= st.tabs(["Investement by Sector", "Stocks", "Sector P&L", "Sector P&L %","52 week high", "52 week low"])
with sector_tab:
    with st.container(border=True):
        st.pyplot(mp.sector_invst_table())

with investment_tab:
    with st.container(border=True):
        st.spinner('Loading Invested Amount...')
        display_dataframe(mp.investment_df)

with sector_gain_tab:
    with st.container(border=True):
        display_dataframe(mp.sector_invst_gain_df)

with sector_gain_per_tab:
    with st.container(border=True):
        st.pyplot(mp.sector_invst_gain_bar_chart())

with wk52_high_tab:
    st.spinner('Loading 52 week high...')
    display_dataframe(mp.wk52_high_df)

with wk52_low_tab:
    st.spinner('Loading 52 week low...')
    display_dataframe(mp.wk52_low_df)
    # st.dataframe(mp.wk52_low_df,use_container_width=True)

# with top_gainers_tab:
#     st.header("DataFrame 4")
# st.spinner('Loading dataframe...')
#     st.dataframe(df)

