import pandas as pd
import math
from sqlalchemy import text
from database import db_conn
from processors.smd_processor import calculate_pe_from_obs, calculated_smd, calculate_pe_forecast

def get_smd_status(weather_list, soil_type, target_date):
    yesterday_data = weather_list[0]

    smd_col = f"smd_{'wd' if 'well' in soil_type else 'md' if 'moderately' in soil_type else 'pd'}"
    
    current_smd = yesterday_data.get(smd_col, 0.0)
    forecast_days = [item for item in weather_list if item['date'] >= yesterday_data['date'] + timedelta(days=1)]
    final_smd = current_smd

    for day_data in forecast_days:
        pe = calculate_pe_forecast(
            max_temp = day_data['maxtp'],
            min_temp = day_data['mintp'],
            mean_tmep = day_data['meantp'],
            wind_speed = day_data['wdsp'],
            pressure = day_data['cbl'],
            humidity = day_data['humidity'],
            total_rad_mj = day_data['glorad'] / 100.0
        )

        _, next_smd, _ = calculated_smd(final_smd, pe, day_data['rain'], soil_type)
        final_smd = next_smd

        if day_data['date'] == target_date:
            break

    if final_smd < 0:
        risk_level = "High"
    elif final_smd < 10:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    return {
        "risk_level": risk_level,
        "smd_value": final_smd
    }


def obs_analysis(init_wd, init_md, init_pd, db_conn):

    current_smd_wd = init_wd # well draiend
    current_smd_md = init_md # moderately drained
    current_smd_pd = init_pd # poorly drained

    query = text("""
             select date, maxtp, mintp, wdsp, glorad, rain
             from obs_hist where date = '2026-03-17'
             order by date
                 """)
    
    try:
        with db_conn.connect() as conn:
            obs_df = pd.read_sql(query, conn)
        
        if obs_df.empty:
            print("No Data Found")
            return None

        results = []

        for _, row in obs_df.iterrows():
            obs_row = {
                'max_temp': row['maxtp'],
                'min_temp': row['mintp'],
                'wdsp': row['wdsp'],
                'glorad': row['glorad'],
                'rain': row['rain']
            }
        
            pe = calculate_pe_from_obs(obs_row)
        
            _, current_smd_wd, _ = calculated_smd(current_smd_wd, pe, row['rain'], 'well')
            _, current_smd_md, _ = calculated_smd(current_smd_md, pe, row['rain'], 'moderately')
            _, current_smd_pd, _ = calculated_smd(current_smd_pd, pe, row['rain'], 'poorly')

            results.append({
                'date': row['date'],
                'pe': pe,
                'rain': row['rain'],
                'smd_wd': current_smd_wd,
                'smd_md': current_smd_md,
                'smd_pd': current_smd_pd
            })

        final_df = pd.DataFrame(results)
        return final_df

    except Exception as e:
        print(f"error: {e}")
        return None

def save_results(df, conn):
    if df is None or df.empty:
        print("No Data Found")
        return

    query = text("""
        update obs_hist set
            pe = :pe,
            smd_wd = :smd_wd,
            smd_md = :smd_md,
            smd_pd = :smd_pd
            where date = :date
            """)

    try:
        with db_conn.begin() as conn: 
            for _, row in df.iterrows():
                conn.execute(query, {
                    'pe': row['pe'],
                    'smd_wd': row['smd_wd'],
                    'smd_md': row['smd_md'],
                    'smd_pd': row['smd_pd'],
                    'date': row['date']
                })
        print(f"{len(df)} succeed")
    except Exception as e:
        print(f"error: {e}")

    

    
    