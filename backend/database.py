import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()


db_user = os.getenv('db_user')
db_password = os.getenv('db_password')
db_host = os.getenv('db_host')
db_port = os.getenv('db_port')
db_name = os.getenv('db_name')
db_url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


def get_db():
    return create_engine(db_url)

db_conn = get_db()

