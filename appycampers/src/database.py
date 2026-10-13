import os 

from sqlalchemy import create_engine, text 
from sqlalchemy.exc import SQLAlchemyError 

DATABASE_URL = os.environ["DATABASE_URL"] 

engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True
)

def check_database_connection():
    try: 
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return True 

    except SQLAlchemyError: 
        return False 