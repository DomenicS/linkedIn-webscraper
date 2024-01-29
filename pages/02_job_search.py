import streamlit as st  
from st_pages import Page, show_pages, add_page_title  

from datetime import datetime
import json  
import pickle  
import pandas as pd  
import numpy as np  
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode  
from myModules import transformer as myBib  
import altair as alt  
import seaborn as sns  
import pandas as pd
from datetime import date  

import matplotlib.pyplot as plt  

import os  


import streamlit as st  

st.set_page_config(
    page_title='Data Job App',
    layout='wide'
    
)

add_page_title()





with open("config/config.json", 'r') as f:
    config = json.load(f)
        
templates_path = config["template_path"]
temp_data_path = config["temp_data_path"]
webscrap_data_path = config["webscrap_data_path"]   
sound_path = config["sound_path"]

input_name = "app_dataframe"

with open(f"{webscrap_data_path}{input_name}.pkl", "rb") as f:
    data = pickle.load(f)

data = myBib.skill_df(data)




    
yes_jobs = []
no_jobs = []

st.sidebar.header("Search Filter")

search_term = st.sidebar.text_input("Enter a city:")

date_filter = st.sidebar.radio(
    "Select Date Range",
    options=["Last Week", "Last 2 Weeks", "Last 3 Weeks",
        "Last Month", "Last 2 Months"]
)
filtered_df = pd.DataFrame()

data['calc_posting_date'] = pd.to_datetime(data['calc_posting_date'])
data['calc_posting_date'] = data['calc_posting_date'].apply(lambda x: x.date())

if date_filter == "Last Week":
    time_filter = date.today() - pd.Timedelta(days=7)
    st.write("time_filter")
    st.write(time_filter)
    st.write(type(time_filter))

    filtered_df = data[data["calc_posting_date"] < time_filter]
elif date_filter == "Last 2 Weeks":
    time_filter = date.today() - pd.Timedelta(days=14)
    filtered_df = data[data["calc_posting_date"] < time_filter]
elif date_filter == "Last 3 Weeks":
    time_filter = date.today() - pd.Timedelta(days=21)
    filtered_df = data[data["calc_posting_date"] < time_filter]   
elif date_filter == "Last Month":
    time_filter = date.today() - pd.Timedelta(days=30)
    filtered_df = data[data["calc_posting_date"] < time_filter]

elif date_filter == "Last 2 Months":
    time_filter = date.today() - pd.Timedelta(days=60)
    filtered_df = data[data["calc_posting_date"] < time_filter]

filtered_df = data[data["calc_posting_date"] >= time_filter]
dtype_ = data["calc_posting_date"].dtype
st.write("column")
st.write(dtype_)



if search_term:
    filtered_df = filtered_df[filtered_df['city'].str.contains(search_term, case=False, na=False)]
    filtered_df = filtered_df[filtered_df["calc_posting_date"] >= time_filter]
    yes_jobs, no_jobs = myBib.top_jobs(filtered_df, yes_jobs, no_jobs)
else:
        yes_jobs, no_jobs = myBib.top_jobs(filtered_df, yes_jobs, no_jobs)




