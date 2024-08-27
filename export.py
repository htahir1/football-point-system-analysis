import requests
import csv
from typing import List, Dict

def get_standings(api_key: str, league_id: int, season: int) -> List[Dict]:
    url = f"https://api.football-data.org/v4/competitions/{league_id}/standings"
    headers = {"X-Auth-Token": api_key}
    params = {"season": season}

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    data = response.json()
    standings = data["standings"][0]["table"]

    return standings

def write_csv(standings: List[Dict], filename: str) -> None:
    headers = ["Position", "Club", "Matches", "Wins", "Draws", "Losses", "GoalsScored", "GoalsConceded", "GoalDiff", "Points"]

    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)

        for team in standings:
            row = [
                team["position"],
                team["team"]["name"],
                team["playedGames"],
                team["won"],
                team["draw"],
                team["lost"],
                team["goalsFor"],
                team["goalsAgainst"],
                team["goalDifference"],
                team["points"]
            ]
            writer.writerow(row)

def main():
    api_key = "211da3ff3be84c69b1519379fc59aa55"  # Replace with your actual API key
    league_id = 2021 # Premier League
    season = 2020  # Change this to the desired season

    try:
        standings = get_standings(api_key, league_id, season)
        write_csv(standings, "premier_league_standings.csv")
        print(f"Standings for season {season} have been written to premier_league_standings.csv")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from the API: {e}")
    except IOError as e:
        print(f"Error writing to CSV file: {e}")

if __name__ == "__main__":
    main()