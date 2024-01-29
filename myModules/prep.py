from bs4 import BeautifulSoup, NavigableString  # Importing necessary libraries
import pandas as pd  # Importing necessary libraries
from datetime import date  # Importing necessary libraries
from datetime import datetime  # Importing necessary libraries
from tqdm import tqdm  # Importing necessary libraries
import pickle  # Importing necessary libraries
import requests  # Importing necessary libraries
from random import randint  # Importing necessary libraries
from time import sleep  # Importing necessary libraries
import os  # Importing necessary libraries
import json  # Importing necessary libraries


os.chdir('c:/Users/Domen/IronHack/01_projects/IH_final_project_data-jobs')
print(os.getcwd())

print(os.getcwd())
with open("config/config.json", 'r') as f:
    config = json.load(f)
    
cleaned_data_path = config["cleaned_data_path"]
webscrap_data_path = config["webscrap_data_path"]    




def get_all_job_information(id, response, scrap_date):

    soup = BeautifulSoup(response.content, "html.parser")
    job_dict = {}
    job_dict['id'] = id
    try:
        job_dict['title'] = soup.find('h2', class_='top-card-layout__title').text.strip()
    except:
        job_dict['title'] = None
        
    try:    
        job_dict['company'] = soup.find("div",{"class":"top-card-layout__card"}).find("a").find("img").get('alt')
    except:
        job_dict['company'] = None
        
    try:    
        job_dict['city'] = soup.find("span",{"class":"topcard__flavor topcard__flavor--bullet"}).text.strip()
    except:
        job_dict['city'] = None
    try:
        job_dict['posting_date'] = soup.find("span", {"class":"posted-time-ago__text"}).text.strip()
    except:
        job_dict['posting_date'] = None
        
    try:    
        job_dict['job_description'] = soup.find("section",{"class":"show-more-less-html"}).text.strip()

    except:
        job_dict['job_description'] = None

    try:    
        x = get_job_information(soup)        
        job_dict['seniority_level'] = x[0]
        job_dict['employment_type'] = x[1]
        job_dict['job_function'] = x[2]
        job_dict['industries'] = x[3]
    except:
        job_dict['seniority_level'] = None
        job_dict['employment_type'] = None
        job_dict['job_function'] = None
        job_dict['industries'] = None
    
    try:    
        job_dict['scraping_date'] = scrap_date
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
    
                        

    return job_dict

def transform_scrap_data_to_df(dict):
    columns = ['id','title', 'company', 'city', 'posting_date', 'job_description', 'seniority_level', 'employment_type', 'job_function', 'industries', 'scraping_date', 'url']
    df = pd.DataFrame(columns=columns)

    for key in tqdm(dict):
        id = key
        response = dict[key]['response']
        scrap_date = dict[key]["scrap_date"]
        new_dict = get_all_job_information(id, response, scrap_date)
        
        new_row_df = pd.DataFrame([new_dict])
        df = pd.concat([df, new_row_df], ignore_index=True)

    return(df)

def get_job_information(soup):    
    class_soup = soup.find("ul", {"class":"description__job-criteria-list"}).find_all('span')
    list = []
    for x in class_soup:
        list.append(x.text.strip())
    
    return list

def second_request_empty_values(df, max_sleeptime = 2000):
    nan_df = df[df["title"].isna()]
    second_requests = nan_df['id'].tolist()
    
    request_dict = {}
    for id in tqdm(second_requests):
            response = requests.get(f'https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{id}')
            wait_time = randint(500,max_sleeptime)
            sleep(wait_time/1000)

            temp_dict = {}
            temp_dict["scrap_date"] = date.today()
            temp_dict["response"] = response
            request_dict[id] = temp_dict

    
    new_nan_df = transform_scrap_data_to_df(request_dict)
    
    temp_df = df[df["title"].notna()]
    final_df = pd.concat([temp_df, new_nan_df], ignore_index=True)
    
    return final_df

def save_cleaned_df(df, name):
    with open(f"{cleaned_data_path}{name}.pkl", "wb") as file:
        pickle.dump(df, file)
        
def null_value_cleaner(df, rounds):
    null_counter = df['title'].isna().sum()
    sleeptime = 2000
    for i in range(rounds):
        if null_counter == 0:
            print(f"Finished in round {id}")
            return df
        else:
            df = second_request_empty_values(df, max_sleeptime = sleeptime)
            null_counter = df['title'].isna().sum()
            print(f"Round{i}: {null_counter} empty values left")
            sleeptime += 500
    return df

def search_keyword(x, dict):
    for key in dict:
        if x == dict:
            y = dict[item]
            return y
        else:
            y = 'unknown'
    return y