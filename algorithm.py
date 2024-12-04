import os
import requests
import pandas as pd
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

# Function to download CSV file
def download_csv(csv_link, folder_path='csv_files'):
    # Extract the raw content URL from GitHub
    raw_url = csv_link.replace('github.com', 'raw.githubusercontent.com').replace('tree/main', '')
    response = requests.get(raw_url)
    
    # Ensure folder exists
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    filename = csv_link.split('/')[-1]
    filepath = os.path.join(folder_path, filename)
    
    # Save the file locally
    with open(filepath, 'wb') as f:
        f.write(response.content)
    
    print(f"Downloaded: {filename}")
    return filepath

# Function to process the CSV file and return a DataFrame
def process_csv(filepath, week, positions=['RB', 'WR', 'QB', 'TE']):
    # Load CSV into a DataFrame
    df = pd.read_csv(filepath)
    
    # Filter by position
    df = df[df['Pos'].isin(positions)]
    
    # Select relevant columns and add 'Week' column
    selected_columns = [
        'PlayerName', 'Pos', 'PlayerOpponent', 'PassingYDS', 'PassingTD', 'PassingInt', 
        'RushingYDS', 'RushingTD', 'ReceivingRec', 'ReceivingYDS', 'ReceivingTD', 'RetTD', 
        'FumTD', '2PT', 'Fum'
    ]
    
    df_filtered = df[selected_columns]
    
    # Add the 'Week' column based on the input week
    df_filtered['Week'] = week
    
    # Remove '@' symbol from 'PlayerOpponent' column
    df_filtered['PlayerOpponent'] = df_filtered['PlayerOpponent'].str.replace('@', '', regex=False)
    
    return df_filtered

# Main function to scrape the pages and process CSVs
def scrape_and_process_csvs():
    all_data = []  # List to store all processed data
    
    # Loop through the side links (1 to n, adjust n based on the total number of side links)
    for x in range(1, 10):  # Assuming the side links range from 1 to 9, adjust as needed
        side_link = f'https://github.com/hvpkod/NFL-Data/tree/main/NFL-data-Players/2024/{x}'
        print(f"Scraping {side_link}...")
        
        # Get CSV links from the side link
        side_csv_links = get_csv_links(side_link)
        
        # Download and process each CSV
        for csv_link in side_csv_links:
            # Download the CSV file
            filepath = download_csv(csv_link)
            
            # Process the CSV file for the specific week (week number is the same as 'x')
            week_data = process_csv(filepath, week=x)
            
            # Append processed data to all_data list
            all_data.append(week_data)

    # Combine all data into a single DataFrame
    final_df = pd.concat(all_data, ignore_index=True)
    
    # Optional: Save the final DataFrame to a CSV file
    final_df.to_csv('nfl_players_data.csv', index=False)
    
    print("Data processing complete. Saved as 'nfl_players_data.csv'.")
    
    return final_df

# Run the scraper and process CSV files
final_df = scrape_and_process_csvs()
print(final_df.head())  # Print the first few rows of the final DataFrame
