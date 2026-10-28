from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy import func, text 
from sqlalchemy.exc import SQLAlchemyError
from extensions import db

def check_database_connection(): 
    try: 
        db.session.execute(text("SELECT 1"))
        return True 

    except SQLAlchemyError: 
        return False 