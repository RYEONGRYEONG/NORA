# pip install fastapi uvicorn mysql-connector-python

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import schema
from sign import sign_up, sign_in

app = FastAPI()

# allow the Next.js to communicate with FastAPI
# FastAPI 8000 port / Next.js 3000 port
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"], # any sites
    allow_methods=["*"], # get, post, delete
    allow_headers=["*"], # auth token
)

@app.post("/register")
def register(user: schema.UserRegister):
    return sign_up(user)

@app.post("/login")
def login(user: schema.UserLogin):
    return sign_in(user)


