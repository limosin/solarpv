import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from os import listdir
import json
import pvlib
from pvlib.pvsystem import PVSystem, retrieve_sam
from pvlib.location import Location
from pvlib.modelchain import ModelChain
from pvlib.atmosphere import gueymard94_pw

# Importing the dataset
Weather_data_path = '../data/weather/'
solar_data_path = '../data/solar/'

weather_file = [f for f in listdir(Weather_data_path) if f.endswith('.csv')]
solar_file = [f for f in listdir(solar_data_path) if (f.endswith('.csv'))]

weather_data = pd.read_csv(Weather_data_path+weather_file[0])
solar_data = pd.read_csv(solar_data_path + solar_file[0])

weather_data['Timestamp'] = pd.to_datetime(weather_data['Timestamp'].values,utc=True).tz_convert('Asia/Kolkata')
solar_data['Timestamp'] = pd.to_datetime(solar_data['Timestamp'].values, utc=True).tz_convert('Asia/Kolkata')
weather_data.index = weather_data['Timestamp']
solar_data.index = solar_data['Timestamp']
if 'Timestamp' in weather_data.columns:
    weather_data.drop('Timestamp', inplace=True, axis=1)
if 'Timestamp' in solar_data.columns:
    solar_data.drop('Timestamp', inplace=True, axis=1)

for col in weather_data.columns:
    if weather_data[col].isnull().sum() >0:
        weather_data[col].interpolate(method='time',axis=0, inplace=True)
if sum(weather_data.isnull().sum(axis=0)) == 0:
    print('All Null values removed')


weather_data['precipitable_water'] = gueymard94_pw(weather_data['temp_air'], weather_data['relative_humidity'])
# This row has relative humidity = 100, which is practically not possible
if len(weather_data.loc[weather_data['precipitable_water'] > 8, 'relative_humidity']) > 0:
    print('Invalid values in the relative humidity column \n Removing such values')
    weather_data.loc['2018-08-19 13:03:00+05:30','relative_humidity'] = 70
    weather_data['precipitable_water'] = gueymard94_pw(weather_data['temp_air'], weather_data['relative_humidity'])

with open('../data/config.json') as jsonfile:
    data = json.load(jsonfile)
    
lats, longs = data['lats'], data['longs']
tilt = data['tilt']
surf_azi = data['surf_azi'] #since panel faces south
altitude = data['altitude']
name = data['name']
timezone = data['timezone']
albedo = data['albedo']
mod_per_string = data['modules_per_string']
str_per_inv = data['strings_per_inverter']

try:
    panel_model = retrieve_sam('CECMod')
    panel_model = panel_model[data['module']]
except:
    try:
        panel_model = retrieve_sam('SandiaMod')
        panel_model = panel_model[data['module']]
    except:
        print('Module not found in the database!!')
try:    
    inverter_model = retrieve_sam('CECinverter')
    inverter_model = inverter_model[data['inverter']]
except:
    try:
        inverter_model = retrieve_sam('SandiaInverter')
        inverter_model = inverter_model[data['inverter']]
    except:
        print('Inverter model not found in the database!!')


def plot_results(output, save_fig=False, model='High-level'):
    
    # Power calculated from the power plant data
    Power_orig_ac = solar_data['Pac']
    Power_orig_dc = solar_data['Vpv1']*solar_data['Ipv1']
        
    Power_pred = output['i_sc']*output['v_oc']
    print('Maximum Predicted Power = ',Power_pred.max(axis=0),'\n')
    print('\nPower Plots\n')
    plt.figure(figsize=[10,6])
    plt.subplot(311)
    output.v_oc[0:1500].plot(grid=True, label='Predicted')
    solar_data.Vpv1[0:1500].plot(grid=True, label='Original')
    plt.title('Voltage')
    plt.legend()
    # plt.savefig(fname='predictions_voltage')
    
    plt.subplot(312)
    output.i_sc[0:1500].plot(grid=True, label='Predicted')
    solar_data.Ipv1[0:1500].plot(grid=True, label='Original')
    plt.title('Current')
    plt.legend()
    # plt.savefig(fname='predictions_current')
    
    plt.subplot(313)
    Power_pred[0:1500].plot(grid=True, label='Predicted_dc')
    Power_orig_dc[0:1500].plot(grid=True, label='Original_dc')
    Power_orig_ac[0:1500].plot(grid=True, label='Original_ac')
    plt.title('Power')
    plt.legend()
    # plt.savefig(fname='predictions_power')
    plt.show()
    print('\n\nDistribution of Values\n')
    Power_pred.hist(figsize = [10,3],bins=20)


# Using the high level API

location = Location(latitude=lats, longitude=longs, altitude=altitude)
system = PVSystem(surface_tilt = tilt, surface_azimuth=surf_azi, albedo=albedo, 
                  module_parameters=panel_model, inverter_parameters=inverter_model,
                 modules_per_string=mod_per_string, strings_per_inverter=str_per_inv, name=name)
mc = ModelChain(system, location, aoi_model='no_loss', name=name+'_ModelChain')
mc.run_model(times = weather_data.index, weather = weather_data)
output_hl = mc.dc
plot_results(output_hl)


times = weather_data.index
solpos = pvlib.solarposition.get_solarposition(times, lats, longs)
solpos['azimuth'] = weather_data['azimuth']
dni_extra = pvlib.irradiance.get_extra_radiation(times)
airmass = pvlib.atmosphere.get_relative_airmass(solpos['apparent_zenith'])
pressure = pvlib.atmosphere.alt2pres(altitude)
am_abs = pvlib.atmosphere.get_absolute_airmass(airmass, pressure)
tl = pvlib.clearsky.lookup_linke_turbidity(times, lats, longs)
cs = pvlib.clearsky.ineichen(solpos['apparent_zenith'], am_abs, tl,
                             dni_extra=dni_extra, altitude=altitude)
aoi = pvlib.irradiance.aoi(tilt, surf_azi, solpos['apparent_zenith'], solpos['azimuth'])
total_irrad = pvlib.irradiance.get_total_irradiance(tilt, surf_azi,
                                                    solpos['apparent_zenith'], solpos['azimuth'],
                                                    cs['dni'], cs['ghi'], cs['dhi'],
                                                    dni_extra=dni_extra, model='haydavies')
spectral_modifier = system.first_solar_spectral_loss(weather_data['precipitable_water'], airmass.values)
fd = 1
aoi_modifier = system.ashraeiam(aoi.values)
effective_irradiance = spectral_modifier*(total_irrad['poa_direct']*aoi_modifier+fd*total_irrad['poa_diffuse'])
temps = system.sapm_celltemp(total_irrad['poa_global'], weather_data['wind_speed'], weather_data['temp_air'])
effective_irradiance = weather_data['dni']
(photocurrent, saturation_current, resistance_series,resistance_shunt, nNsVth) = system.calcparams_cec(effective_irradiance,
                                       temps['temp_cell'])
diode_params = (photocurrent, saturation_current,resistance_series,resistance_shunt, nNsVth)
output_fl = system.singlediode(photocurrent, saturation_current, resistance_series,resistance_shunt, nNsVth)
output_fl = system.scale_voltage_current_power(output_fl)

plot_results(output_fl, False, 'Function_level')