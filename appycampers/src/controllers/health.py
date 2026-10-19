from flask import Blueprint 
from database import check_database_connection 

health_controller = Blueprint("health", __name__)

@health_controller.get("/health")
def health_check():
    if check_database_connection():
        return{
            "status": "ok",
            "database": "connected",
        }, 200 
    
    else: 
        return {
            "status": "error", 
            "database": "unavailable"
        }, 500