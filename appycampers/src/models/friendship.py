from extensions import db 
from utils import generate_uuid

class Friendship(db.Model):
    __tablename__ = "friendships"

    id = db.Column(db.String(36), primary_key = True, default = generate_uuid)
    senderId = db.Column(db.String(36), db.ForeignKey("users.id", ondelete = "CASCADE"), nullable = False)
    receiverId = db.Column(db.String(36), db.ForeignKey("users.id", ondelete = "CASCADE"), nullable = False)
    status = db.Column(db.String(50), nullable = False, default = "pending")

    sender = db.relationship("User", foreign_keys = [senderId], back_populates = "sent_friendships")
    receiver = db.relationship("User", foreign_keys = [receiverId], back_populates = "reciever_friendships")