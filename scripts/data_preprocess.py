import pandas as pd
import datetime
from current_data import get_current_team_standings, get_current_skater_data
from typing import List, Dict
from sklearn.preprocessing import minmax_scale, LabelEncoder


def generate_seasons() -> List[str]:
    seasons = []
    current_date = datetime.datetime.now()
    current_month, current_year = current_date.month, current_date.year
    season_end_year = int(str(current_year)[-2:])

    if current_month >= 10:
        season_end_year = current_year + 1

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


def fix_team_names(team_data: pd.DataFrame, seasons: List[str]) -> pd.DataFrame:
    # Fix team name values
    replace_values = {
        "ampa Bay Lightning": "Tampa Bay Lightning",
        "ew Jersey Devils": "New Jersey Devils",
        "hicago Black Hawks": "Chicago Black Hawks",
        "hiladelphia Flyers": "Philadelphia Flyers",
        "innesota North Stars": "Minnesota North Stars",
        "ontreal Canadiens": "Montreal Canadiens",
        "orida Panthers": "Florida Panthers"
    }

    team_data = team_data.copy().replace({"Team": replace_values})

    # fix Jets rows to distinguish old org from new
    def replace_jets(row):
        new_jets_start = seasons.index("20112012")

        if row["Team"] == "Winnipeg Jets":
            if row["season"] in seasons[new_jets_start:]:  # for seasons 20112012 and later
                row["Team"] = "Winnipeg Jets (New)"
            else:
                row["Team"] = "Winnipeg Jets (Original)"

        return row

    team_data = team_data.apply(replace_jets, axis=1)

    return team_data


def replace_names_abbrevs(team_data: pd.DataFrame) -> pd.DataFrame:
    team_abbrevs = {
        "Anaheim Ducks": "ANA",
        "Arizona Coyotes": "ARI",
        "Atlanta Flames": "ATF",
        "Atlanta Thrashers": "ATL",
        "Boston Bruins": "BOS",
        "Buffalo Sabres": "BUF",
        "Carolina Hurricanes": "CAR",
        "Chicago Black Hawks": "CBH",
        "Columbus Blue Jackets": "CBJ",
        "Calgary Flames": "CGY",
        "Chicago Blackhawks": "CHI",
        "Colorado Rockies": "CLR",
        "Colorado Avalanche": "COL",
        "Dallas Stars": "DAL",
        "Detroit Red Wings": "DET",
        "Edmonton Oilers": "EDM",
        "Florida Panthers": "FLA",
        "Hartford Whalers": "HAR",
        "Los Angeles Kings": "LAK",
        "Mighty Ducks of Anaheim": "MDA",
        "Minnesota Wild": "MIN",
        "Minnesota North Stars": "MNS",
        "Montreal Canadiens": "MTL",
        "New Jersey Devils": "NJD",
        "Nashville Predators": "NSH",
        "New York Islanders": "NYI",
        "New York Rangers": "NYR",
        "Ottawa Senators": "OTT",
        "Philadelphia Flyers": "PHI",
        "Phoenix Coyotes": "PHX",
        "Pittsburgh Penguins": "PIT",
        "Quebec Nordiques": "QUE",
        "San Jose Sharks": "SJS",
        "St. Louis Blues": "STL",
        "Tampa Bay Lightning": "TBL",
        "Toronto Maple Leafs": "TOR",
        "Vancouver Canucks": "VAN",
        "Vegas Golden Knights": "VEG",
        "Winnipeg Jets (Original)": "WIN",
        "Winnipeg Jets (New)": "WPG",
        "Washington Capitals": "WSH"
    }

    team_data = team_data.copy().replace(team_abbrevs)

    return team_data


def convert_duplicates(skater_data: pd.DataFrame) -> pd.DataFrame:
    # identify all multi-team players (in most cases, players who were traded during a season)
    # by filtering dataframe to entries with "TOT" as the team
    traded_players = skater_data[skater_data["Tm"] == "TOT"]

    # crate a list that contains just the names and seasons, which we can iterate through
    traded_players_list = [(row[0], row[1]) for row in traded_players[["Player", "season"]].values]

    # create a list and populate with the team abbreviations that represent replacement values for "TOT" for each player + season
    team_most_games = []

    for player, season in traded_players_list:
        player_data = skater_data.loc[
            (skater_data["Player"] == player) & (skater_data["season"] == season) & (
                    skater_data["Tm"] != "TOT")].copy()
        # sort each individual player's DF by games played first, then PLUSMINUS > points if GP the same for multiple rows
        player_data = player_data.sort_values(by=["GP", "PLUSMINUS", "PTS"], ascending=False)
        team_most_games.append(player_data.iloc[0]["Tm"])

    # now replace "TOT" values in the original defensemen dataframe with the updated team abbreviation values
    skater_data.loc[skater_data["Tm"] == "TOT", "Tm"] = team_most_games

    skater_data = skater_data.drop_duplicates(subset=["season", "Rk"], keep="last")

    return skater_data


def pre_merge_preprocess(dfs: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    seasons = generate_seasons()

    # remove asterisks from team names
    dfs["standings"]["Team"] = dfs["standings"]["Team"].str.replace("*", "")
    dfs["skater_stats"]["Player"] = dfs["skater_stats"]["Player"].str.replace("*", "")
    dfs["voting"]["Player"] = dfs["voting"]["Player"].str.replace("*", "")

    # Adjust team names in standings data
    dfs["standings"] = fix_team_names(dfs["standings"], seasons)

    # replace team names with abbrevs in standings data
    dfs["standings"] = replace_names_abbrevs(dfs["standings"])

    # filter player data to defensemen only
    dfs["skater_stats"] = dfs["skater_stats"][dfs["skater_stats"]["Pos"] == "D"].copy().sort_values(
        by=["season", "Player", "GP"]).reset_index(drop=True)

    # deal with duplicates (traded players)
    dfs["skater_stats"] = convert_duplicates(dfs["skater_stats"].copy())

    return dfs


def merge_dfs(dfs: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    players_teams_data = dfs["skater_stats"].merge(dfs["standings"], how="left", left_on=["season", "Tm"],
                                                   right_on=["season", "Team"], suffixes=("_player", "_team"))
    voting_data = dfs["voting"].drop(["Age", "Tm", "Pos", "G", "A", "PTS", "PLUSMINUS", "PS"], axis=1)
    all_merged_data = players_teams_data.merge(voting_data, how="left", left_on=["season", "Player"],
                                               right_on=["season", "Player"])

    return all_merged_data


def drop_unused_cols(df: pd.DataFrame) -> pd.DataFrame:
    # create list of column names that will be dropped from the dataframe
    columns_to_drop = [
        "Rk",
        "Pos",
        "FOW",
        "FOL",
        "FO%",
        "Team",
        "GP_team",
        "W",
        "L",
        "OL",
        "PTS%",
        "GF",
        "GA",
        "SRS",
        "SOS",
        "RPt%",
        "RW",
        "RgRec",
        "RgPt%",
        "Place",
        "Vote%",
        "1st",
        "2nd",
        "3rd",
        "4th",
        "5th",
        "OPS",
        "DPS",
        "GPS"
    ]

    # create a copy of the dataframe post-dropping of columns
    pared_data = df.drop(columns_to_drop, axis=1).copy()

    return pared_data


def adjust_remaining_cols(df: pd.DataFrame, seasons: List[str]) -> pd.DataFrame:
    # create dictionary for substitutions
    abbrev_subs = {
        "PHX": "ARI",  # Phoenix Coyotes became Arizona Coyotes
        "MDA": "ANA",  # Mighty Ducks of Anaheim became Anaheim Ducks
        "CBH": "CHI"  # Chicago Black Hawks became Chicago Blackhawks
    }

    # apply substitutions
    df["Tm"] = df["Tm"].replace(abbrev_subs)

    # fix nulls in Votes column
    df.loc[df["Votes"].isnull(), "Votes"] = 0

    # convert Votes to percentage of total, excluding current season
    for season in seasons[:-1]:
        season_vote_data = df.loc[df["season"] == season, "Votes"]
        season_vote_data = season_vote_data / season_vote_data.sum()
        df.loc[df["season"] == season, "Votes"] = season_vote_data

    # fix ATOI column datatype/values
    df["ATOI"] = df["TOI"] / df["GP_player"]

    # create dictionary for column label substitutions
    new_column_labels = {
        "Player": "name",
        "Age": "age",
        "Tm": "team",
        "GP_player": "games_played",
        "G": "goals",
        "A": "assists",
        "PTS_player": "points",
        "PLUSMINUS": "plus_minus",
        "PIM": "penalty_minutes",
        "PS": "point_share",
        "EV": "even_strength_goals",
        "PP": "power_play_goals",
        "SH": "shorthanded_goals",
        "GW": "game_winning_goals",
        "EV.1": "even_strength_assists",
        "PP.1": "power_play_assists",
        "SH.1": "shorthanded_assists",
        "S": "shots",
        "S%": "shooting_pct",
        "TOI": "total_toi",
        "ATOI": "avg_toi",
        "BLK": "blocked_shots",
        "HIT": "hits",
        "PTS_team": "team_standings_pts",
        "Votes": "norris_point_pct",
    }

    # apply substitutions and check new column labels
    df.rename(new_column_labels, axis=1, inplace=True)

    return df


def fix_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    df.loc[df["shooting_pct"].isnull(), "shooting_pct"] = 0

    blocked_shots_missing = (df["blocked_shots"].isnull()) & (df["hits"].notnull())
    # insert 0 for blocked_shots value where missing
    df.loc[blocked_shots_missing, "blocked_shots"] = 0

    return df


def generate_features(df: pd.DataFrame) -> pd.DataFrame:
    stats_to_average = ["goals", "assists", "points", "blocked_shots", "hits"]
    pg_suffix = "_per_game"
    p60_suffix = "_per_60"

    for stat in stats_to_average:
        pg_label = stat + pg_suffix
        df[pg_label] = df[stat] / df["games_played"]

        p60_label = stat + p60_suffix
        df[p60_label] = df[stat] / (df["total_toi"] / 60)

    return df


def rescale_continuous(df: pd.DataFrame) -> pd.DataFrame:
    cols = ["age", "games_played", "goals", "assists", "points", "plus_minus", "penalty_minutes",
            "point_share", "even_strength_goals", "power_play_goals", "shorthanded_goals",
            "game_winning_goals", "even_strength_assists", "power_play_assists", "shorthanded_assists",
            "shots", "shooting_pct", "total_toi", "avg_toi", "blocked_shots", "hits", "team_standings_pts",
            "goals_per_game", "goals_per_60", "assists_per_game", "assists_per_60", "points_per_game",
            "points_per_60", "blocked_shots_per_game", "blocked_shots_per_60", "hits_per_game",
            "hits_per_60"]

    for season in df["season"].unique():
        season_cols = df.loc[df["season"] == season, cols].copy()
        rescaled_data = minmax_scale(season_cols)
        df.loc[df["season"] == season, cols] = rescaled_data

    return df


def encode_categorical(df: pd.DataFrame) -> pd.DataFrame:
    # encode team column -> convert to integers for use with tree-based models
    encoder = LabelEncoder()
    df["team"] = encoder.fit_transform(df["team"])

    return df


def post_merge_preprocess(df: pd.DataFrame) -> tuple:
    seasons = generate_seasons()

    df = drop_unused_cols(df)
    df = adjust_remaining_cols(df, generate_seasons())
    df = fix_missing_values(df)
    df = generate_features(df)
    df = rescale_continuous(df)
    df = encode_categorical(df)

    past_data = df[df["season"] != seasons[-1]].copy()
    current_data = df[df["season"] == seasons[-1]].copy()

    return past_data, current_data


dfs = create_dataframes("./nhl_data")
aggregated_data = aggregate_data(dfs)
premp_data = pre_merge_preprocess(aggregated_data)
merged_data = merge_dfs(premp_data)
print(post_merge_preprocess(merged_data)[0].head())

