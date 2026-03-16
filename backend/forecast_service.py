import pandas as pd
import xmltodict
import requests
from datetime import datetime

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
        db_data.append((
            val['farm_id'],
            val['forecast_time'],
            val.get('temp'),
            val.get('precip', 0.0), 
            val.get('humidity'),
            val.get('wind_speed'),
            val.get('wind_gust'),
            val.get('wind_dir'),
            val.get('dew_point'),
            val.get('pressure'),
            val.get('global_rad'),
            val.get('symbol_id')
        ))

    try:
        query = """
            insert into forecast
            (farm_id, forecast_time, temp, precip, humidity, wind_speed, wind_gust, wind_dir, dew_point, pressure, global_rad, symbol_id)
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            on duplicate key update
            temp = values(temp),
            precip = values(precip),
            humidity = values(humidity),
            wind_speed = VALUES(wind_speed),
            wind_gust = VALUES(wind_gust),
            wind_dir = values(wind_dir),
            dew_point = VALUES(dew_point),
            pressure = VALUES(pressure),
            global_rad = VALUES(global_rad),
            symbol_id = VALUES(symbol_id);
        """
        conn.execute(query, db_data)
        conn.commit()
        print(f"{farm_id} forecast updated successfully")
    except Exception as e:
        conn.rollback()
        print(f"error: {e}")
        raise e
    finally:
        conn.close()

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