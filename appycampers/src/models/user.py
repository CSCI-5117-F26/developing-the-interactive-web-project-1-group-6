import uuid 

from extensions import db
from utils import generate_uuid

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

    sent_friendships = db.relationship("Friendship", foreign_keys = "Friendship.sender_id", back_populates = "sender", passive_delete = True)

    received_friendships = db.relationship("Friendship", foreign_keys = "Friendship.receiver_id", back_populates = "receiver", passive_deletes = True)

    created_camps = db.relationship("Camp", back_populates = "creator", cascade = "all, delete-orphan")
    camp_memberships = db.relationship("CampMember", back_populates = "user", cascade = "all, delete-orphan")
    gear_claims = db.relationship("GearClaim", back_populates = "claimed_by_user", cascade = "all, delete-orphan")
    expenses_paid = db.relationship("CampExpense", back_populates = "paid_by_user", cascade = "all, delete-orphan")


