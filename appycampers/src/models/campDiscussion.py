from extensions import db 
from utils import generate_uuid

class CampDiscussion(db.Model):
    __tablename__ = "camp_discussions"

    id = db.Column(db.String(36), primary_key = True, default = generate_uuid)
    campId = db.Column(db.String(36), db.ForeignKey("camps.id", ondelete = "CASCADE"), nullable = False)
    userId = db.Column(db.String(36), db.ForeignKey("users.id", ondelete = "CASCADE"), nullable = False)
    message = db.Column(db.Text, nullable=False)
    createdAt = db.Column(db.DateTime(timezone = True), server_default = db.func.now(), nullable = False) 

    camp = db.relationship("Camp", back_populates = "discussions")
    user = db.relationship("User", back_populates = "discussions")