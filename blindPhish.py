import requests
from bs4 import BeautifulSoup
import re
import time
import os
from dotenv import load_dotenv
import pandas as pd
import requests
from urllib.parse import urljoin
import csv
import sys
sys.path.append("D:\\Code\\SecurityCodes\\LocalScraper\\modules")
from banner_bash import banner_bash


# Load environment variables (for API key and Search Engine ID)
load_dotenv()

def crawl(seed_url, max_urls=100):
    # To avoid visiting the same URL again
    visited = set()
    # Queue for URLs to be crawled
    queue = [seed_url]
    # List to store crawled URLs
    urls = []

    while queue and len(urls) < max_urls:
        url = queue.pop(0)  # Get the next URL to crawl
        if url in visited:
            continue

        print(f"Crawling: {url}")
        try:
            # Fetch the content of the page
            response = requests.get(url)
            visited.add(url)  # Mark URL as visited
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract and normalize all <a> tag href links
            for link in soup.find_all('a', href=True):
                full_url = urljoin(url, link['href'])
                # Add URL to queue if not already visited
                if full_url not in visited and full_url not in queue:
                    queue.append(full_url)
                    urls.append(full_url)


                    if len(urls) >= max_urls:
                        break

        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")

        # Optional: Sleep to avoid being blocked by servers for rapid requests
        time.sleep(1)

    return urls


# Function to fetch email addresses from a given URL
def fetch_emails_from_url(url):
    try:
        # Fetch the content of the web page
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all text content on the page
        text = soup.get_text()

        # Regular expression pattern to extract emails
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

        # Find all matching email addresses
        emails = re.findall(email_pattern, text)

        # Remove duplicates by converting the list to a set and back to a list
        unique_emails = list(set(emails))
        for email in unique_emails:
            print(email)
        return unique_emails

    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return []

# Function to fetch emails using Google Custom Search API
def extract_emails_from_site(website, apiKey, sessionId):
    """
    Uses Google Custom Search API to find indexed pages of the website and extract email addresses.

    Parameters:
        website (str): The domain name to search for.
        apiKey (str): The Google API Key.
        sessionId (str): The custom search engine ID.

    Returns:
        dict: JSON response from the Google API with search results.
    """
    
    # print(f"Finding indexed pages for: {website}")
    query = f'intext:"@{website}" site:{website}'
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    params = {
        'key': apiKey,
        'cx': sessionId,
        'q': query,
        'num': 10
    }

    google_search_url = 'https://www.googleapis.com/customsearch/v1'
    response = requests.get(google_search_url, params=params)

    if response.status_code == 200:
        print("Request successful!")
        return response.json()
    else:
        print(f"Failed to fetch results. Status code: {response.status_code}")
        return None

# Function to process the extracted emails
def process_extracted_emails(text, website):
    """
    Processes the emails found from the Google API search results.

    Parameters:
        text (dict): The search result JSON containing snippets.
        website (str): The domain name to search for.

    Returns:
        list: A list of unique email addresses.
    """
    all_emails = []

    if 'items' in text:
        for item in text['items']:
            snippet = item.get('snippet', '')
            print(f"Snippet: {snippet}")
            
            # Regex pattern to find emails
            pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            found_emails = re.findall(pattern, snippet)

            all_emails.extend(found_emails)
    else:
        print("No results found.")

    return list(set(all_emails))  # Return unique emails

# Main script
# if __name__ == "__main__":
#     str = banner_bash("BlindScraper")
#     print(str)
#     # API credentials from .env file
#     api_key = os.getenv("Your_Google_API_KEY")
#     search_engine_id = os.getenv("SESSION_ID")

#     # Inputting user's emails
#     website = input("Enter the domain for the website:  ")
    
#     #  Scraper Code for crawler and scraper
#     url = f"https://{website}"
#     found_urls = crawl(url)
#     # Fetch emails
#     emails_code = []
#     for url in found_urls:
#         emails_code = fetch_emails_from_url(url)

#     # Search Results from Google
#     search_results = extract_emails_from_site(website, api_key, search_engine_id)
    
#     emails_dorking = []
#     if search_results:
#         emails = process_extracted_emails(search_results, website)
#         if emails:
#             print(f"Emails found:")
#             for email in emails:
#                 print(email)
#             emails_dorking = emails
#     print(emails_code)
#     emails = emails_dorking+emails_code
#     emails = list(set(emails))
#     print(emails)
#     # Save emails to Excel file            
#     save_emails_to_excel(emails)

#     # Save emails to CSV file
#     with open('emails.csv', mode='w', newline='') as file:
#         writer = csv.writer(file)
#         writer.writerow(["Emails"])
#         # Writing each email as a new row in the CSV file
#         for e in emails:
#             writer.writerow([e])
