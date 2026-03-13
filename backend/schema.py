from pydantic import BaseModel, EmailStr

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    job: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class FarmSave(BaseModel):
    name: str
    location: str
    lat: float
    lng: float
    soil_condition: str