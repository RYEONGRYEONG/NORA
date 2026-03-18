def calculate_rain_risk(forecast_list, soil_type, target_date, past_rain_sum, days):
    forecast_rain_sum = sum(item['rain'] for item in forecast_list[:2])

    # 1. hard high
    if past_rain_sum >= 10.0:
        return {"risk_level": "High", "score": 100, "reason": "Past rainfall exceeds 10mm, indicating saturated soil."}
    
    if forecast_rain_sum >= 10.0 and 'poorly' in soil_type:
        return {"risk_level": "High", "score": 100, "reason": "Heavy rainfall (>=10mm) is forecasted on poorly drained soil."}
    
    # 2. near high
    if past_rain_sum >= 7.0 and forecast_rain_sum >= 7.0:
        return {"risk_level": "High", "score": 100, "reason": "High rainfall pressure: both past and forecasted rain exceed 7mm."}

    # (1) past rain score
    if past_rain_sum >= 10.0: past_score = 40
    elif past_rain_sum >= 7.0: past_score = 30
    elif past_rain_sum >= 5.0: past_score = 20
    elif past_rain_sum >= 3.0: past_score = 10
    else: past_score = 0

    # (2) forecast rain score
    if forecast_rain_sum >= 10.0: forecast_score = 35
    elif forecast_rain_sum >= 7.0: forecast_score = 24
    elif forecast_rain_sum >= 5.0: forecast_score = 16
    elif forecast_rain_sum >= 3.0: forecast_score = 8
    else: forecast_score = 0

    # (3) soil type score
    if 'poorly' in soil_type: soil_score = 25
    elif 'moderately' in soil_type: soil_score = 15
    else: soil_score = 5

    total_score = past_score + forecast_score + soil_score

   
    # 3. Final Banding
    if total_score >= 67:
        risk_level = "High"
    elif total_score >= 34:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    return {
        "risk_level": risk_level,
        "score": total_score,
        "details": {
            "past_rain_sum": round(past_rain_sum, 2),
            "forecast_rain_sum": round(forecast_rain_sum, 2),
            "breakdown": {"past": past_score, "forecast": forecast_score, "soil": soil_score}
        }
    }