# pip install fastapi uvicorn mysql-connector-python

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import schema
from database import db_conn
from sign import sign_up, sign_in
from sqlalchemy import text
import json

app = FastAPI()

# allow the Next.js to communicate with FastAPI
# FastAPI 8000 port / Next.js 3000 port
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:3000", "https://nora-virid.vercel.app"],
    allow_methods=["*"], # get, post, delete
    allow_headers=["*"], # auth token
)

@app.get("/analysis/{location}")
def get_analysis(location: str):
    with db_conn.connect() as conn:
        query = text("select * from analysis_runs")
        result = conn.execute(query, {"loc": location}).mappings().first()

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


