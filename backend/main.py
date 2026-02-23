# pip install fastapi uvicorn mysql-connector-python

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine
# allow the Next.js to communicate with FastAPI
# FastAPI 8000 port / Next.js 3000 port

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"], # any sites
    allow_methods=["*"], # get, post, delete
    allow_headers=["*"], # auth token
)

load_dotenv()
db_user = os.getenv('db_user')
db_password = os.getenv('db_password')
db_host = os.getenv('db_host')
db_port = os.getenv('db_port')
db_name = os.getenv('db_name')

db_conn = create_engine(f'mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')


@app.get("/data")
def get_data():
    query = "select * from forecast_cache"
    query2 = "select * from obs_hist"
    df = pd.read_sql(query, db_conn)
    df2 = pd.read_sql(query2, db_conn)
    
    return {
        "forecast": df.to_dict(orient="records"), 
        "observed": df2.to_dict(orient="records")      
    }

@app.get("/talking")
def get_talking():
    query3 = "select * from forecast_cache limit 3" 
    query4 = "select * from obs_hist limit 7" 
    
    df3 = pd.read_sql(query3, db_conn)
    df4 = pd.read_sql(query4, db_conn)

    future_3days = df3['rainfall'].sum()
    past_7days = df4['rainfall'].sum()

    return {
        "talking_to_each_other": {
            "combined_rainfall_value": round(past_7days + future_3days, 2),
            "risk": "Calculating"
        }
    }
