import pandas as pd
import xmltodict
import requests
from datetime import datetime, timedelta
from sqlalchemy import text
from services.alert_service import alert_if_heavy_rain

def update_farm_forecast(farm_id, lat, lon, conn, run_env='local'):
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
            "precip": val.get('precip'),
            "wind_speed": val.get('wind_speed'),
            "wind_gust": val.get('wind_gust'),
            "wind_dir": val.get('wind_dir'),
            "humidity": val.get('humidity'),
            "dew": val.get('dew_point'),
            "press": val.get('pressure'),
            "rad": val.get('global_rad'),
            "sym": val.get('symbol_id')
        })

# Alert Demo Code
    demo = datetime.now()
    for val in db_data:
       demo_time = datetime.strptime(val['time'], '%Y-%m-%d %H:%M:%S')
        if demo_time > demo:
            val['precip'] = 15.0
            break
            
    try:
        query = text("""
                     insert into forecast (farm_id, forecast_time, temp, precip, humidity, wind_speed, wind_gust, wind_dir, dew_point, pressure, global_rad, symbol_id)
                     values (:farm_id, :time, :temp, :precip, :humidity, :wind_speed, :wind_gust, :wind_dir, :dew, :press, :rad, :sym)
                     on duplicate key update
                     temp = values(temp), precip = values(precip), humidity = values(humidity), wind_speed = values(wind_speed), wind_gust = values(wind_gust),
                     wind_dir = values(wind_dir), dew_point = values(dew_point), pressure = values(pressure), global_rad = values(global_rad), symbol_id = values(symbol_id)
                     """)
        
        conn.execute(query, db_data)
        
        print(f"{farm_id} forecast updated successfully")

        if run_env == "github_actions":
            user_query = text("select farm_name, user_email from farms where id = :farm_id")
            farm_info = conn.execute(user_query, {"farm_id": farm_id}).fetchone()
            
            if not farm_info or not farm_info[1]:
                print(f"Skip Alert: No email found for {farm_id}")
                return
            
            farm_name = farm_info[0]
            user_email = farm_info[1]

            heavy_rain_threshold = 10.0
            alert = False

            now = datetime.now()
            time_limit = now + timedelta(hours=48)

            for val in db_data:
                forecast_time = datetime.strptime(val['time'], '%Y-%m-%d %H:%M:%S')

                print(f"{farm_name} {val['time']} Precip: {val.get('precip')}") # Github action

                if now <= forecast_time <= time_limit:
                    if val.get('precip') and float(val['precip']) >= heavy_rain_threshold:
                        alert_if_heavy_rain(user_email, farm_name, val['time'], val['precip'])
                        alert = True
                        break

            if not alert:
                print(f"No Alert Sent: No Heavy rain detected for {farm_name} within 48h")

    except Exception as e:
        conn.rollback()
        print(f"error: {e}")
        raise e
        
