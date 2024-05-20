import matplotlib
import requests
import zipfile
import io
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

matplotlib.use('module://backend_interagg')  # explicitly use pycharm's inbuilt matplotlib backend

'''
Plot how good each country is at voting on the "best" countries

For each country:
1. Determine how many votes to country A, B, C etc. 
2. Then, compare how many votes they gave to the final place of country A,B,C
3. Calculate a coefficient for this (coefficient is 1 if they voted the most on first place and the least on last place,
coefficient is 0 if they voted the least on first place and the most on first place)
4. Now average it for each year, to get a general coefficient for each country.
5. Plot each countries' coefficient by mapping to green-red in a geographic map
'''

# load datasets into memory to avoid doing this multiple times later
data_votes_source = pd.read_excel("Datasets/votes.xlsx")
data_contestants_source = pd.read_excel("Datasets/contestants.xlsx")
valid_years = [2016, 2017, 2018, 2019, 2021, 2022, 2023]

def calculate_coefficient(country: str):
    data_votes_all_years = data_votes_source
    data_votes_all_years = data_votes_all_years[data_votes_all_years["from_country_id"] == country]
    data_contestants_all_years = data_contestants_source
    coefficients = []
    not_voted_counter = 0

    for year in valid_years:
        data_votes = data_votes_all_years[data_votes_all_years["year"] == year]
        data_votes = data_votes[data_votes["round"] == "final"]
        data_votes = data_votes[data_votes[
                                    "tele_points"] > 0.1]  # exclude countries with zero telepoints since we can't meaningfully distinguish these
        countries_voted_on = data_votes["to_country_id"]

        if not countries_voted_on.empty:
            number_of_countries_voted_on = len(countries_voted_on)

            # Rank the votes given by each country
            data_votes['ranking_according_to_this_country'] = data_votes["tele_points"].rank(method='min', ascending=False).astype(int)

            # find real votes from the other dataset and add to big dataframe
            data_contestants = data_contestants_all_years[data_contestants_all_years["year"] == year]
            data_contestants = data_contestants[data_contestants["to_country_id"].isin(countries_voted_on)] # only get other countries on which this country voted
            data = pd.merge(data_contestants, data_votes, on='to_country_id')
            data = data[['ranking_according_to_this_country', 'place_contest', 'to_country_id']]

            # Calculate and normalize the rank differences
            data['difference'] = (data['place_contest'] - data['ranking_according_to_this_country']).abs()
            data['normalized_difference'] = data['difference'] / (number_of_countries_voted_on - 1)

            # Calculate the coefficient for each country
            coefficient = 1 - data['normalized_difference'].sum() / (number_of_countries_voted_on - 1)
            coefficients.append(coefficient)
        else:
            not_voted_counter = not_voted_counter + 1

    if not_voted_counter > 1:
        print (f"country {country} did not vote on anyone in {not_voted_counter} out of {len(valid_years)} years, so confidence for coefficient is lower")
    average_coefficient = sum(coefficients) / len(coefficients)
    return average_coefficient

def get_countries_in_valid_years():
    data_votes = data_votes_source
    data_votes = data_votes[data_votes['year'].isin(valid_years)]
    countries = pd.DataFrame()
    countries["country_id"] = data_votes['from_country_id'].unique()
    unqiue_country_data = data_contestants_source[['to_country_id', 'to_country']].drop_duplicates(inplace=False)
    countries = pd.merge(unqiue_country_data, countries, left_on='to_country_id',
                                    right_on='country_id', how='right')
    countries = countries.rename(columns={"to_country": "country_name"}).drop(axis=1,
                                                                                               labels='to_country_id').dropna()
    return countries

def plot_countries(coefficient_dataframe):
    data = coefficient_dataframe

    # get country data
    url_countries = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
    response = requests.get(url_countries)
    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        z.extractall("natural_earth_countries")
    gdf_countries = gpd.read_file("natural_earth_countries/ne_110m_admin_0_countries.shp")

    # List of European countries to use
    european_countries = coefficient_dataframe['country_name'].to_list()

    # filter obtained country data for data that i created earlier
    gdf_europe = gdf_countries[gdf_countries['NAME'].isin(european_countries)]
    gdf_europe = gdf_europe.merge(coefficient_dataframe, left_on='NAME', right_on='country_name')

    # plot and make pretty
    bright_red = "#FF7F7F"  # Light red
    bright_green = "#7FFF7F"  # Light green
    red_green_color_map = mcolors.LinearSegmentedColormap.from_list("coef_cmap", [bright_red, bright_green])
    normalize_map = mcolors.Normalize(vmin=0.1, vmax=0.7)
    gdf_europe = gdf_europe.to_crs(3857)
    fig, ax = plt.subplots(1, 1, dpi=300,  figsize=(8, 6))
    gdf_europe.plot(ax=ax, color=gdf_europe['coefficient'].apply(lambda x: red_green_color_map(normalize_map(x))), edgecolor='black',
                    linewidth=0.5)

    ax.set_xlim([-3500000, 6000000])
    ax.set_ylim([3000000, 12000000])

    sm = plt.cm.ScalarMappable(cmap=red_green_color_map, norm=normalize_map)
    sm._A = [] # idk why setting this to an empty list is necessary, but it fixes my stuff
    color_bar = fig.colorbar(sm, ax=ax)
    color_bar.set_label('Voting Coefficient')
    plt.title('Voting prediction power per European country population in Eurovision (2016-2023)')
    plt.tight_layout()
    ax.axis('off')
    plt.show()


if __name__ == '__main__':
    country_coefficients = get_countries_in_valid_years()

    country_coefficients['coefficient'] = country_coefficients['country_id'].apply(calculate_coefficient)

    plot_countries(country_coefficients)
