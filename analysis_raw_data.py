import pandas as pd
import os
from datetime import datetime

def get_seasons(num_years=20):
    current_year = datetime.now().year
    return range(current_year, current_year - num_years, -1)

def get_season_code(year):
    return f"{str(year)[-2:]}{str(year+1)[-2:]}"

def read_raw_data(year):
    season_code = get_season_code(year)
    filename = f"data/epl{season_code}leaguetable.csv"
    if not os.path.exists(filename):
        print(f"No data available for season {year}-{year+1}")
        return None

    dtypes = {
        'Position': 'int',
        'Club': 'str',
        'Matches': 'int',
        'Wins': 'int',
        'Draws': 'int',
        'Losses': 'int',
        'GoalsScored': 'int',
        'GoalsConceded': 'int',
        'GoalDiff': 'int',
        'Points': 'int'
    }

    df = pd.read_csv(filename, dtype=dtypes)
    return df

def calculate_new_standings(df):
    df['new_points'] = df['Wins'] * 2 + df['Draws'] * 1
    df['position_change'] = df['Position'] - df['new_points'].rank(method='min', ascending=False)
    return df.sort_values('new_points', ascending=False).reset_index(drop=True)

def analyze_seasons(seasons):
    all_season_data = []
    for year in seasons:
        print(f"Analyzing data for season {year}-{year+1}...")
        df = read_raw_data(year)
        if df is not None:
            new_standings = calculate_new_standings(df)
            all_season_data.append({
                'season': f"{year}-{year+1}",
                'standings': new_standings
            })
    return all_season_data

def main():
    seasons = get_seasons()
    results = analyze_seasons(seasons)
    
    for season_data in results:
        season = season_data['season']
        df = season_data['standings']
        print(f"\nSeason: {season}")
        print(df[['Club', 'Points', 'new_points', 'position_change']])
        
        # Analyze championship changes
        original_champion = df.loc[df['Position'] == 1, 'Club'].values[0]
        new_champion = df.loc[0, 'Club']
        if original_champion != new_champion:
            print(f"Championship change: {original_champion} -> {new_champion}")

if __name__ == "__main__":
    main()