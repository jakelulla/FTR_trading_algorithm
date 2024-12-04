import requests
from bs4 import BeautifulSoup

# Function to extract data from a single week (check table extraction)
def scrape_week_data_single_page(week_number):
    url = f'https://fantasy.espn.com/football/leaders?statSplit=singleScoringPeriod&scoringPeriodId={week_number}'
    
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Print out the raw HTML to inspect the structure (for debugging)
    print(soup.prettify())  # This will output the HTML structure of the page
    
    # Find the table containing the player data
    table = soup.find('table', {'class': 'Table Table--align-right'})
    if not table:
        print("Table not found!")
        return []
    
    # Print the table HTML to ensure we have found it
    print(table.prettify())  # Print the entire table to inspect its structure
    
    rows = table.find_all('tr')[1:]  # Skip header row
    
    week_data = []
    
    # Extract data from each row in the table
    for row in rows:
        columns = row.find_all('td')
        player_name = columns[0].get_text(strip=True)
        opp = columns[1].get_text(strip=True)
        fpts = columns[2].get_text(strip=True)
        position = columns[0].find('span', {'class': 'PlayerHeader__Position'}).get_text(strip=True) if columns[0].find('span', {'class': 'PlayerHeader__Position'}) else None
        
        # Store the data for the current player in the week
        week_data.append({
            'Player': player_name,
            'Position': position,
            'Week': week_number,
            'OPP': opp,
            'FPTS': fpts
        })
    
    return week_data

# Test on Week 1 for debugging
week_1_data = scrape_week_data_single_page(1)
print(week_1_data)  # Output the collected data for Week 1
