from tqdm import tqdm  
import pandas as pd  
from langdetect import detect  
import nltk  
from nltk.stem import WordNetLemmatizer  

from sklearn.feature_extraction.text import CountVectorizer  
from nltk.tokenize import word_tokenize  
from nltk.stem import WordNetLemmatizer  
import re  
import pandas as pd  
import nltk  
from nltk.stem import WordNetLemmatizer  
from sklearn.feature_extraction.text import CountVectorizer  
from nltk.tokenize import word_tokenize  
from nltk.corpus import wordnet  
from nltk.corpus import stopwords  


import collections  
import numpy as np  
import pandas as pd  
import matplotlib.cm as cm  
import matplotlib.pyplot as plt  
from matplotlib import rcParams  
from wordcloud import WordCloud, STOPWORDS  

import spacy  

from datetime import datetime, timedelta  
from datetime import datetime  


nlp = spacy.load("de_core_news_sm")

def check_language(x):
    try:
        return detect(x)
    except:
        return 'unknown'

def add_language_values_to_df(df, search_column, new_column = 'language'):
    df[search_column].fillna("", inplace=True)

    tqdm.pandas(desc="Processing")
    df[new_column] = df[search_column].progress_apply(check_language)
    return df

def title_pre_processing(x):
    return x


def clean_up(s):
    pattern_to_remove = r'\([a-z]/[a-z]/[a-z]\)'
    s = re.sub(pattern_to_remove, '', s)
    s = re.sub('all genders', '', s)
    s = re.sub(r'(?<=\w)\.', ' . ', s)
    s = re.sub('--', ' ', s)
    s = re.sub('––', ' ', s)
    s = re.sub('–', ' ', s)
    s = re.sub('&', ' ', s)



    return s.lower().strip()

def tokenize(s):
    tokens = word_tokenize(s)
    return tokens

nlp = spacy.load("de_core_news_sm")

def get_wordnet_pos(word, language):
    tag_dict = {"J": wordnet.ADJ, 
            "N": wordnet.NOUN,
            "V": wordnet.VERB,
            "R": wordnet.ADV}
    tag = nltk.pos_tag([word], lang=language)[0][1][0].upper()
    return tag_dict.get(tag, wordnet.NOUN)

def stem_and_lemmatize_english(l):
    lemmatizer = WordNetLemmatizer()
    lemmatized = [lemmatizer.lemmatize(word, get_wordnet_pos(word, 'eng')) for word in l]
    return lemmatized 

def stem_and_lemmatize_german(l):
    
    text = nlp(l)
    
    lemmatized_tokens  = [token.lemma_ for token in text]
    lemmatized_text = " ".join(lemmatized_tokens)
    return lemmatized_text 


def remove_stopwords_englisch(l, language = 'english'):

    text_no_sw = [word for word in l if not word in stopwords.words(language)]
    return text_no_sw

def remove_stopwords_german(l, language = 'german'):

    text_no_sw = [word for word in l if not word in stopwords.words(language)]
    return text_no_sw

def re_blob(x):
    return " ".join(x)


def drop_words(s):
    
    droplist = ['campus', 'online', 'remote', 'berlin', 'hamburg', 'frankfurt', 'duales', 'mitarbeiter', 
                'home office', 'teilzeit', 'vollzeit', 'w d', 'home', 'office']

    
    for word in droplist:
        if word in s:
            s = re.sub(word, '', s)
    return s


def extract_keywords(row):
    
    s = row['cp2_title']
    
    keywords = ['data_analyst', 'analytics_engineer','software-architect', 'ml_engineer', 'it_systemadmin', 'software_developer','scientist_','research_scientist', 'data_architect','java_software_engineer','data_engineer', 'database_datawarehouse', 'business_analyst', 'product_analyst', 
                'business_intelligence_analyst', 'full_stack', 'database_administrator', 'fp&a_analyst', 'product_analyst'
                'programm_manager', 'data_analytics', 'big_data_engineer/specialist', 'sap_specialist', 'devops_engineer', 'backend_developer', 'data_management'
               'software_engineer', 'analysis_engineer', 'data_scientist', 'machine_learning_engineer', 'ai_engineer', 'controlling_', 'it_systemadmin'
               'cloud_engineer', 'deep_learning', 'reporting_analyst', 'test_engineer', 'system_engineer', 'specialist', 'sap_specialist']
    
    regex_pattern = r'\b(?:' + '|'.join(re.escape(keyword) for keyword in keywords) + r')\b'
    
    matched_keywords = re.findall(regex_pattern, s, re.IGNORECASE)

    if matched_keywords:
        row['new_job_title'] = matched_keywords
        


    return row



def extract_level(row):
    student_list = ['werkstudent', 'praktikum','student', 'studium', 'wissenschaftlich', 'pflichtpraktikum', 'intern', 'masterarbeit', 'ausbildung'
                    'bachelorarbeit']
    junior_list = ['junior', 'young professional']
    senior_list = ['senior', 'lead']
    manager_list = ['manager', 'head of', 'head ']
    consultant_list = ['consultant']
    
    s = row['cp1_title']
    
    for word in student_list:
        if word in s.lower():
            row['job_level'] = 'student_level'
            s = re.sub(word, "", s)
            
    for word in junior_list:
        if word in s.lower():
            row['job_level'] = 'junior_level'
            s = re.sub(word, "", s)
    
    for word in consultant_list:
        if word in s.lower():
            row['job_level'] = 'consultant'
            s = re.sub(word, "", s)
            
    for word in senior_list:
        if word in s.lower():
            row['job_level'] = 'senior_level'
            s = re.sub(word, "", s)
            
    for word in manager_list:
        if word in s.lower():
            row['job_level'] = 'manager_level'
            s = re.sub(word, "", s)
            
    row['cp2_title'] = s
    return row
        



def word_cloud(df, column):
    title_list = df[column].tolist()

    bag = []
    bag = " ".join(title_list)
    bag

    stopwords = STOPWORDS
    wordcloud = WordCloud(stopwords=stopwords, background_color="white", max_words=1000).generate(bag)
    rcParams['figure.figsize'] = 10, 20
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.show()
    filtered_words = [word for word in bag.split() if word not in stopwords]
    counted_words = collections.Counter(filtered_words)
    words = []
    counts = []
    for letter, count in counted_words.most_common(10):
        words.append(letter)
        counts.append(count)
    colors = cm.rainbow(np.linspace(0, 1, 10))
    rcParams['figure.figsize'] = 20, 10
    plt.title('Top words in the headlines vs their count')
    plt.xlabel('Count')
    plt.ylabel('Words')
    plt.barh(words, counts, color=colors)
    plt.show()
    
    
    
def get_job_title(row):
    s = row['cp1_title']
    
    s = re.sub('data analyst', ' data_analyst ', s)  
    s = re.sub('datenanalyst', ' data_analyst ', s) 
    
    s = re.sub('operations analyst', ' operations_analyst ', s) 
    s = re.sub('operation analyst', ' operations_analyst ', s) 
    
    s = re.sub('data engineer', ' data_engineer ', s)
    s = re.sub('business analyst', ' business_analyst ', s)
    s = re.sub('business-analyst', ' business_analyst ', s)
    s = re.sub('business-analyst', ' business_analyst ', s)
    s = re.sub('businessanalyst', ' business_analyst ', s)
    
    s = re.sub('busines process analyst', ' business_process_analyst ', s)
    
    s = re.sub('product analyst', ' product_analyst ', s)
    
    s = re.sub('business intelligence analyst', ' bi_analyst ', s)
    s = re.sub('business intelligence', ' bi_analyst ', s)
    s = re.sub('bi analyst', ' bi_analyst ', s)
    s = re.sub('bi engineer', ' bi_engineer ', s)
    
    s = re.sub('programm manager', ' programm_manager ', s)
    s = re.sub('software engineer', ' software_engineer ', s)
    s = re.sub('software developer', ' software_developer ', s)
    s = re.sub('software entwickler', ' software_developer ', s)
    s = re.sub('softwareentwickler', ' software_developer ', s)
    s = re.sub('developer ', ' software_developer ', s)
    
    s = re.sub('software architect', ' software_architect ', s)
    s = re.sub('software-architect', ' software_architect ', s)
    s = re.sub('software-architect', ' software_architect ', s)
    
    s = re.sub('system engineer', ' system_engineer ', s)
    s = re.sub('analysis engineer', ' analysis_engineer ', s)
    
    s = re.sub('analytics engineer', ' analytics_engineer ', s)
    
    s = re.sub('data science', ' data_scientist ', s)
    s = re.sub('data scientist', ' data_scientist ', s)
    
    
    s = re.sub('machine learn engineer', ' ml_engineer ', s)
    s = re.sub('machine learn', ' ml_engineer ', s)
    s = re.sub('machine_learn', ' ml_engineer ', s)
    s = re.sub('ml ', ' ml_engineer ', s)
    
    s = re.sub('ai ', ' ai_engineer ', s)
    s = re.sub('artificial intelligence', ' ai_engineer ', s)
    
    s = re.sub('cloud', ' cloud_engineer ', s)
    s = re.sub('cloud_engineer', ' cloud_engineer ', s)
    
    
    s = re.sub('devops engineer ', ' devops_engineer ', s)
    s = re.sub('devops engin', ' devops_engineer ', s)
    s = re.sub('devop engin', ' devops_engineer ', s)
    
    
    s = re.sub('devolop engin ', ' develop_engineer ', s)
    s = re.sub('devolop_engineer', ' develop_engineer ', s)
    s = re.sub('entwicklungsingenieur', ' develop_engineer ', s)
    
    s = re.sub('fp & a', ' fp&a_analyst ', s)
    
    s = re.sub('deep learn', ' deep_learning ', s)
    s = re.sub('reporting analyst', ' reporting_analyst ', s)
    
    s = re.sub('sap ', ' sap_specialist ', s)

    s = re.sub('data analytics', ' data_analytics ', s)
    
    s = re.sub('control', ' controlling_ ', s)

    s = re.sub('test engineer', ' test_engineer ', s)
    s = re.sub('test engin', ' test_engineer ', s)
    
    s = re.sub('big data', ' big_data_engineer/specialist ', s)
    s = re.sub('big data', ' big_data_engineer/specialist ', s)
    
    s = re.sub('staff engineer', ' staff_engineer ', s)
    
    s = re.sub('java', ' java_software_engineer ', s)
    s = re.sub('java-', ' java_software_engineer ', s)
    s = re.sub('java ', ' java_software_engineer ', s)
    
    s = re.sub('backend ', ' backend_developer ', s)
    
    s = re.sub('it ', ' it_systemadmin ', s)
    s = re.sub('systemadministrator', ' it_systemadmin ', s)
    
    
    s = re.sub('data manag ', ' data_management ', s)
    
    s = re.sub('full stack ', ' full_stack ', s)
    s = re.sub('full-stack ', ' full_stack ', s)
    s = re.sub('fullstack ', ' full_stack ', s)
    
    s = re.sub('database administr ', ' database_datawarehouse ', s)
    s = re.sub('datenbankadministr ', ' database_datawarehouse ', s)
    s = re.sub('datenbank-administr ', ' database_datawarehouse ', s)
    s = re.sub('datenbank-administr ', ' database_datawarehouse ', s)
    s = re.sub('datenbank-administr ', ' database_datawarehouse ', s)
    s = re.sub('data warehous', ' database_datawarehouse ', s)
    
    
    s = re.sub('research scientist ', ' research_scientist ', s)
    s = re.sub(' scientist ', ' scientist_ ', s)
    
    s = re.sub('data architect', 'data_architect', s)
    
    
    keywords = ['data_analyst', 'analytics_engineer','bi_analyst','software_architect', 'ml_engineer', 'it_systemadmin', 'software_developer','scientist_','research_scientist', 'data_architect','java_software_engineer','data_engineer', 'database_datawarehouse', 'business_analyst', 'product_analyst', 
            'business_intelligence_analyst', 'full_stack', 'database_administrator', 'fp&a_analyst', 'product_analyst',
            'programm_manager', 'data_analytics', 'big_data_engineer/specialist', 'sap_specialist', 'devops_engineer', 'backend_developer', 'data_management',
            'software_engineer', 'analysis_engineer', 'data_scientist', 'machine_learning_engineer', 'ai_engineer', 'controlling_', 'it_systemadmin',
            'cloud_engineer', 'deep_learning', 'reporting_analyst', 'test_engineer', 'system_engineer', 'specialist', 'sap_specialist']

    regex_pattern = '|'.join(re.escape(keyword) for keyword in keywords)
    
    matched_keywords = re.findall(regex_pattern, s, re.IGNORECASE)

    if matched_keywords:
        row['new_job_title'] = matched_keywords
        row['first_match'] = True
        
    row['cp1_title'] = s

    return row
    

    
def second_round_jobtitle(row):
    s = row['cp1_title']        
    matched_keywords = re.findall(r'analyst', s, re.IGNORECASE)
    if matched_keywords:
        row['new_job_title'] = matched_keywords
        row['first_match'] = True
        
    return row

def false_col(row):

    row['first_match'] = 'False'
    return row
    
    
def check_pattern_in_string(s, keywords):
    regex_pattern = '|'.join(re.escape(keyword) for keyword in keywords)
    matched_keywords = re.findall(regex_pattern, s, re.IGNORECASE)
    return matched_keywords


def check_skills(row, keywords, check_column = "job_description", skill_column = "skills"):
    s = row[check_column]
    matched_keywords = check_pattern_in_string(s, keywords)
    
    if matched_keywords:
        row[skill_column] = matched_keywords

    return row

def check_german_style(row):

    s = row["job_description"]
    
    informal_keywords = ['du', 'deine']
    
    is_informal = any(keyword in s for keyword in informal_keywords)
    
    if is_informal:
        row["language"] = 'ger+'
        
    return s

def prepare_dataset(data):
    data = data.apply(time_to_weeks, axis=1) # add transform posting date to date format
    data.fillna("", inplace=True)
    data['skills'] = data['skills'].apply(remove_duplicates_and_lower) # lower
    return data 


def time_to_weeks(row):
    scrap_date = row['scraping_date']
    posting_date = row['posting_date']    
    

    if 'minute' in posting_date or 'hour' in posting_date or 'Just now' in posting_date:
        new_date = scrap_date
    if 'day' in posting_date:
        days = int(posting_date.split(' ')[0])
        new_date = scrap_date - timedelta(days=days)
    if 'week' in posting_date:
        weeks = int(posting_date.split(' ')[0])
        new_date = scrap_date - timedelta(weeks=weeks)
    if 'month' in posting_date:
        months = int(posting_date.split(' ')[0])
        new_date = pd.to_datetime(scrap_date) - pd.DateOffset(months=months)
    if 'year' in posting_date:
        years = int(posting_date.split(' ')[0])
        new_date = pd.to_datetime(scrap_date) - pd.DateOffset(years=years)
    
    
    if isinstance(new_date, datetime):    
        row['calc_posting_date'] = new_date.date()
    else:
        row['calc_posting_date'] = new_date
        
        
    return row


def remove_duplicates_and_lower(skill_list):
    return list(set([skill.lower() for skill in skill_list]))