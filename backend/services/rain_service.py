from sqlalchemy import text
from datetime import timedelta
from processors.rain_processor import calculate_rain_risk

def is_heavy_rain(weather_list, soil_type, target_date):
    if soil_type == 'poor':
        days = 5
    elif soil_type == 'moderately':
        days = 3
    else:
        days = 2
        
    # calculate the total rainfall over the past days from "target date"
    # e.g, today: 17th
    start = target_date - timedelta(days=days)  # start: 17-days
    end = target_date - timedelta(days=1) # end: 16th

    past_rain_sum = sum(item['rain'] for item in weather_list if start <= item['date'] <= end)
    
    forecast_list = [
        item for item in weather_list if item['date'] >= target_date
    ]

    if not forecast_list:
        return {"error": "No future forecast data found."}
    
    return calculate_rain_risk(
        db_forecast = forecast_list,
        soil_type = soil_type,
        target_date = target_date,
        past_rain_sum = past_rain_sum,
        days = days
    )