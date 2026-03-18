from sqlalchemy import text
from datetime import date, timedelta
from services.rain_service import is_heavy_rain
from services.smd_service import get_smd_status

def get_matrix_risk(smd_risk, rain_risk):
    matrix = {
        ("High", "High"): "High", ("High", "Medium"): "High", ("High", "Low"): "Medium",
        ("Medium", "High"): "High", ("Medium", "Medium"): "Medium", ("Medium", "Low"): "Medium",
        ("Low", "High"): "Medium", ("Low", "Medium"): "Medium", ("Low", "Low"): "Low",
    }
    return matrix.get((smd_risk, rain_risk), "Medium") # default: Medium

# STEP 1
def final_analysis(db_conn, farm_id, target_date):
    with db_conn.connect() as conn:
        query_soil = text("select soil_condition from farms where id = :farm_id")
        result = conn.execute(query_soil, {"farm_id": farm_id}).fetchone()
        if not result: return {"error": "Farm not found"}
        soil_type = result[0]

        start = target_date - timedelta(days=5) 
        query_weather = text("""
            select date, rain, maxtp, mintp, meantp, glorad, cbl, wdsp, hm, ddhm, hg, humidity, dew_point 
            from v_unified_weather
            where farm_id = :farm_id and date >= :start
            order by date asc
        """)
        weather_data = conn.execute(query_weather, {"farm_id": farm_id, "start": start}).fetchall()
        weather_list = [dict(row._mapping) for row in weather_data]

    # STEP 3 if first_check is not Low in step 2 
    def evaluate_date(eval_date):
        # (1) call rain_service
        rain_report = is_heavy_rain(weather_list, soil_type, eval_date)
        if "error" in rain_report: return {"final_risk": "Error", "details": rain_report}
        
        # (2) call smd ervice 
        smd_report = get_smd_status(weather_list, soil_type, eval_date)
        smd_risk = smd_report['risk_level']
        
        # (3) call get_matrix_risk
        rain_risk = rain_report['risk_level']
        final_risk = get_matrix_risk(smd_risk, rain_risk)
        
        return {
            "final_risk": final_risk,
            "smd_risk": smd_risk,
            "rain_risk": rain_risk,
            "smd_value": smd_report['smd_value'],
            "rain_details": rain_report
        }

    # STEP 2. evaluate the target_date first
    first_check = evaluate_date(target_date)
    if first_check['final_risk'] == 'Low':
        first_check['message'] = f"{target_date} is a safe day for fertiliser application."
        first_check['recommended_date'] = target_date
        return first_check

    # if high-risk, search for an alternative date 
    today = date.today() 
    for i in range(1, 11):
        check_date = today + timedelta(days=i)
        if check_date == target_date: continue
            
        alt_result = evaluate_date(check_date)
        if alt_result['final_risk'] == 'Low':
            alt_result['message'] = f"{target_date} is high-risk. We strongly recommend {check_date} instead!"
            alt_result['recommended_date'] = check_date
            return alt_result

    # if no safe days are found
    first_check['message'] = f"{target_date} is high-risk, and there are no suitable alternative dates within 10-day forecast."
    first_check['recommended_date'] = None
    return first_check