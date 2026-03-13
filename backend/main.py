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
            query = text("insert into farms (farm_name, location_name, latitude, longitude, soil_condition) values (:name, :location, :lat, :lng, :soil)")
            conn.execute(query, {
                "name": farm.farm_name,
                "location": farm.location_name,
                "lat": farm.latitude,
                "lng": farm.longitude,
                "soil": farm.soil_condition
            })
            conn.commit()
        return {"message": "Farm saved successfully!"}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Database save failed")
                         

@app.get("/analysis/{location}")
def get_analysis(location: str):
    with db_conn.connect() as conn:
        query = text("select * from analysis_runs where location = :loc")
        result = conn.execute(query, {"loc": location}).mappings().first()

        if result is None:
            raise HTTPException(status_code=404, detail="Analysis data not found")

        data = dict(result)

        if data.get('metrics_json'):
            data['metrics_json'] = json.loads(data['metrics_json'])
        
        if data.get('forecast_issued_at'):
            data['forecast_issued_at'] = data['forecast_issued_at'].isoformat()

        return data
    
@app.post("/register")
def register(user: schema.UserRegister):
    return sign_up(user)

@app.post("/login")
def login(user: schema.UserLogin):
    return sign_in(user)


