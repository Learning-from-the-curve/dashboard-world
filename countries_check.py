import pandas as pd
import numpy as np
import pickle

from process_functions import adjust_names, aggregate_countries
from pickle_functions import picklify
from pathlib import Path

#download the ISO codes
url_ISO = 'https://raw.githubusercontent.com/lukes/ISO-3166-Countries-with-Regional-Codes/master/all/all.csv'
ISO = pd.read_csv(url_ISO)

# Fix ISO codes dictionary
ISO = ISO[['name','alpha-3']].copy()
ISO.at[ISO['name'] == 'Bolivia (Plurinational State of)','name'] = "Bolivia"
ISO.at[ISO['name'] == 'Brunei Darussalam','name'] = "Brunei"
ISO.at[ISO['name'] == 'Cabo Verde','name'] = "Cape Verde"
ISO.at[ISO['name'] == 'Congo, Democratic Republic of the','name'] = "Democratic Republic of the Congo"
ISO.at[ISO['name'] == 'Congo','name'] = "Republic of Congo"
ISO.at[ISO['name'] == "Côte d'Ivoire",'name'] = "Cote d'Ivoire"
ISO.at[ISO['name'] == "Curaçao",'name'] = "Curacao"
ISO.at[ISO['name'] == "Czechia",'name'] = "Czech Republic"
ISO.at[ISO['name'] == "Eswatini",'name'] = "Swaziland"
ISO.at[ISO['name'] == "Falkland Islands (Malvinas)",'name'] = "Falkland Islands"
ISO.at[ISO['name'] == "Iran (Islamic Republic of)",'name'] = "Iran"
ISO.at[ISO['name'] == "Korea, Republic of",'name'] = "South Korea"
ISO.at[ISO['name'] == "Lao People's Democratic Republic",'name'] = "Laos"
ISO.at[ISO['name'] == "Virgin Islands (British)",'name'] = "British Virgin Islands"
ISO.at[ISO['name'] == "Timor-Leste",'name'] = "East Timor"
ISO.at[ISO['name'] == "Moldova, Republic of",'name'] = "Moldova"
ISO.at[ISO['name'] == "Palestine, State of",'name'] = "Palestine"
ISO.at[ISO['name'] == "Réunion",'name'] = "Reunion"
ISO.at[ISO['name'] == "Russian Federation",'name'] = "Russia"
ISO.at[ISO['name'] == "Saint Barthélemy",'name'] = "Saint Barthelemy"
ISO.at[ISO['name'] == "Sint Maarten (Dutch part)",'name'] = "Sint Maarten"
ISO.at[ISO['name'] == "Saint Martin (French part)",'name'] = "St Martin"
ISO.at[ISO['name'] == "Syrian Arab Republic",'name'] = "Syria"
ISO.at[ISO['name'] == "Taiwan, Province of China",'name'] = "Taiwan"
ISO.at[ISO['name'] == "Tanzania, United Republic of",'name'] = "Tanzania"
ISO.at[ISO['name'] == "United Kingdom of Great Britain and Northern Ireland",'name'] = "United Kingdom"
ISO.at[ISO['name'] == "Venezuela (Bolivarian Republic of)",'name'] = "Venezuela"
ISO.at[ISO['name'] ==  "Viet Nam",'name'] = "Vietnam"

#store in pickle files
picklify(ISO, 'ISO')
