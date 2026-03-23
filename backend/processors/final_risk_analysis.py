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
    return matrix[(smd_risk, rain_risk)]

# STEP 1
def final_analysis(db_conn, farm_id, target_date):
    with db_conn.connect() as conn:
        query_soil = text("select soil_condition from farms where id = :farm_id")
        result = conn.execute(query_soil, {"farm_id": farm_id}).fetchone()
        soil_type = result[0]

        if 'poorly' in soil_type: days = 5
        elif 'moderately' in soil_type: days = 3
        else: days = 2

        max_allowed_date = date.today() + timedelta(days=8)
        if target_date > max_allowed_date:
            return {"error": f"Search available up to {max_allowed_date}"}
        
        today = date.today()
        start = today - timedelta(days=1) 

        query_weather = text("""
            select date, rain from v_unified_weather
            where (farm_id = :farm_id or farm_id is null) and date >= :start
            order by date asc
        """)

        weather_data = conn.execute(query_weather, {"farm_id": farm_id, "start": start}).fetchall()
        weather_list = [dict(row._mapping) for row in weather_data]

    # STEP 3 if first_check is not Low in step 2 
    def evaluate_date(eval_date, w_list, s_type):
        # (1) call rain_service
        rain_report = is_heavy_rain(w_list, s_type, eval_date)
        if "error" in rain_report: return {"final_risk": "Error", "details": rain_report}
        
        # (2) call smd ervice 
        # smd_report = get_smd_status(w_list, s_type, eval_date)
        # smd_risk = smd_report['risk_level']
        smd_risk = "Low" # test 
        
        # (3) call get_matrix_risk
        rain_risk = rain_report['risk_level']
        final_risk = get_matrix_risk(smd_risk, rain_risk)
    
        return {
            "final_risk": final_risk,
            "smd_risk": smd_risk,
            "rain_risk": rain_risk,
            "score": rain_report['score'],
            "smd_value": 0.0, # test
            #smd_report['smd_value'],
            "reason": rain_report.get('reason', "Normal rainfall levels."),
            "past_rain_sum": rain_report['details']['past_rain_sum'],
            "forecast_rain_sum": rain_report['details']['forecast_rain_sum']
        }

    # STEP 2. evaluate the target_date first
    first_check = evaluate_date(target_date, weather_list, soil_type)
    first_risk = first_check['final_risk']
    if first_risk == 'Low':
        first_check['message'] = f"{target_date} is a safe day for fertiliser application."
        first_check['recommended_date'] = target_date
        return first_check

    alt_report = []
    # search for an alternative date 
    for i in range(0, 9):
        check_date = today + timedelta(days=i)
        if check_date == target_date: continue
            
        alt_result = evaluate_date(check_date, weather_list, soil_type)
        alt_result['date'] =  check_date.strftime("%Y-%m-%d")
        
        alt_report.append(alt_result)

        if alt_result['final_risk'] == 'Low' and check_date != target_date:
            alt_result['message'] = f"{target_date} is {first_risk}. We strongly recommend {check_date} instead!"
            alt_result['recommended_date'] = check_date
            alt_report['full_demo_report'] = alt_report 
            return alt_result