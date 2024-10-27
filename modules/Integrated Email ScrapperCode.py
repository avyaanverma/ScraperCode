import requests
from bs4 import BeautifulSoup
import re
import time
import os
from dotenv import load_dotenv
import pandas as pd

# Load environment variables (for API key and Search Engine ID)
load_dotenv()

# Function to fetch email addresses from a given URL
def fetch_emails_from_url(url):
    """
    Extracts email addresses from the content of a given URL.

    Parameters:
        url (str): The URL to scrape for email addresses.

    Returns:
        list: A list of found email addresses.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()

        # Regex pattern to find emails
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, text)

        return list(set(emails))  # Return unique emails

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
    print(f"Finding indexed pages for: {website}")
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

# Function to save emails to an Excel file
def save_emails_to_excel(emails, filename='emails.xlsx'):
    """
    Saves the list of emails to an Excel file.

    Parameters:
        emails (list): List of email addresses.
        filename (str): The filename for the Excel file.
    """
    df = pd.DataFrame(emails, columns=['Email'])
    df.to_excel(filename, index=False)
    print(f"Emails saved to {filename}")

# Main script
if __name__ == "__main__":
    # API credentials from .env file
    api_key = os.getenv("Your_Google_API_KEY")
    search_engine_id = os.getenv("SESSION_ID")

    # Extract emails using Google Custom Search API
    website = "vitbhopal.ac.in"
    search_results = extract_emails_from_site(website, api_key, search_engine_id)

    if search_results:
        emails = process_extracted_emails(search_results, website)

        if emails:
            print(f"Emails found:")
            for email in emails:
                print(email)

            # Save emails to Excel file
            save_emails_to_excel(emails)
