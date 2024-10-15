#importing required libraries :)
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from dotenv import load_dotenv
import os
load_dotenv()
def extract_emails_from_site(website, apiKey,sessionId):
    print(f"Finding indexed pages for: {website}")
    query = f'intext:"@gmail.com" site:{website}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    #Parameters for the API Request

    params = {
        'key' : apiKey, # Your google API Key
        'cx' : sessionId, # Your custome search engine ID
        'q' : query, # The search query 
        'num': 10   # Number of results per page
    }

    # google's search url for api
    google_search_url = f'https://www.googleapis.com/customsearch/v1?{params}    '


    print(google_search_url)
    response = requests.get(google_search_url)
   
    if response.status_code == 200:
        print("Request successful!")
        return response.json()
    else:
        print(f"Failed to fetch results. Status code: {response.status_code}")
        return None
    print("Looped")
    
# Input: Website to scrape
website = input("Enter the website (e.g., vitbhopal.ac.in): ").strip()

# Google Custom Search API Credentials 
api_key = os.getenv("Your_Google_API_KEY")
search_engine_id = os.getenv("SESSION_ID")

# Extract emails from the given website  for comparing :))
text = extract_emails_from_site(website, api_key, search_engine_id)


if text:
    print(text['items'])

