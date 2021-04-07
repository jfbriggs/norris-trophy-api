import pandas as pd
import datetime
from current_data import get_current_team_standings, get_current_skater_data
from typing import List


def generate_seasons() -> List[str]:
    seasons = []
    current_date = datetime.datetime.now()
    current_month, current_year = current_date.month, current_date.year
    season_end_year = int(str(current_year)[-2:])

    if current_month >= 10:
        season_end_year = current_year + 1

    print(season_end_year)

    for i in range(79, 99):
        seasons.append("19" + str(i) + "19" + str(i + 1))

    seasons.append("19992000")

    for i in range(0, season_end_year):
        first = str(i).zfill(2)
        second = str(i + 1).zfill(2)
        season = "20" + first + "20" + second

        if season != "20042005":  # leave out 04-05, as a lockout caused a total loss of that season
            seasons.append("20" + first + "20" + second)

    return seasons


def get_current_data(year: str) -> None:
    current_standings_data = get_current_team_standings(year)
    current_skater_data = get_current_skater_data(year)

    # save up-to-date current season data (standings and skater data) to CSV files in data folder
    current_standings_data.to_csv("./nhl_data/season_standings/season_standings_20202021.csv", index_label=False)
    current_skater_data.to_csv("./nhl_data/skater_stats/skater_stats_20202021.csv", index_label=False)


def create_dataframes(data_path: str) -> dict:
    seasons = generate_seasons()

    standings_prefix = "season_standings"
    skater_stats_prefix = "skater_stats"
    norris_voting_prefix = "norris_voting"

    standings_dfs = []
    skater_stats_dfs = []
    voting_dfs = []

    for season in seasons:
        standings_df = pd.read_csv(f"{data_path}/{standings_prefix}/{standings_prefix}_{season}.csv")
        standings_df["season"] = season
        standings_dfs.append(standings_df)

        skater_stats_df = pd.read_csv(f"{data_path}/{skater_stats_prefix}/{skater_stats_prefix}_{season}.csv")
        skater_stats_df["season"] = season
        skater_stats_dfs.append(skater_stats_df)

        # for voting data, there's none for current, suspended season - skip it
        try:
            voting_df = pd.read_csv(f"{data_path}/{norris_voting_prefix}/{norris_voting_prefix}_{season}.csv")
            voting_df["season"] = season
            voting_dfs.append(voting_df)
        except:
            pass

    return {
        "standings": standings_dfs,
        "skater_stats": skater_stats_dfs,
        "voting": voting_dfs
    }


def aggregate_data(data: dict) -> dict:
    result = {}
    for dataset, df_list in data.items():
        result[dataset] = pd.concat(df_list).reset_index(drop=True)

    return result
