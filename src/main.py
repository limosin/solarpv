'''
Author : Somil Singhai

@inputs :  Plant attributes -> location, no. of modules, strings,etc
			Inverter details, Module details

@output : Predicted output

'''

# importing the basic libraries
import numpy as np
import pandas as pd
import os
import datetime

# pvlib and auxillaries
from pvlib.location import Location
from pvlib.solarposition import get_solarposition
from pvlib import clearsky
from pvlib.atmosphere import get_relative_airmass
from pvlib.irradiance import get_extra_radiation
from pvlib import clearsky
from pvlib.irradiance import get_ground_diffuse
from pvlib.irradiance import get_sky_diffuse
#_____________________________________________________________________________________________#

# Function to construct location object


def construct_location_object(latid, longit, tz, elev, name):
    '''

    @input : latitude, longitude, elevation, tz, name
    @output : A dictionary containing all the above things

    '''

    return Location(latitude=latid, longitude=longit, tz=tz, altitude=elev, name=name)

#______________________________________________________________________________________________#

# Function to get the solarposition using pyephem method


def _get_solarposition(times, location, method='pyephem'):
    '''
    @input : time dataframe, location object, the method to be used
    @output : a Dataframe contatining -> 1. Apparent_Elevation
                                                                             2. Apparent_Azimuth
                                                                             3. Elevation
                                                                             4. Azimuth
                                                                             5. Apparent_Zenith
                                                                             6. Zenith
    '''
    return location.get_solarposition(times=times, method=method)


#_______________________________________________________________________________________________#

# Function to get the relative air mass
def _get_relative_airmass(zenith, model='pickering2002'):
    '''
    @input : zenith/ apparent zenith from solar_position_df
    @output : relative airmass dataframe
    @models : 'simple', 'kasten19666', 'youngirvine1967', 'kastenyoung1989', 
                      'young1994', 'pickering2002'
    '''

    return get_relative_airmass(zenith, model=model)


#_______________________________________________________________________________________________#

# Function to get Extraterrestrial Radiation
def _get_extrat_radiation(times, method='spencer'):
    '''
    @input : times, solar_constant, method
    @ouptut : pandas timeseries with extrat radiation in watts per square meter
    @method : ['pyephem', 'spencer', 'nrel', 'asce'] 

    '''

    return get_extra_radiation(times, method=method)


#_______________________________________________________________________________________________#

# Function to get clear_sky
def _get_clear_sky(times, location, model='ineichen'):
    '''
    @input : apparent_zenith, airmass_abs, linke_tubidity, elevation, extrat_radiation
    @output: Dataframe containing - dhi(direct horizo irra), dni(direct normal irra), ghi

    '''

    return location.get_clearsky(times, model=model)


#_______________________________________________________________________________________________#

# Function to calculate the diffusion through ground
def _get_ground_diffusion(surf_tilt, ghi, albedo=0.25, surface_type=None):
    '''
    @input : surface_tilt, ghi, albedo/surface type
    @output : Ground reflected irradiances in W/m^2.

    '''

    return get_ground_diffuse(surf_tilt, ghi, albedo, surface_type)

#_______________________________________________________________________________________________#


# Function to calculate the diffusion by sky
def _get_sky_diffusion(surf_tilt, surf_az, solar_zenith, solar_azimuth, dni, ghi, dhi, extrat, airmass, model):
    '''
    @input : surface_tilt, ghi,dni,dhi,surface_azimuth, solar_zenith, solar_azimuth, airmass, model
    @output : sky reflected irradiances in W/m^2.

    '''

    return get_sky_diffuse(surf_tilt, surf_az, solar_zenith, solar_azimuth, dni, ghi, dhi,
                           dni_extra=extrat, airmass=airmass, model=model)

#_______________________________________________________________________________________________#


def main():

    # Importing the plant configuration from the site_config.csv
    site_config = pd.read_csv('../site_config.csv')

    # Importing the solardata
    solardata = data = pd.read_csv('../Narnaul_site/data/solar_data/inverter_data_final.csv')

    times = pd.to_datetime([time for time in solardata['Timestamp']])

    # Constructing a location object
    location = construct_location_object(site_config.Latitude[0], site_config.Longitude[0],
                                         site_config.Timezone[0], site_config.Elev[0], 'Narnaul')

    # Getting the solarposition using _get_solarposition function
    # There are many methods availabel such as pyephem, nrel_numpy, ephemeris, etc
    solar_position_df = _get_solarposition(times, location, 'pyephem')

    # Calculating the relative airmass
    rela_airmass = _get_relative_airmass(solar_position_df['apparent_zenith'], 'pickering2002')

    # Calculating the extraterrestrial Radiation
    extrat = _get_extrat_radiation(times, 'spencer')

    # Calculating ghi, dni and dhi
    Irradiance_df = _get_clear_sky(times, location, 'ineichen')

    # Calculating the ground diffusion
    # * I need to have surf_tilt for this, currently it is zero
    # * Also the surface type is required too
    ground_diffuse_df = _get_ground_diffusion(0, Irradiance_df['ghi'], 0.25, 'sand')

    # Calculating the sky diffusion
    surf_tilt = 40
    surf_az = 0
    sky_diffuse_df = _get_sky_diffusion(surf_tilt, surf_az, solar_position_df['zenith'], solar_position_df['azimuth'],
                                        Irradiance_df['dni'], Irradiance_df['ghi'], Irradiance_df['dhi'], extrat, rela_airmass, 'perez')


if __name__ == '__main__':
    main()
