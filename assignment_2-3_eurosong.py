import pandas as pd
import matplotlib
import seaborn as sns
import openpyxl
from typing import List

matplotlib.use('module://backend_interagg')  # explicitly use pycharm's inbuilt matplotlib backend

def get_final_placement(row, data_contestants):
    print(row)
    year = row["year"]
    country_id = row["to_country_id"]
    this_contestant_this_year_row = data_contestants[
        (data_contestants["year"] == year) &
        (data_contestants["to_country_id"] == country_id)
    ]
    final_placement = this_contestant_this_year_row["place_final"]
    if not final_placement.empty:
        return final_placement.values[0]
    return None

def get_vote_distribution_data(*, yearrange: List[int]):
    # get data and only use finals data
    data_all_years = pd.read_excel("Datasets/votes.xlsx")
    data_all_years = data_all_years[data_all_years["round"] == "final"]

    # read this at the start to save processing by reloading it many times later
    data_contestants = pd.read_excel("Datasets/contestants.xlsx")
    data_contestants = data_contestants[data_contestants["year"].isin(yearrange)]


    # create a dataframe which has the sum of all telepoints and jurypoints per country, marked by year
    processed_data = pd.DataFrame()
    for year in yearrange:
        data = data_all_years[data_all_years["year"] == year]
        grouped_data = data.groupby("to_country_id")[["tele_points", "jury_points"]].sum().reset_index()
        grouped_data["year"] = year

        grouped_data["final_placement"] = grouped_data.apply(get_final_placement, args=(data_contestants,), axis=1)
        processed_data = pd.concat([processed_data, grouped_data], ignore_index=True)
    return processed_data

# only select years in which the votes are seperate
valid_years = [2016, 2017, 2018, 2019, 2021, 2022, 2023]
data = get_vote_distribution_data(yearrange=valid_years)

# create the plot with palette for the placement (gold is number 1, black is lower)
colors = ["gold", "black"]
cmap = matplotlib.colors.LinearSegmentedColormap.from_list("custom_gold_black", colors, N=26)

plot = sns.scatterplot(
    data=data,
    x="tele_points",
    y="jury_points",
    hue="final_placement",
    palette = cmap
)

# plot visual adjustments
plot.set_title(f'telepoints vs jurypoints (hue marks placement)')
plot.legend(title='placement', bbox_to_anchor=(1.05, 1), loc='upper left', labels=['1-5', '5-10', '10-15', '15-20', '20-26'])

matplotlib.pyplot.tight_layout()
matplotlib.pyplot.show()