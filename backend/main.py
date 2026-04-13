# pip install fastapi uvicorn mysql-connector-python

import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import schema
from database import db_conn
from sign import sign_up, sign_in
from sqlalchemy import text
import requests
import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO
import json
from datetime import date, datetime, timedelta
from fastapi import HTTPException
from database import db_url, db_conn
from services.smd_service import obs_analysis, save_results
from services.forecast_service import update_farm_forecast
from processors.final_risk_analysis import final_analysis
from services.rag_service import generate_nora_reasoning

app = FastAPI()

# allow the Next.js to communicate with FastAPI
# FastAPI 8000 port / Next.js 3000 port
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_methods=["*"], # get, post, delete
    allow_headers=["*"] # auth token
)

def fetch_yesterday_weather(target_date, db_conn):
    api_date = target_date.strftime('%d/%m/%Y')
    db_date = target_date.strftime('%Y-%m-%d')

    url = "https://www.met.ie/climate/available-data/daily-data"
    
    session = requests.Session()
    r = session.get(url)
    r.raise_for_status()
    
    soup = BeautifulSoup(r.text, "html.parser")
    token = soup.find("meta", {"name": "token"})["content"]
    
    payload = {
    "stationname": "Oak Park",
    "reportdate": api_date,
    "_token": token,
    }
    
    headers = {
    "Referer": url,
    "Origin": "https://www.met.ie",
    "User-Agent": "Mozilla/5.0",
    }

    resp = session.post(url, data=payload, headers=headers)
    resp.raise_for_status()

    tables = pd.read_html(StringIO(resp.text))
    
    if len(tables) > 0:
        df_raw = tables[0]
        raw_rain = df_raw['Rainfall  (mm)'].iloc[0]
        raw_gmin = df_raw['Grass Min Temp  (°C)'].iloc[0]
        clean_rain = 0.0 if str(raw_rain).strip().lower() == 'tr' else float(raw_rain)
        clean_gmin = None if str(raw_gmin).strip().lower() == 'n/a' else float(raw_gmin)
    
        march_table = pd.DataFrame({
            'location': ['Oak Park'],
            'date': [pd.to_datetime(df_raw['Date'].iloc[0], dayfirst=True)],
            'rain': [clean_rain],
            'maxtp': [float(df_raw['Max Temp  (°C)'].iloc[0])],
            'mintp': [float(df_raw['Min Temp  (°C)'].iloc[0])],
            'gmin': [clean_gmin],
            'wdsp': [float(df_raw['Mean Wind Speed  (knots)'].iloc[0])],
            'hg': [float(df_raw['Max Gust  (>= 34 knots)'].iloc[0])]
        })

        try:
            march_table.to_sql('obs_hist', con=db_conn, if_exists='append', index=False)
            print("succeed")
        except Exception as e:
            print(f"error: {e}")

    csv_url = "https://www.met.ie/latest-reports/observations/yesterday/download" 

    df = pd.read_csv(csv_url)
    oak_park_yesterday = df[df['Station'] == 'Oak Park']

    soil = oak_park_yesterday['Soil (ºC)'].iloc[0]
    soil = None if str(soil).strip().lower() == 'nan' else soil
    global_rad = oak_park_yesterday['Global (J/cm^2)'].iloc[0]

    with db_conn.connect() as conn:
        query = text("""
            update obs_hist 
            set soil = :soil_val, glorad = :grad
            where date = :target_date
        """)
    
        conn.execute(query, {
            "soil_val": soil,
            "grad": global_rad,
            "target_date": db_date,
        })
        conn.commit() 

def get_previous_smd(target_date, db_conn):
    day_before = (target_date - timedelta(days=1)).strftime('%Y-%m-%d')

    query = text("""
                 select smd_wd, smd_md, smd_pd from obs_hist where date = :day_before limit 1
                 """)
    
    with db_conn.connect() as conn:
        result = conn.execute(query, {"day_before": day_before}).fetchone()

    if result:
        return result[0], result[1], result[2]
    else:
        print(f"{day_before} data not found")
        raise ValueError(f"DB error: no SMD data found for {day_before}")

def run_daily_obs():
    yesterday = datetime.now() - timedelta(days=1)
    target_date_str = yesterday.strftime('%Y-%m-%d')

    fetch_yesterday_weather(yesterday, db_conn)
    
    init_wd, init_md, init_pd = get_previous_smd(yesterday, db_conn)
    df_smd = obs_analysis(init_wd, init_md, init_pd, db_conn, target_date_str)

    if df_smd is not None and not df_smd.empty:
        save_results(df_smd, db_conn)
        print("Automation Completed")
    else:
        print("Automation Failed")

def run_forecast():
    current_env = os.getenv("RUN_ENV", "local")
    with db_conn.connect() as conn:
        try:
            farm_query = text("select id, latitude, longitude from farms")
            farms = conn.execute(farm_query).fetchall()

            for farm in farms:
                farm_id = farm[0]
                lat = farm[1]
                lon = farm[2]

                update_farm_forecast(farm_id, lat, lon, conn, run_env=current_env)

            conn.commit()
            print("All farm forecasts updated successfully")

        except Exception as e:
            print(f"Error in main: {e}")
            conn.rollback() 

def main():
    if len(sys.argv) > 1:
        task = sys.argv[1]

        if task == "obs":
            run_daily_obs()
        elif task == "forecast":
            run_forecast()
        else:
            print(f"Error: Unkown task {task}")
    
    else:
        print("Error: No task specified")


if __name__ == "__main__":
    main()

@app.get("/api/historical")
def get_historical_data(farm_id: int):
    try:
        with db_conn.connect() as conn:
            farm_query = text("select soil_condition from farms where id = :id")
            farm_info = conn.execute(farm_query, {"id": farm_id}).fetchone()
            
            if not farm_info:
                return {"status": "error", "message": "Farm not found"}
            
            soil_type = farm_info[0]
            smd_col = f"smd_{'wd' if 'well' in soil_type else 'md' if 'moderately' in soil_type else 'pd'}"

            trend_query = text(f"""
                select date, {smd_col} as smd, rain 
                from obs_hist
                where date between date_sub(curdate(), interval 15 day) and date_sub(curdate(), interval 1 day)
                order by date asc
            """)
            trend_rows = conn.execute(trend_query).fetchall()
            
            trend_data = [{
                "date": r.date.isoformat(),
                "smd": float(r.smd),
                "rain": float(r.rain)
            } for r in trend_rows]

            avg_query = text(f"""
                select avg({smd_col}) as avg_smd, avg(rain) as avg_rain
                from obs_hist
                where month(date) = month(date_sub(curdate(), interval 1 day))
                and date < date_sub(curdate(), interval 1 year) 
            """)
            avg_row = conn.execute(avg_query).fetchone()

            return {
                "trend": trend_data,
                "average": {
                    "smd": float(avg_row.avg_smd),
                    "rain": float(avg_row.avg_rain)
                }
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/forecast")
def get_daily_forecast(farm_id: int): 
    try:
        with db_conn.connect() as conn:
            daily_query = text("""
                               select date, rain, maxtp, mintp, humidity from v_unified_weather
                               where farm_id = :id and date between curdate() and date_add(curdate(), interval 7 day)
                               """)
            daily_rows = conn.execute(daily_query, {"id": farm_id}).fetchall()

            return{
                "daily": [{
                    "date": r.date.isoformat(),
                    "rain": float(r.rain), # Decimal -> float
                    "max": float(r.maxtp),
                    "min": float(r.mintp),
                    "humidity": float(r.humidity)
                } for r in daily_rows]
            }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/hourly")
def get_hourly_forecast(farm_id: int, target_date: str):
    try:
        with db_conn.connect() as conn:
            hourly_query = text("""
                                select forecast_time, precip, temp, humidity, wind_speed, wind_gust
                                from forecast where farm_id = :id and date(forecast_time) = :target_date order by forecast_time asc 
                                """)
            hourly_rows = conn.execute(hourly_query, {"id": farm_id, "target_date": target_date}).fetchall()
            
            return{
                "hourly": [{
                    "time": r.forecast_time.isoformat(),
                    "rain": float(r.precip),
                    "temp": float(r.temp),
                    "humidity": float(r.humidity),
                    "wind": float(r.wind_speed),
                    "gust": float(r.wind_gust)
                } for r in hourly_rows]
            }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/farms/select/{farm_id}")
def select_and_sync_farm(farm_id: int):
    try:
        with db_conn.connect() as conn:
            farm_query = text("select latitude, longitude from farms where id = :id")
            farm = conn.execute(farm_query, {"id": farm_id}).fetchone()
            
            if not farm:
                raise HTTPException(status_code=404, detail="Farm not found")
            
            update_farm_forecast(farm_id, farm[0], farm[1], conn)
            
            conn.commit()
            return {"success": True, "message": "Forecast synced successfully"}
            
    except Exception as e:
        print(f"Sync Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to sync forecast")

@app.delete("/api/farms/{farm_id}")
def delete_farm(farm_id: int):
    try:
        with db_conn.connect() as conn:
            query = text("delete from farms WHERE id = :farm_id")
            result = conn.execute(query, {"farm_id": farm_id})
            
            conn.commit()
            
            if result.rowcount == 0:
                raise HTTPException(status_code=404, detail="Farm not found")
                
            return {"success": True, "message": f"Farm {farm_id} deleted successfully"}

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error during deletion")

@app.get("/api/farms")
def get_my_farms(email: str):
    try:
        with db_conn.connect() as conn:
            query = text("""
                select id, farm_name, location_name, latitude, longitude, soil_condition, is_default 
                from farms 
                where user_email = :email
            """)
            result = conn.execute(query, {"email": email}).fetchall()
            
            farms = []
            for row in result:
                farms.append({
                    "id": row[0],
                    "farm_name": row[1],
                    "location_name": row[2],
                    "latitude": row[3],
                    "longitude": row[4],
                    "soil_condition": row[5],
                    "is_default": row[6]
                })
            
            return farms
            
    except Exception as e:
        print(f"Fetch Farms Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch farms")

@app.get("/api/analysis")
def risk_analysis(farm_id: int, target_date: str):
    
    try: 
        try: # e.g, "2026-03-20"
            parsed_date = datetime.strptime(target_date, '%Y-%m-%d').date()
        
        except ValueError: # e.g, "03/20/2026"
            parsed_date = datetime.strptime(target_date, '%m/%d/%Y').date()

        print(f"DEBUG: farm id: {farm_id}, target date: {parsed_date}", flush=True)    

        with db_conn.connect() as conn:
            farm = conn.execute(text("select latitude, longitude from farms where id = :id"), {"id": farm_id}).fetchone()
            update_farm_forecast(farm_id, farm[0], farm[1], conn)
            conn.commit()

        query_soil = text("select soil_condition from farms where id = :farm_id")
        result = conn.execute(query_soil, {"farm_id": farm_id}).fetchone()
        soil_type = result[0]

        full_report = final_analysis(db_conn, farm_id, parsed_date, soil_type)

        target_data = next(item for item in full_report if item['date'] == target_date)

        # target_date, final_risk, smd_value, forecast_rain_sum, past_rain_sum, soil_type
        ai_reasoning = generate_nora_reasoning(
            target_date,
            target_data['final_risk'],
            target_data['smd_value'],
            target_data['forecast_rain_sum'], 
            target_data['past_rain_sum'],
            target_data['soil_type']
        )

        result['ai_reasoning'] = ai_reasoning

        return result

    except Exception as e:
        print(f"Analysis Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/save-farm")
def save_farm(farm: schema.FarmSave):
    try:
        with db_conn.connect() as conn:

            reset_query = text("update farms set is_default = 0 where user_email = :email")
            conn.execute(reset_query, {"email": farm.user_email})

            query = text("""insert into farms (farm_name, location_name, latitude, longitude, soil_condition, user_email, is_default) 
                        values (:name, :location, :lat, :lng, :soil, :email, 1)""")
            
            result = conn.execute(query, {
                "name": farm.farm_name,
                "location": farm.location_name,
                "lat": farm.latitude,
                "lng": farm.longitude,
                "soil": farm.soil_condition,
                "email": farm.user_email
                })
            
            farm_id = result.lastrowid

            update_farm_forecast(farm_id, farm.latitude, farm.longitude, conn)
            
            conn.commit()
        return {"message": "Farm saved successfully!"}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Database save failed")  
    
@app.post("/register")
def register(user: schema.UserRegister):
    return sign_up(user)

@app.post("/login")
def login(user: schema.UserLogin):
    return sign_in(user)


