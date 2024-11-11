import blindPhish as bp
import pandas as pd
import emailverifier
import sys
sys.path.append("D:\\Code\\SecurityCodes\\LocalScraper\\modules")
from banner_bash import banner_bash


if __name__=="__main__":
# banner name
    str = banner_bash("BlindScraper")
    print(str)

# Extracting Emails 
# enter organisation name
    website = input("Enter the domain for the website:  ")
    url = f"https://{website}"
    found_urls = bp.crawl(url)
    all_emails = []
    for url in found_urls:
        emails = bp.fetch_emails_from_url(url)
        all_emails.extend(emails)
    filename = f"./excels/{website.split('.')[0]}.xlsx"
    df = pd.DataFrame(all_emails, columns=['Email'])
    df.to_excel(filename, index=False)


# read an excel file


# convert excel file to dataframe 

# apply the functions to the dataframe

# return the dataframe with data 

# save to an excel file 