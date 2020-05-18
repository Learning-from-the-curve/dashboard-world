import numpy as np
import pandas as pd

def center_date(row, max_MA_index, country):
    '''
    function used for an apply method
    input: 
    row of a dataframe
    date of the max Moving Average
    country 
    output:
    updated row with the difference of # of days in place of the date
    '''
    final_string = ''
    temp_string = str(row['index']-max_MA_index)

    for char in temp_string:
        if char == '-' or char.isdigit():
            final_string += char
        else:
            break
    row[country] = final_string
    return row


def adjust_names(data):
    '''
    Adjust countries' names. Still problems with most French overseas territories and Channel Islands
    input:
    dataframe containing the information for each country for each date
    output:
    updated dataframe with correct country names
    '''
    data['Country/Region'].loc[data['Country/Region'] == 'Burma'] = 'Myanmar'
    data['Country/Region'].loc[data['Country/Region'] == 'Cabo Verde'] = 'Cape Verde'
    data['Country/Region'].loc[data['Country/Region'] == 'Congo (Brazzaville)'] = 'Republic of Congo'
    data['Country/Region'].loc[data['Country/Region'] == 'Congo (Kinshasa)'] = 'Democratic Republic of the Congo'
    data['Country/Region'].loc[data['Country/Region'] == 'Czechia'] = 'Czech Republic'
    data['Country/Region'].loc[data['Country/Region'] == 'Eswatini'] = 'Swaziland'
    data['Country/Region'].loc[data['Country/Region'] == 'Korea, South'] = 'South Korea'
    data['Country/Region'].loc[data['Country/Region'] == 'Taiwan*'] = 'Taiwan'
    data['Country/Region'].loc[data['Country/Region'] == 'Timor-Leste'] = 'East Timor'
    data['Country/Region'].loc[data['Country/Region'] == 'US'] = 'United States of America'
    data['Country/Region'].loc[data['Country/Region'] == 'West Bank and Gaza'] = 'Palestine'
    data['Province/State'].loc[data['Province/State'] == 'Falkland Islands (Malvinas)'] = 'Falkland Islands'
    return data

def aggregate_countries(data, graph):
    '''
    input:
    dataframe containing the information for each country for each date
    string with the type of graph (scatter, map)
    output:
    updated dataframe with aggregated provinces and states in a country
    '''
    # For countries that have disaggregated data sum them
    if graph == "map":
        data = data.set_index('Country/Region')
        data['Confirmed'] = data.groupby(level = 0)['Confirmed'].sum()
        data['Deaths'] = data.groupby(level = 0)['Deaths'].sum()
    else:
        data['Country/Region'][(data['Country/Region'] == 'France') & (data['Province/State'].isna() == False)] = data['Province/State']
        data['Country/Region'][(data['Country/Region'] == 'United Kingdom') & (data['Province/State'].isna() == False)] = data['Province/State']
        data['Country/Region'][(data['Country/Region'] == 'Netherlands') & (data['Province/State'].isna() == False)] = data['Province/State']
        data['Country/Region'][(data['Country/Region'] == 'Denmark') & (data['Province/State'].isna() == False)] = data['Province/State']
        data = data.set_index('Country/Region')
        data = data.groupby(level = 0).sum()
    data = data.groupby(level = 0).first()
    data = data.reset_index()
    return data

def moving_average(data, window):
    '''
    input:
    dataframe containing the information for each country for each date
    # of days
    output:
    dataframe with Moving Average for each country for each date
    dataframe with difference of # of days from the date of the max, for each country for each date
    '''
    df_sub = data.copy()
    df_sub = df_sub.apply(lambda x: x - x.shift(periods = 1))
    df_sub.iloc[0] = data.iloc[0]
    df_MA = df_sub.copy()
    for country in list(df_MA):
        if data[country].iloc[-1] != 0:
            df_MA[country] = (df_MA[country]/data[country].iloc[-1])*100
            df_MA[country] = df_MA[country].astype('float64').apply(np.log)
            df_MA[country] = df_MA[country].rolling(window).mean()
        else:
            df_MA[country] = np.nan
    df_centered_date = df_MA.copy()
    for country in list(df_centered_date):
        if not np.isnan(df_centered_date[country].max()):
            df_temp = df_centered_date.copy()
            max_MA_index = df_temp.loc[df_temp[country] == df_temp[country].max()].index.tolist()[0]
            df_temp.loc[max_MA_index, [country]] = 0.0
            df_temp = df_temp.reset_index()
            df_temp = df_temp[[country, 'index']].apply(center_date, args = (max_MA_index, country), axis = 1)
            df_temp = df_temp.set_index('index')
            df_centered_date[country] = df_temp[country].copy()
    return df_MA, df_centered_date