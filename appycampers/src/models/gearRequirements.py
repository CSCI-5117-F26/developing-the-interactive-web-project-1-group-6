from extensions import db 
from utils import generate_uuid 

class GearRequirement(db.Model):
    __tablename__ = "gear_requirements"

    id = db.Column(db.String(36), primary_key = True, default = generate_uuid)
    campId = db.Column(db.String(36), db.ForeignKey("camps.id", ondelete = "CASCADE"), nullable = False)
    itemName = db.Column(db.String(255), nullable = False)
    quantity = db.Column(db.Integer, nullable = False, default = 1)

    camp = db.relationship("Camp", back_populates = "gear_requirements")
    claims = db.relationship("GearClaim", back_populates = "gear_requirement", cascade = "all, delete-orphan")

