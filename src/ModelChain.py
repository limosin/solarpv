import pandas as pd
import numpy as np
# pvlib imports
import pvlib
from pvlib.pvsystem import PVSystem
from pvlib.location import Location
from pvlib.modelchain import ModelChain

'''
Objective : Get the dc output from the modules

Notes:

Steps:
1. 

'''

# load some module and inverter specifications
cec_modules = pvlib.pvsystem.retrieve_sam('CECMod')
sandia_modules = pvlib.pvsystem.retrieve_sam('SandiaMod')
cec_inverters = pvlib.pvsystem.retrieve_sam('CECInverter')
cec_module = cec_modules['Vikram_Solar_Eldora_VSP_72_315_03']
cec_inverter = cec_inverters['ABB__MICRO_0_25_I_OUTD_US_208_208V__CEC_2014_']
sandia_module = sandia_modules['Canadian_Solar_CS5P_220M___2009_']


# Importing the plant configuration from the site_config.csv
site_config = pd.read_csv('../site_config.csv')

# location = Location(site_config.Latitude[0],site_config.Longitude[0],
# 							site_config.Timezone[0],site_config.Elev[0], 'Narnaul')
location = Location(latitude=26, longitude=76)
system = PVSystem(surface_tilt=20, surface_azimuth=0, module_parameters=sandia_module,
                  inverter_parameters=cec_inverter)

mc = ModelChain(system, location)

# Importing the weather data
weather = pd.read_csv('../Narnaul_site/data/weather_data/selected_data.csv', index_col='Timestamp')

weather.index = pd.to_datetime(weather.index.values)
weather.index = weather.index.tz_localize('Asia/Kolkata')
mc.run_model(times=weather.index, weather=weather)
print(mc.dc)
