from pydantic import BaseModel, EmailStr

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    job: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str