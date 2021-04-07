import requests
from bs4 import BeautifulSoup
import pandas as pd


def get_current_team_standings(year: str) -> pd.DataFrame:
    nhl_standings_html = requests.get(f"https://www.hockey-reference.com/leagues/NHL_{year}_standings.html").text

    nhl_standings_soup = BeautifulSoup(nhl_standings_html, "html.parser")

    table_header_html = nhl_standings_soup.find(id="standings").find('thead').find_all('th')

    table_headers = ["Team"] + [th.text for th in table_header_html if th.text]

    team_row_html = nhl_standings_soup.find(id="standings").find('tbody').find_all(class_="full_table")

    team_data = []

    for row in team_row_html:
        team_name = row.find("th").find("a").text
        team_values = [team_name] + [td.text for td in row.find_all("td")]
        team_data.append(team_values)

    team_data_df = pd.DataFrame(team_data, columns=table_headers)

    return team_data_df


def get_current_skater_data(year: str) -> pd.DataFrame:
    skater_stats_html = requests.get(f"https://www.hockey-reference.com/leagues/NHL_{year}_skaters.html").text

    skater_stats_soup = BeautifulSoup(skater_stats_html, "html.parser")

    table_header_html = skater_stats_soup.find(id="stats").find("thead").find_all(attrs={"scope": "col"})

    table_headers = [th.text for th in table_header_html]
    table_headers = ["PLUSMINUS" if header == "+/-" else header for header in table_headers]

    stats_row_html = skater_stats_soup.find(id="stats").find("tbody").find_all("tr")

    skater_data = []

    for row in stats_row_html:
        if not row.get("class") or "thead" not in row.get("class"):
            rk = row.find("th").text
            player_values = [rk] + [td.text for td in row.find_all("td")]
            skater_data.append(player_values)

    skater_data_df = pd.DataFrame(skater_data, columns=table_headers)

    return skater_data_df


def get_current_data(year: str) -> None:
    current_standings_data = get_current_team_standings(year)
    current_skater_data = get_current_skater_data(year)

    # save up-to-date current season data (standings and skater data) to CSV files in data folder
    current_standings_data.to_csv("./nhl_data/season_standings/season_standings_20202021.csv", index_label=False)
    current_skater_data.to_csv("./nhl_data/skater_stats/skater_stats_20202021.csv", index_label=False)