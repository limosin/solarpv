import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import pandas as pd
from os import listdir
import json
import pvlib
from pvlib.pvsystem import PVSystem, retrieve_sam
from pvlib.location import Location
from pvlib.modelchain import ModelChain
from pvlib.atmosphere import gueymard94_pw

# times = weather_data.index
# solpos = pvlib.solarposition.get_solarposition(times, lats, longs)
# solpos['azimuth'] = weather_data['azimuth']
# dni_extra = pvlib.irradiance.get_extra_radiation(times)
# airmass = pvlib.atmosphere.get_relative_airmass(solpos['apparent_zenith'])
# pressure = pvlib.atmosphere.alt2pres(altitude)
# am_abs = pvlib.atmosphere.get_absolute_airmass(airmass, pressure)
# tl = pvlib.clearsky.lookup_linke_turbidity(times, lats, longs)
# cs = pvlib.clearsky.ineichen(solpos['apparent_zenith'], am_abs, tl,
#                              dni_extra=dni_extra, altitude=altitude)
# aoi = pvlib.irradiance.aoi(tilt, surf_azi, solpos['apparent_zenith'], solpos['azimuth'])
# total_irrad = pvlib.irradiance.get_total_irradiance(tilt, surf_azi,
#                                                     solpos['apparent_zenith'], solpos['azimuth'],
#                                                     cs['dni'], cs['ghi'], cs['dhi'],
#                                                     dni_extra=dni_extra, model='haydavies')
# spectral_modifier = system.first_solar_spectral_loss(weather_data['precipitable_water'], airmass.values)
# fd = 1
# aoi_modifier = system.ashraeiam(aoi.values)
# effective_irradiance = spectral_modifier*(total_irrad['poa_direct']*aoi_modifier+fd*total_irrad['poa_diffuse'])
# temps = system.sapm_celltemp(total_irrad['poa_global'], weather_data['wind_speed'], weather_data['temp_air'])
# effective_irradiance = weather_data['dni']
# (photocurrent, saturation_current, resistance_series,resistance_shunt, nNsVth) = system.calcparams_cec(effective_irradiance,
#                                        temps['temp_cell'])
# diode_params = (photocurrent, saturation_current,resistance_series,resistance_shunt, nNsVth)
# output_fl = system.singlediode(photocurrent, saturation_current, resistance_series,resistance_shunt, nNsVth)
# output_fl = system.scale_voltage_current_power(output_fl)
# plot_results(output_fl, False, 'Function_level')

class Model():

    def __init__(self):
        self.weather_file = None
        self.solar_file = None
        self.data = None
        self.output = 0
        self.weather_data = None
        self.solar_data = None
    
    def weather_file_setter(self, filepath):
        self.weather_file = filepath
        try:
            self.weather_data = pd.read_csv(self.weather_file)
            self.weather_data['Timestamp'] = pd.to_datetime(self.weather_data['Timestamp'].values, \
                                                            utc=True).tz_convert('Asia/Kolkata')
            self.weather_data.index = self.weather_data['Timestamp']                                                        
            return True
        except:
            return False

    def solar_file_setter(self, filepath):
        self.solar_file = filepath
        try:
            self.solar_data = pd.read_csv(self.solar_file)
            self.solar_data['Timestamp'] = pd.to_datetime(self.solar_data['Timestamp'].values, \
                                                        utc=True).tz_convert('Asia/Kolkata')
            self.solar_data.index = self.solar_data['Timestamp']   
            return True
        except:
            return False

    def data_setter(self, data):
        self.lats = data['lats']
        self.longs = data['longs']
        self.tilt = data['tilt']
        self.surf_azi = data['surf_azi'] #since panel faces south
        self.altitude = data['altitude']
        self.name = data['name']
        self.timezone = data['timezone']
        self.albedo = data['albedo']
        self.mod_per_string = data['modules_per_string']
        self.str_per_inv = data['strings_per_inverter']

        try:
            self.panel_model = retrieve_sam('CECMod')
            self.panel_model = self.panel_model[data['module']]
        except:
            try:
                self.panel_model = retrieve_sam('SandiaMod')
                self.panel_model = self.panel_model[data['module']]
            except:
                return False, str('Module not found in the database!!')
        try:    
            self.inverter_model = retrieve_sam('CECinverter')
            self.inverter_model = self.inverter_model[data['inverter']]
        except:
            try:
                self.inverter_model = retrieve_sam('SandiaInverter')
                self.inverter_model = self.inverter_model[data['inverter']]
            except:
                return False, str('Inverter model not found in the database!!')
        
        return True, str('Pass')
        
    def preprocess(self):
        
        if self.timezone != 'Asia/Kolkata':
            self.weather_data['Timestamp'] = pd.to_datetime(self.weather_data['Timestamp'].values, \
                                                            utc=True).tz_convert(self.timezone)
            self.solar_data['Timestamp'] = pd.to_datetime(self.solar_data['Timestamp'].values, \
                                                        utc=True).tz_convert(self.timezone)
        
        if 'Timestamp' in self.weather_data.columns:
            self.weather_data.drop('Timestamp', inplace=True, axis=1)
        if 'Timestamp' in self.solar_data.columns:
            self.solar_data.drop('Timestamp', inplace=True, axis=1) 

        for col in self.weather_data.columns:
            if self.weather_data[col].isnull().sum() >0:
                self.weather_data[col].interpolate(method='time',axis=0, inplace=True)
            # if sum(self.weather_data.isnull().sum(axis=0)) == 0:
            #     print('All Null values removed')  

        self.weather_data['precipitable_water'] = gueymard94_pw(self.weather_data['temp_air'],\
                                                            self.weather_data['relative_humidity'])

        # This row has relative humidity = 100, which is practically not possible
        if len(self.weather_data.loc[self.weather_data['precipitable_water'] > 8, 'relative_humidity']) > 0:
            print('Invalid values in the relative humidity column \n Removing such values')
            self.weather_data.loc['2018-08-19 13:03:00+05:30','relative_humidity'] = 70
            self.weather_data['precipitable_water'] = gueymard94_pw(self.weather_data['temp_air'], self.weather_data['relative_humidity'])

    def export_fig(self, output):
        Power_orig_ac = self.solar_data['Pac']
        Power_orig_dc = self.solar_data['Vpv1']*self.solar_data['Ipv1']
        Power_pred = output['i_sc']*output['v_oc']

        print('Maximum Predicted Power = ',Power_pred.max(axis=0),'\n')

        fig_voltage = plt.figure(figsize=[5,4])
        ax_voltage = fig_voltage.add_subplot(111, title='Current Plot')
        output.v_oc.plot(grid=True, label='Predicted', ax=ax_voltage)
        self.solar_data.Vpv1.plot(grid=True, label='Original', ax=ax_voltage)

        fig_current = plt.figure(figsize=[5,4])
        ax_current = fig_current.add_subplot(111, title='Current Plot')
        output.i_sc.plot(grid=True, label='Predicted', ax=ax_current)
        self.solar_data.Ipv1.plot(grid=True, label='Original', ax=ax_current)

        fig_power = plt.figure(figsize=[5,4])
        ax_power = fig_power.add_subplot(111, title='Current Plot')
        Power_pred.plot(grid=True, label='Predicted_dc', ax=ax_power)
        Power_orig_dc.plot(grid=True, label='Original_dc', ax=ax_power)
        Power_orig_ac.plot(grid=True, label='Original_ac', ax=ax_power)

        return fig_voltage, fig_current, fig_power

    def plot_results(self, output, save_fig=False, model='High-level'):
        # Power calculated from the power plant data
        Power_orig_ac = self.solar_data['Pac']
        Power_orig_dc = self.solar_data['Vpv1']*self.solar_data['Ipv1']
            
        Power_pred = output['i_sc']*output['v_oc']
        print('Maximum Predicted Power = ',Power_pred.max(axis=0),'\n')
        print('\nPower Plots\n')
        plt.figure(figsize=[10,6])
        plt.subplot(311)
        output.v_oc[0:1500].plot(grid=True, label='Predicted')
        self.solar_data.Vpv1[0:1500].plot(grid=True, label='Original')
        plt.title('Voltage')
        plt.legend()
        
        plt.subplot(312)
        output.i_sc[0:1500].plot(grid=True, label='Predicted')
        self.solar_data.Ipv1[0:1500].plot(grid=True, label='Original')
        plt.title('Current')
        plt.legend()
        
        plt.subplot(313)
        Power_pred[0:1500].plot(grid=True, label='Predicted_dc')
        Power_orig_dc[0:1500].plot(grid=True, label='Original_dc')
        Power_orig_ac[0:1500].plot(grid=True, label='Original_ac')
        plt.title('Power')
        plt.legend()
        plt.show()

        if  save_fig:
            plt.savefig(fname='predictions_current')
            plt.savefig(fname='predictions_voltage')
            plt.savefig(fname='predictions_power')

        print('\n\nDistribution of Values\n')
        Power_pred.hist(figsize = [10,3],bins=20)

    def run_api(self):
        # Using the high level API

        self.preprocess()

        self.location = Location(latitude=self.lats, longitude=self.longs, altitude=self.altitude)
        self.system = PVSystem(surface_tilt = self.tilt, surface_azimuth=self.surf_azi, albedo=self.albedo, 
                        module_parameters=self.panel_model, inverter_parameters=self.inverter_model,
                        modules_per_string=self.mod_per_string, strings_per_inverter=self.str_per_inv, name=self.name)
        self.mc = ModelChain(self.system, self.location, aoi_model='no_loss', name=self.name+'_ModelChain')
        self.mc.run_model(times = self.weather_data.index, weather = self.weather_data)
        self.output = self.mc.dc

if __name__ == '__main__':

    Weather_data_path = '../data/weather/'
    solar_data_path = '../data/solar/'

    weather_file = [f for f in listdir(Weather_data_path) if f.endswith('.csv')]
    solar_file = [f for f in listdir(solar_data_path) if (f.endswith('.csv'))]

    
    with open('../data/config.json') as jsonfile:
        data = json.load(jsonfile)
    model = Model()
    model.weather_file_setter(Weather_data_path + weather_file[0])
    model.solar_file_setter( solar_data_path + solar_file[0])
    model.data_setter(data)
    model.run_api()
    model.plot_results(model.output)