import pandas as pd
import matplotlib
import seaborn as sns
import openpyxl

matplotlib.use('module://backend_interagg')  # explicitly use pycharm's inbuilt matplotlib backend

def get_contestants_data(what_data: str, country: str):
    pd.set_option('display.max_columns', None)
    data = pd.read_excel("Datasets/contestants.xlsx")
    pd.set_option('display.max_columns', 10)
    match what_data:
        case "distribution of top place per country":
            data = data[data['to_country'] == country]
            data = data[['place_contest', 'year']]

    return data

countries = ["Lithuania", "Sweden", "Netherlands"]
for country in countries:
    data = get_contestants_data('distribution of top place per country', country)
    sns.set_theme()

    colors = ["gold", "black"]
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("custom_gold_black", colors, N=8)

    placement_plot = sns.histplot(
        data=data,
        x="place_contest",
        stat="count",
        binrange=(0,40),
        bins = 8
    )
    placement_plot.set_title(f'distribution of placements in {country}')

    for i in range(0,8):
        placement_plot.patches[i].set_facecolor(cmap(i))
    matplotlib.pyplot.show()