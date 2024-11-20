import re
import requests
from bs4 import BeautifulSoup

email = "rizwan.ur@vitbhopal.ac.in"


# Extract name from the email
local_part = email.split('@')[0]
name_parts = re.split('[._-]', local_part)
full_name = " ".join([part.capitalize() for part in name_parts])

# Specify organization name (replace with actual organization name if needed)
organization_name = re.split('[@]', email)[1].split('.')[0]
print(f"org name : {organization_name}")

name=""
for a in full_name:
  if a.isdigit() or a in ["@_!#$%^&*()<>?/\|}{~:]"]: continue
  name+=a
print(name) 

# Search for LinkedIn profile using the format [name] [organization] [linkedin]
query = f"{name} {organization_name} linkedin site:linkedin.com"
search_url = f"https://www.google.com/search?q={query}"

# Send a GET request to Google Search
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
response = requests.get(search_url, headers=headers)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    linkedin_url = None
    # Look for LinkedIn URLs in the search results
    for link in soup.find_all('a', href=True):
        href = link['href']
        if 'linkedin.com/in/' in href:
            # Clean up the URL to get the full LinkedIn profile path
            linkedin_url = href.split('&')[0]  # Remove unnecessary query parameters
            if linkedin_url.startswith('/url?q='):
                linkedin_url = linkedin_url[7:]  # Remove the '/url?q=' part of the link
            break

    # Output the results
    print(f"Name extracted: {full_name}")
    if linkedin_url:
        print(f"LinkedIn Profile: {linkedin_url}")
    else:
        print("No LinkedIn profile found.")
else:
    print("Failed to retrieve search results.")
