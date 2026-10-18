from extensions import db 
from utils import generate_uuid 

class CampExpense(db.Model):
    __tablename__ = "camp_expenses"

    id = db.Column(db.String(36), primary_key = True, default = generate_uuid)
    campId = db.Column(db.String(36), db.ForeignKey("camps.id", ondelete = "CASCADE"), nullable = False)
    paidByUserId = db.Column(db.String(36), db.ForeignKey("users.id", ondelete = "CASCADE"), nullable = False)
    title = db.Column(db.String(255), nullable = False)
    amount = db.Column(db.Numeric(10, 2), nullable = False)

    camp = db.relationship("Camp", back_populates = "expenses")
    paid_by_user = db.relationship("User", back_populates = "expenses_paid")