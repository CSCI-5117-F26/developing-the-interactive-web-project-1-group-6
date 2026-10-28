from extensions import db
from utils import generate_uuid

class CampItem(db.Model):
   __tablename__ = "camp_items"
   id = db.Column(db.String(36), primary_key = True, default = generate_uuid)
   campId = db.Column(db.String(36), db.ForeignKey("camps.id", ondelete = "CASCADE"), nullable = False)
   userId = db.Column(db.String(36), db.ForeignKey("users.id", ondelete = "CASCADE"), nullable = False)
   itemName = db.Column(db.String(255), nullable = False)

   user = db.relationship("User")

