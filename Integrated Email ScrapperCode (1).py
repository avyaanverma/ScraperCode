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

# Function to fetch emails using Google Custom Search API with pagination
def extract_emails_from_site(website, apiKey, sessionId, pages=5):
    """
    Uses Google Custom Search API to find indexed pages of the website and extract email addresses.
    Implements pagination to get more results.

    Parameters:
        website (str): The domain name to search for.
        apiKey (str): The Google API Key.
        sessionId (str): The custom search engine ID.
        pages (int): Number of pages to search (API paginates every 10 results).

    Returns:
        list: All collected emails.
    """
    print(f"Finding indexed pages for: {website}")
    all_emails = []
    
    for start in range(1, pages * 10, 10):  # Pagination: increments the start index by 10
        query = f'intext:"@{website}" site:{website}'
        params = {
            'key': apiKey,
            'cx': sessionId,
            'q': query,
            'num': 10,
            'start': start  # Pagination parameter to fetch results from each page
        }

        google_search_url = 'https://www.googleapis.com/customsearch/v1'
        response = requests.get(google_search_url, params=params)

        if response.status_code == 200:
            print(f"Request successful for page {start // 10 + 1}!")
            search_results = response.json()
            emails = process_extracted_emails(search_results, website)
            all_emails.extend(emails)
        else:
            print(f"Failed to fetch results for page {start // 10 + 1}. Status code: {response.status_code}")
            break

        time.sleep(1)  # Delay between requests to prevent rate-limiting

    return list(set(all_emails))  # Return unique emails

# Function to process the extracted emails from search results
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

# Function to crawl a website and extract URLs
def crawl(seed_url, max_urls=100):
    """
    Crawls the website starting from the seed_url, collecting up to max_urls.
    
    Parameters:
        seed_url (str): The initial URL to begin the crawl.
        max_urls (int): The maximum number of URLs to crawl.
    
    Returns:
        list: A list of found URLs.
    """
    visited = set()  # Track visited URLs
    queue = [seed_url]  # URLs to be crawled
    urls = []  # To store the URLs found

    while queue and len(urls) < max_urls:
        url = queue.pop(0)
        if url in visited:
            continue

        try:
            # Fetch the page content
            response = requests.get(url)
            visited.add(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract all <a> tag links
            for link in soup.find_all('a', href=True):
                full_url = re.sub(r'#.*$', '', urljoin(url, link['href']))  # Clean fragment URLs
                if full_url not in visited and full_url not in queue and full_url.startswith(seed_url):
                    queue.append(full_url)
                    urls.append(full_url)

                    if len(urls) >= max_urls:
                        break

        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")

        # Optional delay to prevent rate-limiting
        time.sleep(1)

    return urls

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
    # Crawling example
    seed_url = "https://www.vitbhopal.ac.in"
    found_urls = crawl(seed_url, max_urls=50)  # Increased URL crawling limit
    print(f"Found {len(found_urls)} URLs")

    # Fetch emails from specific URLs
    all_emails = []
    for url in found_urls:
        emails = fetch_emails_from_url(url)
        all_emails.extend(emails)
    
    # Ensure unique emails
    all_emails = list(set(all_emails))

    # Display the found emails
    print(f"Emails found from crawling:")
    for email in all_emails:
        print(email)

    # Save emails to Excel file
    save_emails_to_excel(all_emails)

    # API credentials from .env file
    api_key = os.getenv("Your_Google_API_KEY")
    search_engine_id = os.getenv("SESSION_ID")

    # Extract emails using Google Custom Search API
    website = "vitbhopal.ac.in"
    google_emails = extract_emails_from_site(website, api_key, search_engine_id, pages=5)

    print(f"Emails found via Google Search API:")
    for email in google_emails:
        print(email)

    # Save emails to Excel file
    save_emails_to_excel(google_emails, filename='google_emails.xlsx')
