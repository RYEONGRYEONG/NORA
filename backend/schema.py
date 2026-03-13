from pydantic import BaseModel, EmailStr

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    job: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class FarmSave(BaseModel):
    farm_name: str
    location_name: str
    latitude: float
    longitude: float
    soil_condition: str
    user_email: str