# pip install fastapi uvicorn mysql-connector-python

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import schema
from database import db_conn
from sign import sign_up, sign_in
from sqlalchemy import text
import json
from datetime import date, datetime
from fastapi import HTTPException
from database import db_url, db_conn
from services.forecast_service import update_farm_forecast
from processors.final_risk_analysis import final_analysis

app = FastAPI()

# allow the Next.js to communicate with FastAPI
# FastAPI 8000 port / Next.js 3000 port
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_methods=["*"], # get, post, delete
    allow_headers=["*"] # auth token
)

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
                where date between date_sub(curdate(), interval 15 day) and date_sub(curdate(), interval 2 day)
                order by date asc
            """)
            trend_rows = conn.execute(trend_query).fetchall()
            
            trend_data = [{
                "date": r.date.isoformat(),
                "smd": float(r.smd),
                "rain": float(r.rain)
            } for r in trend_rows]

            avg_query = text("""
                select avg({smd_col}) as avg_smd, avg(rain) as avg_rain
                from obs_hist
                where month(date) = month(date_sub(curdate(), interval 2 day))
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
                               where farm_id = :id and between curdate() and date_add(curdate(), interal 7 day))
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

        result = final_analysis(db_conn, farm_id, parsed_date)
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


