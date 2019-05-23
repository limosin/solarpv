# Importing the libraries
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import argparse
import os

if not os.path.exists('../data/weather'):
    os.makedirs('../data/weather')

if not os.path.exists('../data/solar'):
    os.makedirs('../data/solar')


Weather_data_path = '../data/weather/'

Weather_params = pd.read_csv('../data/Parameters.csv',names={1,2,3})
Weather_params.columns = ['Code', 'Quantity', 'Unit']
Weather_params = Weather_params[0:-3]

Weather_params.drop('Unit', axis=1,inplace=True)

#Constructing a dictionary out of these two columns
Param_dict = dict(zip(Weather_params['Code'].values, Weather_params['Quantity'].values))
keys_of_param_dict = [n for n in Param_dict.keys()]
columns_list = list(Weather_params.Quantity.values)
columns_list.insert(0,'Timestamp')

#parse the arguments
parser = argparse.ArgumentParser()
parser.add_argument('data', help='Input Weather data file name without .csv',default='null')
args=parser.parse_args()

if args.data=='null':
    print('Invalid file name entered!! \n Exiting..')
else:
    try:
        weather_data = pd.read_csv('../'+args.data+'.csv',usecols=['Timestamp', 'ParameterNumber','ParameterValue'])
        weather_data.columns = ['Timestamp', 'Parameter', 'Value']
        datetime = weather_data.Timestamp.unique()

        new_df = pd.DataFrame(columns=columns_list)
        new_df['Timestamp'] = datetime
        new_df.index = datetime
        new_df.drop('Timestamp', axis=1, inplace=True)

        total_params = len(columns_list)-1
        i=0
        print('\n\nProcessing the data...\n\n\n')
        print('Ignore warnings if any..')
        for Para in Param_dict.keys():
            mini_df = weather_data[weather_data['Parameter']==Para]
            mini_df.drop('Parameter', axis=1, inplace=True)
            new_df.loc[mini_df.Timestamp.values, Param_dict[Para]] = mini_df.Value.values
            i=i+1
            print('Completetd '+str(int(i/total_params*100))+'% of processing')

        print('Renaming columns.....')
        name_dict = {'Timestamp':'Timestamp', 
                     'Relative Humidity': 'relative_humidity',
                     'Air Temperature': 'temp_air',
                     'Wind Speed': 'wind_speed',
                     'Dew Point': 'dew_point',
                     'Global Radiation 1':'ghi',
                     'Diffuse Radiation': 'dhi',
                     'Atmospheric Pressure QNH':'atm_qnh',
                     'Atmospheric Pressure QFE':'atm_qfe',
                     'Direct Radiation 1':'dni',
                     'Solar Azimuth':'azimuth',
                     'Global Energy 1':'global_E',
                     'Diffuse Energy 1':'Diffuse_E',
                     'Direct Energy 1':'Direct_E'}

        new_df.rename(columns=name_dict, inplace=True)
        new_df.reset_index(inplace=True)
        new_df.rename(columns={'index':'Timestamp'}, inplace=True)
        print('\nPrinting the First 5 rows..\n')
        print(new_df.head())

        if os.path.exists(Weather_data_path+args.data+'.csv'):
            os.remove(Weather_data_path+args.data+'.csv')

        new_df.to_csv(Weather_data_path+args.data+'.csv',index=False)
        print('\nData Exported to '+Weather_data_path+args.data+'.csv')
        print('You can remove the original file if you wish to')
    except:
        print('File not found, please check the name or if the file exists in the desired location')

