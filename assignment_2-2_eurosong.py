import pandas as pd
import matplotlib
import seaborn as sns
import openpyxl
from typing import List

matplotlib.use('module://backend_interagg')  # explicitly use pycharm's inbuilt matplotlib backend

def get_vote_distribution_data(*, yearrange: List[int]):
    # get data and only use finals data
    data_all_years = pd.read_excel("Datasets/votes.xlsx")
    data_all_years = data_all_years[data_all_years["round"] == "final"]

    # create a dataframe which has the sum of all telepoints and jurypoints per country, marked by year
    processed_data = pd.DataFrame()
    for year in yearrange:
        data = data_all_years[data_all_years["year"] == year]
        grouped_data = data.groupby("to_country_id")[["tele_points", "jury_points"]].sum().reset_index()
        grouped_data["year"] = year
        processed_data = pd.concat([processed_data, grouped_data], ignore_index=True)
    return processed_data

# only select years in which the votes are seperate
valid_years = [2016, 2017, 2018, 2019, 2021, 2022, 2023]
data = get_vote_distribution_data(yearrange=valid_years)

# create the plot with palette for the years
palette = sns.cubehelix_palette(start=0.8, rot=-.1, light=0.7, n_colors=len(valid_years))
plot = sns.scatterplot(
    data=data,
    x="tele_points",
    y="jury_points",
    hue="year",
    palette = palette
)

# plot visual adjustments
plot.set_title(f'telepoints vs jurypoints (hue marks year)')
plot.legend(title='Year', bbox_to_anchor=(1.05, 1), loc='upper left')

matplotlib.pyplot.tight_layout()
matplotlib.pyplot.show()