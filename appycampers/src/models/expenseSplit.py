from extensions import db 
from utils import generate_uuid 

class ExpenseSplit(db.Model):
    __tablename__ = "expense_splits"

    id = db.Column(db.String(36), primary_key = True, default = generate_uuid)
    expenseId = db.Column(db.String(36), db.ForeignKey("camp_expenses.id", ondelete = "CASCADE"), nullable = False)
    userId = db.Column(db.String(36), db.ForeignKey("users.id", ondelete = "CASCADE"), nullable = False)

    expense = db.relationship("CampExpense", back_populates = "splits")
    user = db.relationship("User", back_populates = "expense_splits")