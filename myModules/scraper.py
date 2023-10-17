from bs4 import BeautifulSoup, NavigableString  
import requests  
from time import sleep  
from random import randint  
import math  
from tqdm import tqdm  
import pickle  
import pandas as pd  
from datetime import date  
from datetime import datetime  
import json  
import zlib  
import numpy as np  
import json  

import os  

os.chdir('C:/Users/Domen/OneDrive/Projects/linkedIn-webscraper')
print(os.getcwd())

print(os.getcwd())
with open("config/config.json", 'r') as f:
    config = json.load(f)
    
temp_data_path = config["temp_data_path"]
webscrap_data_path = config["webscrap_data_path"]    

def import_keyword_list():  # Importing necessary libraries
    with open("keyword_list.csv", "r") as file:
        keywords = pd.read_csv(file, delimiter = ";")
    keywords["Keywords"] = keywords["Keywords"].str.replace(" ", "%20") # replace all spaces with %20 for thr URL
    keyword_list = keywords['Keywords'].tolist() # creating a list
    return keyword_list

def initialize_empty_df():
    columns = ['id','title', 'company', 'city', 'posting_date', 'job_description', 'seniority_level', 'job_function', 'industries', 'scraping_date', 'url', 'keyword']
    scraper_df = pd.DataFrame(columns=columns)
    return scraper_df

def get_job_information(soup):    
    class_soup = soup.find("ul", {"class":"description__job-criteria-list"}).find_all('span')
    list = []
    for x in class_soup:
        list.append(x.text.strip())
    
    return list

def get_job_description(soup):
    counter = 1
    description_list = []
    qualification_list = []
    information_list = []
    
    class_soup = soup.find("div", {"class":"description__text"}).find_all('ul')
    for x in class_soup:
        list_items = x.find_all('li')
        list = []
        for item in list_items:
            list.append(item.text.strip())
            
        if counter == 1:
            description_list = list
        if counter == 2: 
            qualification_list = list       
        if counter == 3: 
            information_list = list 
        counter += 1 
    
    return description_list, qualification_list, information_list

def get_all_job_information(id, id_control):

    response = requests.get(f'https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{id}')
    soup = BeautifulSoup(response.content, "html.parser")
    job_dict = {}
    job_dict['id'] = id
    try:
        job_dict['title'] = soup.find('h2', class_='top-card-layout__title').text.strip()
    except:
        job_dict['title'] = None
        print("Error: in 'title'")
        
    try:    
        job_dict['company'] = soup.find("div",{"class":"top-card-layout__card"}).find("a").find("img").get('alt')
    except:
        job_dict['company'] = None
        print("Error: in 'company'")
        
    try:    
        job_dict['city'] = soup.find("span",{"class":"topcard__flavor topcard__flavor--bullet"}).text.strip()
    except:
        job_dict['city'] = None
        print("Error: in 'city'")
    try:
        job_dict['posting_date'] = soup.find("span", {"class":"posted-time-ago__text"}).text.strip()
    except:
        job_dict['posting_date'] = None
        print("Error: in 'posting date'")
        
    try:    
        job_dict['job_description'] = soup.find("section",{"class":"show-more-less-html"}).text.strip()

    except:
        job_dict['job_description'] = None
        print("Error: in 'job description'")
        

    try:    
        x = get_job_information(soup)        
        job_dict['seniority_level'] = x[0]
        job_dict['job_function'] = x[1]
        job_dict['industries'] = x[3]
    except:
        print(f"Error: get job information in id {id}")
        job_dict['seniority_level'] = None
        job_dict['job_function'] = None
        job_dict['industries'] = None
    
    try:    
        job_dict['scraping_date'] = date.today()
    except:
        job_dict['scraping_date'] = None 
    
    try:
        name = job_dict['title']
        name = name.replace(" ", "%20")
        company = job_dict['company']
        company = company.replace(" ", "%20")
        job_dict['url'] = f"https://www.linkedin.com/jobs/search?keywords={name}%20{company}&location=Berlin%2C%20Berlin%2C%20Germany&geoId=&trk=public_jobs_jobs-search-bar_search-submit&position=1&pageNum=0"
    except:
        job_dict['url'] = None 
    
                        
    try: 
        id_control.append(id)
    except Exception as e:
        raise ValueError(f"Error occurred: {e}")
    return job_dict, id_control, response

def create_backend_links(link, number_of_results, key_name):
    
    
    
    number_of_loops = math.ceil(number_of_results/25)
    start = 0
    
    print(f"Start creating backend links for {key_name}. Total of found pages: {number_of_loops}\n")
    
    link_key = link.replace("pageNum=0","")
    link_key = link_key.split('jobs/')[1]

    
    backend_call_array = pd.array([])
    
    for i in range(number_of_loops):
        
        backend_call = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/{link_key}start={start}"
        backend_call_array = np.append(backend_call_array, backend_call)
        start += 25
        
    return backend_call_array 

def save_df_as_json_with_time_stamp(df):   
    current_date = datetime.now()
    time = current_date.strftime("%Y-%m-%d_%H-%M-%S")
    time
    
    scraper_df_json = scraper_df.to_json('dataframe.json', orient='split', date_format='iso', indent=4)

    with open(f'{webscrap_data_path}{str(time)}.json', 'wb') as file:
        json.dump(scraper_df_json, file=file)
        
def get_id_list(list):
    
    counter = 0
    id_array = pd.array([])
    for item in tqdm(list):
        response = requests.get(item)
        soup = BeautifulSoup(response.content, "html.parser")
        
        alljobs_on_this_page=soup.find_all("li")
        len(alljobs_on_this_page)
        for x in range(0,len(alljobs_on_this_page)):
            job_div = alljobs_on_this_page[x].find("div", {"class": "base-card"})
            if job_div:
                jobid = job_div.get('data-entity-urn')
                if jobid:
                    jobid = jobid.split(":")[3]
                    id_array = np.append(id_array, jobid)
                else:
                    print("data-entity-urn attribute not found for this job.")
        
    counter +=1
    return id_array

def test():
    print('test')


def export_data(soup_dict, keyword_dict, soup_file_name = 'soup_dictV2', keyword_file_name = 'keyword_dictV2'):
    try:

        
        with open(f"{webscrap_data_path}{soup_file_name}.pkl", "wb") as file:
            pickle.dump(soup_dict, file=file)

        with open(f"{webscrap_data_path}{keyword_file_name}.pkl", "wb") as file:
            pickle.dump(keyword_dict, file)
            

    except Exception as e:
        raise ValueError(f"Error occurred: {e}")    
    return 