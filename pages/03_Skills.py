import streamlit as st  
from st_pages import Page, show_pages, add_page_title  
import json  
import pickle  
import altair as alt  
import pandas as pd  
import numpy as np  
from myModules import transformer as myBib  

import streamlit as st  



st.set_page_config(
    page_title='Data Job App',
    layout='wide'
    
)

add_page_title()


with open("config/config.json", 'r') as f:
    config = json.load(f)
    
NLP_data_path = config['NLP_data_path']
input_name = "skills_df"

with open(f"{NLP_data_path}{input_name}.pkl", "rb") as f:
    data = pickle.load(f)


option = st.sidebar.radio(
    'Choose the number of top skills to display:',
    ('Top 10', 'Top 20', 'Top 50', 'All'),
    index=1  # Pre-set to "Top 20"
)

if option == 'Top 10':
    top_n = 10
elif option == 'Top 20':
    top_n = 20
elif option == 'Top 50':
    top_n = 50
else:
    top_n = None 


filter_list = []
job_filter_dict = { 'All':filter_list, 'Data Analyst':'data_analyst', 'Data Engineer':'data_engineer', 'Data Scientist':'data_scientist', 'Business Analyst':'business_analyst','Bi Analyst':'bi_analyst' ,
                   'Analytics Engineer':'analytics_engineer', 'Machine Learning Engineer':'ml_engineer'}
filter_list = list(job_filter_dict.keys())

job_selection = st.selectbox('Select a Job Title:', list(job_filter_dict.keys()))


if job_selection == 'All':
    filtered_df = data
    counter = len(filtered_df)
if job_selection != 'All':
    filtered_df = data[data['new_job_title'].apply(lambda x: job_filter_dict[job_selection] in x)]
    counter = len(filtered_df)

st.write(f"{counter} jobs found in dataset.")
skill_data = myBib.agg_skill_data(filtered_df, top_n) #prepare dataframe for top list

df_sorted = skill_data.sort_values('percentage', ascending=False)


chart = alt.Chart(df_sorted).mark_bar().encode(
    x='percentage',
    y=alt.X('keywords', sort=None)
).properties(
    width=1000,  # Width in pixels

)

labels = chart.mark_text(
    align='left',
    baseline='middle',
    dx=3
).encode(
    text='percentage'
)

final_chart = chart + labels 





st.altair_chart(final_chart, use_container_width=True)

