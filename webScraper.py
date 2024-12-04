import os
import requests
from bs4 import BeautifulSoup

# Base URL of the GitHub repository
base_url = 'https://github.com/hvpkod/NFL-Data/tree/main/NFL-data-Players/2024'

# Function to get CSV links from a specific page
def get_csv_links(page_url):
    response = requests.get(page_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all links that end with '.csv'
    csv_links = []
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        if href.endswith('.csv'):
            csv_links.append(f"https://github.com{href}")

    return csv_links

# Function to download and save CSV files
def download_csv(csv_link):
    # Extract the raw content URL from GitHub
    raw_url = csv_link.replace('github.com', 'raw.githubusercontent.com').replace('tree/main', '')
    response = requests.get(raw_url)
    
    # Save the file locally
    filename = csv_link.split('/')[-1]
    with open(filename, 'wb') as f:
        f.write(response.content)
    print(f"Downloaded: {filename}")

# Main function to scrape the pages
def scrape_csv_files():
    # Get the CSV links from the main page
    csv_links = get_csv_links(base_url)
    
    # Download CSVs from the main page
    for link in csv_links:
        download_csv(link)

    # Loop through the side links (1 to n, adjust n based on the total number of side links)
    for x in range(1, 10):  # Assuming the side links range from 1 to 9, adjust as needed
        side_link = f'https://github.com/hvpkod/NFL-Data/tree/main/NFL-data-Players/2024/{x}'
        print(f"Scraping {side_link}...")
        side_csv_links = get_csv_links(side_link)
        
        for link in side_csv_links:
            download_csv(link)

# Run the scraper
scrape_csv_files()
