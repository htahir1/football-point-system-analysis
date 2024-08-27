import requests
from datetime import datetime
import pandas as pd
import os

API_KEY = 'APIKEY'  # Replace with your actual API key
BASE_URL = 'https://api.football-data.org/v4/'

def get_seasons(num_years=20):
    current_year = datetime.now().year
    return range(current_year, current_year - num_years, -1)

def fetch_season_data(season):
    url = f"{BASE_URL}competitions/PL/standings"
    headers = {'X-Auth-Token': API_KEY}
    params = {'season': f"{season}"}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        print(f"Error fetching data for season {season}-{season+1}: {response.status_code}")
        print(response.json())
        return None
    return response.json()

def calculate_new_standings(standings):
    new_standings = []
    for team in standings:
        new_points = team['won'] * 3 + team['draw'] * 2 + team['lost'] * 0
        new_standings.append({
            'team': team['team']['name'],
            'original_points': team['points'],
            'new_points': round(new_points, 1),
            'position': team['position']  # Change 'original_position' to 'position'
        })
    return sorted(new_standings, key=lambda x: x['new_points'], reverse=True)

def compare_standings(original_standings, new_standings):
    for i, team in enumerate(new_standings, 1):
        team['new_position'] = i
        original_position = next(t['position'] for t in original_standings if t['team']['name'] == team['team'])
        team['position_change'] = original_position - i
    return new_standings

def analyze_seasons(seasons):
    all_season_data = []
    for season in seasons:
        print(f"Fetching data for season {season}-{season+1}...")
        data = fetch_season_data(season)
        # time.sleep(1)
        if data and 'standings' in data:
            original_standings = data['standings'][0]['table']
            new_standings = calculate_new_standings(original_standings)
            compared_standings = compare_standings(original_standings, new_standings)
            
            all_season_data.append({
                'season': f"{season}-{season+1}",
                'standings': compared_standings
            })
        else:
            print(f"No data available for season {season}-{season+1}")
    return all_season_data

def output_league_table(standings, season):
    df = pd.DataFrame(standings)
    
    # Rename columns to match the desired output
    column_mapping = {
        'position': 'Position',
        'team': 'Club',
        'playedGames': 'Matches',
        'won': 'Wins',
        'draw': 'Draws',
        'lost': 'Losses',
        'goalsFor': 'GoalsScored',
        'goalsAgainst': 'GoalsConceded',
        'goalDifference': 'GoalDiff',
        'points': 'Points'
    }
    df = df.rename(columns=column_mapping)
    
    # Handle team name if it's a dictionary
    if 'Club' in df.columns and isinstance(df['Club'].iloc[0], dict):
        df['Club'] = df['Club'].apply(lambda x: x.get('name', ''))
    
    # Ensure all required columns are present
    required_columns = ['Position', 'Club', 'Matches', 'Wins', 'Draws', 'Losses', 'GoalsScored', 'GoalsConceded', 'GoalDiff', 'Points']
    for col in required_columns:
        if col not in df.columns:
            df[col] = ''  # or some default value
    
    # Select and order the columns
    df = df[required_columns]
    
    # Sort by Position
    df = df.sort_values('Position')
    
    # Create the data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Save the CSV file
    filename = f"data/epl{season}leaguetable.csv"
    df.to_csv(filename, index=False, quoting=1)
    print(f"League table saved to {filename}")

def main():
    seasons = get_seasons()
    results = analyze_seasons(seasons)
    
    for season_data in results:
        season = season_data['season']
        print(f"\nSeason: {season}")
        df = pd.DataFrame(season_data['standings'])
        print(df[['team', 'original_points', 'new_points', 'position_change']])
        
        # Analyze championship changes
        original_champion = df.loc[df['position'] == 1, 'team'].values[0]
        new_champion = df.loc[0, 'team']
        if original_champion != new_champion:
            print(f"Championship change: {original_champion} -> {new_champion}")
        
        # Output league table
        original_standings = next((data['standings'] for data in results if data['season'] == season), None)
        if original_standings:
            season_short = season.replace('-', '')[:4]  # e.g., "2016-2017" becomes "1617"
            output_league_table(original_standings, season_short)
        else:
            print(f"No original standings data found for season {season}")

if __name__ == "__main__":
    main()