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
    
    try: # e.g, "2026-03-20"
        parsed_date = datetime.strptime(target_date, '%Y-%m-%d').date()
        
    except ValueError: # e.g, "03/20/2026"
        parsed_date = datetime.strptime(target_date, '%m/%d/%Y').date()

    print(f"DEBUG: farm id: {farm_id}, target date: {parsed_date}", flush=True)    

    try:
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


