import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import time
from dotenv import load_dotenv
import os

# Load environment variables (for API key and Search Engine ID)
load_dotenv()

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

        print(f"Crawling: {url}")
        try:
            # Fetch the page content
            response = requests.get(url)
            visited.add(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract all <a> tag links
            for link in soup.find_all('a', href=True):
                full_url = urljoin(url, link['href'])
                if full_url not in visited and full_url not in queue:
                    queue.append(full_url)
                    urls.append(full_url)

                    if len(urls) >= max_urls:
                        break

        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")

        # Optional delay to prevent rate-limiting
        time.sleep(1)

    return urls

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
        tuple: Lists of Gmail and domain-specific email addresses.
    """
    all_gmails = []
    comp_mail = []

    if 'items' in text:
        for item in text['items']:
            snippet = item.get('snippet', '')
            print(f"Snippet: {snippet}")
            
            # Regex patterns to find emails
            pattern = '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            dom_pattern = rf'[a-zA-Z0-9._%+-]+@{re.escape(website)}'

            gmail_accounts = re.findall(pattern, snippet)
            domain_accounts = re.findall(dom_pattern, snippet)

            all_gmails.extend(gmail_accounts)
            comp_mail.extend(domain_accounts)
    else:
        print("No results found.")

    return all_gmails, comp_mail

# Main script
if __name__ == "__main__":
    # Crawling example
    seed_url = "https://www.vitbhopal.ac.in"
    found_urls = crawl(seed_url)
    print(f"Found {len(found_urls)} URLs:")
    for url in found_urls:
        print(url)

    # Fetch emails from specific URLs (optional)
    for url in found_urls:
        emails = fetch_emails_from_url(url)
        print(f"Emails found on {url}:")
        for email in emails:
            print(email)

    # API credentials from .env file
    api_key = os.getenv("Your_Google_API_KEY")
    search_engine_id = os.getenv("SESSION_ID")

    # Extract emails using Google Custom Search API
    website = "vitbhopal.ac.in"
    search_results = extract_emails_from_site(website, api_key, search_engine_id)

    if search_results:
        gmails, domain_emails = process_extracted_emails(search_results, website)

        if gmails:
            print(f"Gmail accounts found:")
            for email in gmails:
                print(email)

        if domain_emails:
            print(f"Domain-specific emails found:")
            for email in domain_emails:
                print(email)
