import streamlit as st
import json

with open("config/config.json", 'r') as f:
    config = json.load(f)
    
templates_path = config["template_path"]


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
    settings["keywords"] = url_dict 
    # Export URLs to a JSON file 
    try: 
        with open(f"{templates_path}/{settings_name}.json", "w") as f:
            json.dump(settings, f)
        st.write("URLs exported to search_settings.json")

    except Exception as e:
        raise ValueError(f"Error occurred: {e}.")