from sqlalchemy import text
from database import db_conn
from auth import hash_password, verify_password
import schema

def sign_up(user: schema.UserRegister):
    with db_conn.connect() as conn:
        existing = conn.execute(
            text("select * from users where email = :email"),
            {"email": user.email}
        ).fetchone()

        if existing:
            return {"success": False, "message": "Eamil already exists"}
        
        hashed_pwd = hash_password(user.password)
        conn.execute(
            text("insert into users (email, password, job) values (:email, :password, :job)"),
            {"email": user.email, "password": hashed_pwd, "job": user.job}
        )
        conn.commit()
        return {"success": True, "message": "registered successfully"}
    
def sign_in(user: schema.UserLogin):
    with db_conn.connect() as conn:
        db_user = conn.execute(
            text("select * from users where email = :email"),
            {"email": user.email}
        ).fetchone()

        if not db_user or not verify_password(user.password, db_user.password):
            return {"success": False, "message": "Invalid email or password"}
            
    return {
        "success": True,
        "message": "Login successful",
        "user": {"email": db_user.email, "job": db_user.job}
    }
            
