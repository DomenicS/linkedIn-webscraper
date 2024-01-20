import streamlit as st
import json
import os
import pickle
from datetime import date
from bs4 import BeautifulSoup, NavigableString  
import requests  
from myModules import scraper_v2 as mybib # importing own library
from time import sleep
from random import randint

with open("config/config.json", 'r') as f:
    config = json.load(f)
        
templates_path = config["template_path"]
temp_data_path = config["temp_data_path"]
webscrap_data_path = config["webscrap_data_path"]   
sound_path = config["sound_path"]


# Sidebar navigation
page = st.sidebar.selectbox("Choose a page", ["Save Scrap Settings", "Load Saved Settings"])


if page == "Save Scrap Settings":
    # Initialize variables
    keywords = {'Data Analyst': 'data%20analyst',
                'Data Scientist' : 'data%20scientist',
                'Data Engineer' : 'data%20engineer',
                'Business Analyst' : 'Business%20analyst'}


    TPR_values = {
        '24h': 'r86400',
        'Last week': 'r604800',
        'Last month': 'r2592000',
        'All time': ''
    }

    E_value = '2%2C3%2C4'

    location_values = {
        'Berlin': {'location': 'Berlin%2C%20Berlin%2C%20Germany', 'geoID': '106967730'}
    }

    # Create Streamlit widgets
    st.title("LinkedIn Job Scrap Settings")

    settings_name = st.text_input("Search Settings Name")
    selected_keywords = st.multiselect("Select Keywords", list(keywords.keys()))
    selected_TPR = st.selectbox('Select Timeframe for Search', list(TPR_values.keys()))
    selected_location = st.selectbox('Select Location', list(location_values.keys()))
    settings = {}

    if st.button('Save Scrap Settings'):
        # Construct the LinkedIn URL
        base_url = "https://www.linkedin.com/jobs/search?"
        TPR_query = f"_TPR={TPR_values[selected_TPR]}"
        E_query = f"f_E={E_value}"
        location_query = f"location={location_values[selected_location]['location']}&geoId={location_values[selected_location]['geoID']}&locationId="
        other_params = "distance=25&position=1&pageNum=0"
        url_dict = {}

        for key in selected_keywords:
            keyword_value = keywords[key]  # Fetch the value from the dictionary
            key_query = f"keywords={keyword_value}"
            final_url = f"{base_url}{key_query}&{location_query}&{TPR_query}&{E_query}&{other_params}"
            url_dict[keyword_value] = final_url
            # Display the final URL
            st.write(f"Generated LinkedIn Search URL for {key}:")
            st.write(final_url)
            
        settings["tpr"] = TPR_query
        settings["E"] = E_query
        settings["location"] = location_query
        st.write(url_dict)
        settings["keywords"] = url_dict 
        st.write(settings)
        # Export URLs to a JSON file 
        try: 
            with open(f"{templates_path}/{settings_name}.json", "w") as f:
                json.dump(settings, f, indent=4)
            st.write("URLs exported to search_settings.json")

        except Exception as e:
            raise ValueError(f"Error occurred: {e}.")
        
elif page == "Load Saved Settings":
    # Code for "Load Saved Settings"
    st.title("Load Saved LinkedIn Job Scrap Settings")
    
    # List saved settings files
    files = [f.split('.')[0] for f in os.listdir(templates_path) if f.endswith('.json')]
    
    # Select a settings file to load
    selected_file = st.selectbox("Select a settings file", files)
    
    # Load and display settings from the selected file
    try:
        with open(f"{templates_path}/{selected_file}.json", "r") as f:
            saved_settings = json.load(f)
            st.write(saved_settings)


    except Exception as e:
        st.write(f"An error occurred: {e}")
        
    if st.button('Start Scrap'):      

        soup_file =  'soup_dict'      
        try:
            with open(f"{webscrap_data_path}id_tracker.pkl", "rb") as file:
                id_tracker = pickle.load(file)
                

        except Exception as e:
            st.write(f"An error occurred: {e}")
             
        # progress_bar = st.progress(0)  
        # total_items = len(saved_settings["keywords"])
        
        for key, value in saved_settings["keywords"].items():
            
            st.write(f"Start scraping Process for keyword: {key} using {value}.")
            
            key_name = key.replace('%20', "_")
                
            response = requests.get(value) # first request for keyword
            response.status_code # 200 status code means OK!
            soup = BeautifulSoup(response.content, "html.parser")
            
            number_of_results = soup.find('span', class_="results-context-header__job-count").text # check number of searching results
            numb = int(number_of_results.replace(",", "").replace("+", ""))
            st.write(f"Number of results: {number_of_results} and Number of Loops: {numb}")

            backend_call_url_list = []
            backend_call_url_list = mybib.create_backend_links(value, numb, key_name) # create list with sublinks to select different pages 
            
            
            
            id_array = mybib.get_id_list(backend_call_url_list) # get job id's from all pages
            
            st.write(f"{len(id_array)} ID's found")
            
            backup_interval = 50
 
            progress_bar = st.progress(0)
            total_items = len(id_array)
            progress_text = st.empty()
            
            temp_scrap = {}
            temp_id = {}
            
            
            for i, id in enumerate(id_array):
                if (i + 1) % backup_interval == 0 or i == total_items - 1:
                    try:
                        
                        current_date = date.today()
                        timestamp = current_date.strftime("%Y%m%d")
                        filename = f"{soup_file}-{timestamp}"
                        scrap = {}
                        
                        if os.path.exists(f"{webscrap_data_path}{filename}.pkl"):
                            st.write(f"Update {webscrap_data_path}{filename}.pkl")
                            with open(f"{webscrap_data_path}{filename}.pkl", "rb") as file:
                                scrap = pickle.load(file)
                            scrap.update(temp_scrap)
                            with open(f"{webscrap_data_path}{filename}.pkl", "wb") as file:
                                pickle.dump(scrap, file)
                        else:
                            st.write(f"Create {webscrap_data_path}{filename}.pkl")
                            scrap.update(temp_scrap)
                            with open(f"{webscrap_data_path}{filename}.pkl", "wb") as file:
                                pickle.dump(scrap, file)


                        with open(f"{webscrap_data_path}id_tracker.pkl", "rb") as file:
                            id_tracker = pickle.load(file)
                        id_tracker.update(temp_id)
                        with open(f"{webscrap_data_path}id_tracker.pkl", "wb") as file:
                                pickle.dump(id_tracker, file)
                                
                        temp_scrap = {}
                        temp_id = {}
                    
                        print(f"Backup performed after processing {i + 1} items") 
                        
                    except Exception as e:
                        st.write(f"An error occurred: {e}")    
                
                
                if str(id) not in id_tracker:
                    response = requests.get(f'https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{id}')
                    wait_time = randint(1,200)
                    sleep(wait_time/1000)
                    
                    temp2 = {}
                    temp2["scrap_date"] = date.today()
                    temp2["response"] = response
                    temp_scrap[id] = temp2
                    
                    temp_id[id] = date.today()
                        
                    progress = (i + 1) / total_items
                    progress_bar.progress(progress)
                    progress_text.text(f"Processing {i + 1} of {total_items} ID's...")
                else:
                    progress = (i + 1) / total_items
                    progress_bar.progress(progress)
                    progress_text.text(f"Will skip {id} because is already in the dataset. Processing {i + 1} of {total_items} ID's...")

            try:
                scrap.update(temp_scrap)
                id_tracker.update(temp_id)
                
                temp_scrap = {}
                temp_id = {}
            
                print(f"Backup performed after processing {i + 1} items") 
            
            except Exception as e:
                st.write(f"An error occurred: {e}") 
    
