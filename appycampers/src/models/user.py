import uuid 

from extensions import db

def generate_uuid():
    return str(uuid.uuid4())


class User(db.Model): 
    __tablename__ = "users"

    id = db.Column(db.String(36), primary_key = True, default = generate_uuid)
    username = db.Column(db.String(100), unique = True, nullable = False)
    email = db.Column(db.String(255), unique = True, nullable = False )
    camps = db.Column(db.String(255), nullable = True)
    fullname = db.Column(db.String(255), nullable = True)
    avatar = db.Column(db.String(500), nullable = True)
    password = db.Column(db.String(500), nullable = True)
    accessToken = db.Column(db.Text, nullable = True)
    refreshToken = db.Column(db.Text, nullable = True)