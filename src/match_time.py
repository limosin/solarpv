print('Importing Libraries....')
from pandas import read_csv, read_excel,to_datetime, DatetimeIndex
from os import listdir, remove
print('Done')


def approximate(x):
    return x[:-4]+'00'

if __name__ == '__main__':

    print('\n\nThis script takes only the rows which are common in both weather data and solar data')
    print('And also localizes the timestamps of both the dataframe..\n\n')
    solar_data_path = '../data/solar/'
    Weather_data_path = '../data/weather/'
    
    weather_file = [f for f in listdir(Weather_data_path) if f.endswith('.csv')]
    solar_file = [f for f in listdir(solar_data_path) if (f.endswith('.csv') or f.endswith('.xlsx'))]
    print('Reading the solar data..\n')
    f = solar_file[0]
    if f.endswith('.xlsx'):
        solar_data = read_excel(solar_data_path+f)
    else:
        solar_data = read_csv(solar_data_path+f)
    solar_data.rename(columns={'Time':'Timestamp'}, inplace=True)
    solar_data['Timestamp'] = solar_data.Timestamp.apply(lambda x : approximate(x))

    print('Reading the Weather data..')
    weather_data = read_csv(Weather_data_path+weather_file[0])

    print('Localizing.......\n')
    try:
        solar_data['Timestamp'] = to_datetime(solar_data['Timestamp']).dt.tz_localize('Asia/Kolkata')
        remove(solar_data_path+f)
        print('Replacing with the new files..\n\n')
        solar_data.to_csv(solar_data_path+f.split('.')[0]+'.csv', index=False)
    except:
        print('Solar data already localized')
    try:
        weather_data['Timestamp'] = to_datetime(weather_data['Timestamp']).dt.tz_localize('Asia/Kolkata')
        print('Segmenting the Weather Data....')
        weather_data = weather_data.loc[weather_data['Timestamp'].isin(solar_data['Timestamp'])]
        remove(Weather_data_path+weather_file[0])
        weather_data.to_csv(Weather_data_path+weather_file[0], index=False)

    except:
        print('Weather data already localized')
