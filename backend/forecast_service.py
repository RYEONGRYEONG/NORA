import pandas as pd
import xmltodict
import requests
from datetime import datetime
from sqlalchemy import text

def update_farm_forecast(farm_id, lat, lon, conn):
    # Met Éireann API
    endpoint = f"http://openaccess.pf.api.met.ie/metno-wdb2ts/locationforecast?lat={lat};long={lon}"
    r = requests.get(endpoint)
    data = xmltodict.parse(r.text)
    
    merged_forecasts = {}
    
    for entry in data['weatherdata']['product']['time']:
        raw_time = entry['@to']
        time_key = raw_time.replace('T', ' ').replace('Z', '')
        location = entry.get('location', {})

        if time_key not in merged_forecasts:
            merged_forecasts[time_key] = {'forecast_time': time_key, 'farm_id': farm_id}
        
        # 기온 및 바람 등 정보 업데이트
        if 'temperature' in location:
            merged_forecasts[time_key].update({
                'temp': location['temperature'].get('@value'),
                'wind_speed': location['windSpeed'].get("@mps"),
                'wind_gust': location['windGust'].get('@mps'),  
                'wind_dir': location['windDirection'].get('@deg'),   
                'humidity': location['humidity'].get('@value'),
                'pressure': location['pressure'].get('@value'),
                'dew_point': location['dewpointTemperature'].get('@value'), 
                'global_rad': location['globalRadiation'].get('@value')     
            })

    
        if 'precipitation' in location:
            merged_forecasts[time_key].update({
                'precip': location['precipitation'].get('@value'),
                'symbol_id': location.get('symbol', {}).get('@id')
            })

    
    db_data = []
    for val in merged_forecasts.values():
        db_data.append({
            "farm_id": farm_id,
            "time": val['forecast_time'],
            "temp": val.get('temp'),
            "precip": val.get('humidity'),
            "wind_speed": val.get('wind_speed'),
            "wind_gust": val.get('wind_dir'),
            "wind_dir": val.get('wind_dir'),
            "humidity": val.get('humidity'),
            "dew": val.get('dew_point'),
            "press": val.get('pressure'),
            "rad": val.get('global_rad'),
            "sym": val.get('symbol_id')
        })
      
    try:
        query = text("""
                     insert into forecast (farm_id, forecast_time, temp, precip, humidity, wind_speed, wind_gust, wind_dir, dew_point, pressure, global_rad, symbol_id)
                     values (:farm_id, :time, :temp, :precip, :humidity, :wind_speed, :wind_gust, :wind_dir, :dew, :press, :rad, :sym)
                     on duplicate key update
                     temp = values(temp), precip = values(precip) humidity = values(humidity), wind_speed = values(wind_speed), wind_gust = values(wind_gust),
                     wind_dir = values(wind_dir), dew_point = values(dew_point), pressure = values(pressure), global_rad = values(global_rad), symbol_id = values(symbol_id)
                     """)
        
        conn.execute(query, db_data)

        print(f"{farm_id} forecast updated successfully")
    except Exception as e:
        conn.rollback()
        print(f"error: {e}")
        raise e

    df_hourly = pd.DataFrame(list(merged_forecasts.values()))
    df_hourly['forecast_time'] = pd.to_datetime(df_hourly['forecast_time'])
    
    
    for col in ['temp', 'precip', 'wind_speed', 'global_rad', 'pressure', 'humidity']:
        df_hourly[col] = pd.to_numeric(df_hourly[col], errors='coerce').fillna(0)

    
    df_daily = df_hourly.resample('D', on='forecast_time').agg({
        'temp': ['mean', 'max', 'min'],
        'pressure': 'mean',
        'precip': 'sum',
        'wind_speed': 'mean',
        'humidity': 'mean',
        'global_rad': 'sum'
    }).dropna()
    
    df_daily.columns = ['mean_temp', 'max_temp', 'min_temp',  'wind_speed', 'pressure', 'humidity' , 'total_rad', 'rain']
    return df_daily