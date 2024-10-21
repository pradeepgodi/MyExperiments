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
sector_tab, investment_tab, wk52_high_tab, wk52_low_tab= st.tabs(["Invested Sector Breakdown", "Invested Amount %", "52 week high", "52 week low"])
with sector_tab:
    # Check if the DataFrame has any numeric columns to create a pie chart
    if not mp.sector_invst_df.empty:  
        st.spinner('Loading Sector Breakdown...')
        pie_data = mp.sector_invst_df['total_invested'].value_counts().index.to_list()
        fig, ax = plt.subplots()
        ax.pie(pie_data, labels=mp.sector_invst_df['sector'], autopct='%1.1f%%', startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        st.pyplot(fig)
    else:
        st.write("Please upload a CSV file to display data.")

with investment_tab:
    with st.container(border=True):
        st.spinner('Loading Invested Amount...')
        display_dataframe(mp.investment_df)
        # st.dataframe(mp.investment_df,use_container_width=True)

with wk52_high_tab:
    st.spinner('Loading 52 week high...')
    display_dataframe(mp.wk52_high_df)
    # st.dataframe(mp.wk52_high_df,use_container_width=True)

with wk52_low_tab:
    st.spinner('Loading 52 week low...')
    display_dataframe(mp.wk52_low_df)
    # st.dataframe(mp.wk52_low_df,use_container_width=True)

# with top_gainers_tab:
#     st.header("DataFrame 4")
# st.spinner('Loading dataframe...')
#     st.dataframe(df)

