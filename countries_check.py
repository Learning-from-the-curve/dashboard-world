import pandas as pd
import numpy as np
import pickle

from process_functions import adjust_names, aggregate_countries
from pickle_functions import picklify
from pathlib import Path

#download, filter and stores the updated list of countries present in the john hopkins files

#download from the JH repo
url_confirmed = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
df_confirmed = pd.read_csv(url_confirmed)

#filter the countries' names to fit our list of names
df_confirmed = adjust_names(df_confirmed.copy())
df_confirmed = aggregate_countries(df_confirmed.copy(), graph = 'scatter')

#store in pickle files
picklify(set(df_confirmed['Country/Region'].copy()), 'set_countries_JH')
