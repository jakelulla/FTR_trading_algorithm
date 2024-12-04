import requests
from bs4 import BeautifulSoup
import pandas as pd
import io

# List of positions to scrape for each week
positions = ['QB', 'RB', 'TE', 'WR']

# Base URL for GitHub repository
base_url = 'https://github.com/hvpkod/NFL-Data/tree/main/NFL-data-Players/2024/'

# Function to get the list of week directories (excluding 'projected' weeks)
def get_week_links():
    # Request the main page that lists the weeks
    response = requests.get(base_url)
    if response.status_code != 200:
        print(f"Failed to retrieve base URL. Status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all the links that represent directories for weeks
    links = soup.find_all('a', href=True)
    week_links = []

    for link in links:
        href = link['href']
        # Ensure we are targeting valid directories that represent weeks
        if href.startswith('/hvpkod/NFL-Data/tree/main/NFL-data-Players/2024/') and 'projected' not in href:
            # Extract the week number from the URL (last part of the URL path after the last '/')
            week = href.strip('/').split('/')[-1]
            week_links.append(week)

    return week_links

# Function to scrape data from each week for a given position
def scrape_week_data(week, position):
    # Construct the raw GitHub URL for each .csv file for the position
    csv_url = f"https://raw.githubusercontent.com/hvpkod/NFL-Data/main/NFL-data-Players/2024/{week}/{position}.csv"
    
    # Send GET request to fetch the raw CSV file content
    response = requests.get(csv_url)
    if response.status_code == 200:
        # Read CSV content into a pandas DataFrame
        data = pd.read_csv(io.StringIO(response.text))
        
        # Add a 'Week' column to the DataFrame
        data['Week'] = week
        
        # Extract necessary columns (PlayerName, PlayerOpponent, TotalPoints)
        data_filtered = data[['PlayerName', 'PlayerOpponent', 'TotalPoints', 'Week']]
        
        return data_filtered
    else:
        print(f"Failed to retrieve data for {position} in week {week}. Status code: {response.status_code}")
        return pd.DataFrame()

# Function to scrape the full season data (PlayerName and Rank)
def scrape_nfl_data():
    all_data = pd.DataFrame(columns=['PlayerName', 'Rank'])
    
    for pos in positions:
        # Construct the URL for the CSV file of each position
        csv_url = f"https://raw.githubusercontent.com/hvpkod/NFL-Data/main/NFL-data-Players/2024/{pos}_season.csv"
        
        # Send GET request to fetch raw content of the CSV file
        response = requests.get(csv_url)
        
        if response.status_code == 200:
            # Read the CSV content into a pandas DataFrame
            data = pd.read_csv(io.StringIO(response.text))
            
            # Extract PlayerName and Rank columns
            data_filtered = data[['PlayerName', 'Rank']]
            
            # Append the data for the current position to the all_data DataFrame
            all_data = pd.concat([all_data, data_filtered], ignore_index=True)
        else:
            print(f"Failed to retrieve data for {pos}. Status code: {response.status_code}")
    
    return all_data

# Function to scrape all data and create a DataFrame for each player
def scrape_nfl_weekly_data():
    # Initialize the overall data DataFrame
    all_data = pd.DataFrame(columns=['PlayerName', 'Rank', 'Week', 'PlayerOpponent', 'TotalPoints'])

    # Scrape the main player data (season stats with PlayerName and Rank)
    season_data = scrape_nfl_data()

    # Get the list of weeks to scrape (excluding 'projected' weeks)
    weeks = get_week_links()

    if not weeks:
        print("No weeks found. Exiting...")
        return all_data

    for week in weeks:
        for pos in positions:
            # Scrape weekly data for each position (QB, RB, TE, WR)
            week_data = scrape_week_data(week, pos)
            if not week_data.empty:
                # Merge with season data to match PlayerName and Rank
                merged_data = pd.merge(season_data, week_data, on='PlayerName', how='inner')
                all_data = pd.concat([all_data, merged_data], ignore_index=True)

    return all_data

# Function to create a final DataFrame for each player with their name, rank, and game details
def create_final_player_data():
    # Scrape weekly data for all players
    nfl_weekly_data = scrape_nfl_weekly_data()

    if nfl_weekly_data.empty:
        print("No weekly data found. Exiting...")
        return pd.DataFrame()

    # Create a dictionary to store player data
    player_dict = {}

    # Group data by PlayerName
    grouped_data = nfl_weekly_data.groupby('PlayerName')

    for player, data in grouped_data:
        # Get the player's rank
        rank = data['Rank'].iloc[0]
        
        # Create a list of games for the player, with each game containing week, opponent, and total points
        games = []
        for _, row in data.iterrows():
            games.append({
                'Week': row['Week'],
                'PlayerOpponent': row['PlayerOpponent'],
                'TotalPoints': row['TotalPoints']
            })
        
        # Store the player's information in the dictionary
        player_dict[player] = {
            'Rank': rank,
            'Games': games
        }

    # Convert the dictionary into a DataFrame
    player_final_data = pd.DataFrame.from_dict(player_dict, orient='index').reset_index()
    player_final_data.rename(columns={'index': 'PlayerName'}, inplace=True)

    return player_final_data

# Execute the function and store the final DataFrame
final_player_data = create_final_player_data()

# Print data for a specific player (Josh Allen)
print(final_player_data[final_player_data['PlayerName'] == 'Josh Allen'])
