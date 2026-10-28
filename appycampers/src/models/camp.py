from extensions import db 
from utils import generate_uuid 
import enum 

class VisibilityType(enum.Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    FRIENDS_ONLY = "friends_only"

class Camp(db.Model): 
    __tablename__ = "camps"
    id = db.Column(db.String(36), primary_key = True, default = generate_uuid)
    creatorId = db.Column(db.String(36), db.ForeignKey("users.id", ondelete = "CASCADE"), nullable = False)
    name = db.Column(db.String(255), nullable = False)
    state = db.Column(db.String(100), nullable = False)
    city = db.Column(db.String(100), nullable = False)
    addres = db.Column(db.String(255), nullable = False) 
    campSiteNumber = db.Column(db.String(50), nullable = True)
    startDate = db.Column(db.Date, nullable = False)
    endDate = db.Column(db.Date, nullable = False)
    expectedCampers = db.Column(db.Integer, nullable = False, default = 1)
    campoutDescription = db.Column(db.Text, nullable = True)
    longitude = db.Column(db.String(100), nullable = True)
    latitude = db.Column(db.String(100), nullable = True)
    campoutType = db.Column(db.String(100), nullable = True)
    campImage = db.Column(db.String(500), nullable = True)
    Visibility = db.Column(db.Enum(VisibilityType), nullable = False, default = VisibilityType.PUBLIC)
    allowJoinRequets = db.Column(db.Boolean, nullable = False, default = True) 

    creator = db.relationship("User", back_populates = "created_camps")
    members = db.relationship("CampMember", back_populates = "camp", cascade = "all, delete-orphan")
    discussions = db.relationship("CampDiscussion", back_populates = "camp", cascade = "all, delete-orphan")
    gear_requirements = db.relationship("GearRequirement", back_populates = "camp", cascade = "all, delete-orphan")
    expenses = db.relationship("CampExpense", back_populates = "camp", cascade = "all, delete-orphan")
