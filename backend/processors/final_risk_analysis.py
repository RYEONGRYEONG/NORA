from sqlalchemy import text
from datetime import date, timedelta
from services.rain_service import is_heavy_rain
from services.smd_service import get_smd_status

def get_matrix_risk(smd_risk, rain_risk):
    matrix = {
        ("High", "High"): "High", ("High", "Medium"): "High", ("High", "Low"): "High",
        ("Medium", "High"): "High", ("Medium", "Medium"): "Medium", ("Medium", "Low"): "Medium",
        ("Low", "High"): "High", ("Low", "Medium"): "Medium", ("Low", "Low"): "Low",
    }
    return matrix[(smd_risk, rain_risk)]

# STEP 1
def final_analysis(db_conn, farm_id, target_date, soil_type):
    with db_conn.connect() as conn:
        max_allowed_date = date.today() + timedelta(days=7)
        if target_date > max_allowed_date:
            return {"error": f"Search available up to {max_allowed_date}"}
        
        today = date.today()
        start = today - timedelta(days=2)


        query_weather = text("""
            select date, rain, maxtp, mintp, wdsp, cbl, humidity, glorad, smd_wd, smd_md, smd_pd from v_unified_weather
            where (farm_id = :farm_id or farm_id is null) and date >= :start
            order by date asc
        """)

        weather_data = conn.execute(query_weather, {"farm_id": farm_id, "start": start}).fetchall()
        weather_list = [dict(row._mapping) for row in weather_data]

    # STEP 3 if first_check is not Low in step 2 
    def evaluate_date(eval_date, w_list, s_type):
        # (1) call rain_service
        rain_report = is_heavy_rain(w_list, s_type, eval_date)
        if "error" in rain_report: return {"risk_level": "Error", "details": rain_report}
        
        # (2) call smd ervice 
        smd_report = get_smd_status(w_list, s_type, eval_date)
        smd_risk = smd_report['risk_level']
        
        # (3) call get_matrix_risk
        rain_risk = rain_report['risk_level']
        final_risk = get_matrix_risk(smd_risk, rain_risk)
    
        return {
            "final_risk": final_risk,
            "smd_risk": smd_risk,
            "rain_risk": rain_risk,
            "score": rain_report['score'],
            "smd_value": smd_report['smd_value'], 
            "reason": rain_report.get('reason', "Normal rainfall levels."),
            "past_rain_sum": rain_report['details']['past_rain_sum'],
            "forecast_rain_sum": rain_report['details']['forecast_rain_sum']
        }

    # STEP 2. evaluate the target_date first
    full_demo_report = []
    for i in range(0, 8):
        check_date = today + timedelta(days=i) 
        alt_result = evaluate_date(check_date, weather_list, soil_type)
        alt_result['date'] =  check_date.strftime("%Y-%m-%d")
        full_demo_report.append(alt_result) 

    target_date_str = target_date.strftime("%Y-%m-%d")
    first_check = next((item for item in full_demo_report if item['date'] == target_date_str), None)
    display_date = target_date.strftime("%d-%m-%Y")

    if first_check['final_risk'] == 'Low':
        result = dict(first_check)
        result['message'] = f"{display_date} is a safe day for fertiliser application."
        result['recommended_date'] = target_date_str
        result['full_demo_report'] = full_demo_report
        return result
    
    elif first_check['final_risk'] == 'Medium':
        alt_low = next((item for item in full_demo_report if item['final_risk'] == 'Low' and item['date'] != target_date_str), None)

        if alt_low:
            alt_low_display = date.fromisoformat(alt_low['date']).strftime("%d-%m-%Y")
            result = dict(alt_low)
            result['message'] = f"{display_date} is Medium. It is acceptable, but {alt_low_display} (Low) is a safer alternative."
            result['recommended_date'] = alt_low['date']
            result['full_demo_report'] = full_demo_report
            return result
        else:
            result = dict(first_check)
            result['message'] = f"{display_date} is Medium. No safer days (Low) found in the forecast, so proceed with caution."
            result['recommended_date'] = target_date_str 
            result['full_demo_report'] = full_demo_report
            return result
    
    # first_check['final_risk'] == 'High'
    else:
        alt_low = next((item for item in full_demo_report if item['final_risk'] == 'Low' and item['date'] != target_date_str), None)
        
        if alt_low:
            alt_low_display = date.fromisoformat(alt_low['date']).strftime("%d-%m-%Y")
            result = dict(alt_low)
            result['message'] = f"{display_date} is High-risk! We strongly recommend waiting until {alt_low_display} (Low)."
            result['recommended_date'] = alt_low['date']
            result['full_demo_report'] = full_demo_report
            return result
            
        alt_medium = next((item for item in full_demo_report if item['final_risk'] == 'Medium' and item['date'] != target_date_str), None)
        
        if alt_medium:
            alt_medium_display = date.fromisoformat(alt_medium['date']).strftime("%d-%m-%Y")
            result = dict(alt_medium)
            result['message'] = f"{display_date} is High-risk! No optimal days found, but {alt_medium_display} (Medium) is a better option."
            result['recommended_date'] = alt_medium['date']
            result['full_demo_report'] = full_demo_report
            return result
        
        # all High
        result = dict(first_check)
        result['message'] = f"{display_date} is High-risk, and there are NO suitable alternative dates within the forecast. DO NOT SPREAD."
        result['recommended_date'] = None
        result['full_demo_report'] = full_demo_report
        return result




