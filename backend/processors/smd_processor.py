import pandas as pd
from sqlalchemy import text
import math

def calculate_pe_from_obs(row): # Pressure, humidity, dew_point Data X 
  
    t_max = row['max_temp']
    t_min = row['min_temp']
    t_mean = (t_max + t_min) / 2
    rad_mj = row['glorad'] / 100.0  # J/cm2 -> MJ/m2
    wind_ms = max(0, row['wdsp'] * 0.514)   # Knot -> m/s
    
    es_tmax = 0.6108 * math.exp((17.27 * t_max) / (t_max + 237.3))
    es_tmin = 0.6108 * math.exp((17.27 * t_min) / (t_min + 237.3))
    es = (es_tmax + es_tmin) / 2
    
    # 2. dew_point = tmin 
    dew_point = t_min - 1.5
    ea = 0.6108 * math.exp((17.27 * dew_point) / (dew_point + 237.3)) 
    vpd = max(0, es - ea)
    
    # pressure = 101.3kPa 
    es_mean = 0.6108 * math.exp((17.27 * t_mean) / (t_mean + 237.3))
    delta = (4098 * es_mean) / ((t_mean + 237.3) ** 2)
    gamma = 0.067 
    
    rn = 0.75 * rad_mj
    wind_factor = 1 + 0.34 * wind_ms
    num = (0.408 * delta * rn) + (gamma * (900 / (t_mean + 273)) * wind_ms * vpd)
    den = delta + (gamma * wind_factor)
    
    return max(0.0, num / den)

def calculate_pe_forecast(mean_temp, max_temp, min_temp, wind_speed, pressure, humidity, total_rad_mj):

    wind_speed_ms = max(0, wind_speed * 0.5144)
    rn = 0.75 * total_rad_mj

    es_tmax = 0.6108 * math.exp((17.27 * max_temp) / (max_temp + 237.3))
    es_tmin = 0.6108 * math.exp((17.27 * min_temp) / (min_temp + 237.3))
    es = (es_tmax + es_tmin) / 2

    ea = es * (max(0, min(100, humidity)) / 100.0) 

    vpd = max(0, es - ea) 

    es_mean = 0.6108 * math.exp((17.27 * mean_temp) / (mean_temp + 237.3))
    delta = (4098 * es_mean) / ((mean_temp + 237.3) ** 2)

    pressure_kpa = pressure / 10
    gamma = 0.000665 * pressure_kpa
    
    wind_factor = 1 + 0.34 * max(0, wind_speed_ms)

    num = (0.408 * delta * rn) + (gamma * (900 / (mean_temp + 273)) * wind_speed_ms * vpd)
    den = delta + (gamma * wind_factor)
        
    pe = num / den
        
    return max(0.0, round(pe, 2))


def calculated_smd(yesterday_smd, pe, rain, soil_type):
    smd_max = 110.0

    if soil_type == 'well':
        smd_min = 0.0
        smd_c = 0.0
    
    elif soil_type == 'moderately':
        smd_min = -10.0
        smd_c = 0.0
    
    elif soil_type == 'poorly':
        smd_min = -10.0
        smd_c = 10.0
    
    else:
        smd_min, smd_c = 0.0, 0.0

    if yesterday_smd <= smd_c:
        ae = pe
    else:
        ae = pe * ((smd_max - yesterday_smd) / (smd_max - smd_c))
    ae = max(ae, 0)

    temp_smd = yesterday_smd - rain + ae

    drain = 0.0

    if temp_smd < 0:
        if soil_type == 'well':
            drain = -temp_smd
        elif soil_type == 'moderately':
            drain = min(-temp_smd,10)
        elif soil_type == 'poorly':
            if temp_smd < -10:
                drain = 0.5
            else:
                drain = 0.5 * ((-temp_smd) / 10.0)

    current_smd = temp_smd + drain

    current_smd = max(smd_min, min(smd_max, current_smd))

    return round(ae, 2), round(current_smd, 2), round(drain, 2)