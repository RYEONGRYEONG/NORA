# pip install fastapi uvicorn mysql-connector-python

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import schema
from database import db_conn
from sign import sign_up, sign_in
from sqlalchemy import text
import json
from fastapi import HTTPException
from database import db_url, db_conn
from services.forecast_service import update_farm_forecast

app = FastAPI()

# allow the Next.js to communicate with FastAPI
# FastAPI 8000 port / Next.js 3000 port
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_methods=["*"], # get, post, delete
    allow_headers=["*"] # auth token
)

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


