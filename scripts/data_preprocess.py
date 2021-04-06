import pandas as pd
import datetime


def generate_seasons():
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


print(generate_seasons())
