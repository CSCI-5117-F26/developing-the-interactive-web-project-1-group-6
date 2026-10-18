from extensions import db 
from utils import generate_uuid 
import enum 

class MemberRole(enum.Enum):
    CAMP_MASTER = "camp_master"
    ADMIN = "admin"
    CAMP_MEMBER = "camper_member"

class RequestStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class CampMember(db.Model):
    __tablename__ = "camp_members"

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    campId = db.Column(db.String(36), db.ForeignKey("camps.id", ondelete="CASCADE"), nullable=False)
    userId = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = db.Column(db.Enum(MemberRole), nullable=False, default=MemberRole.CAMPER)
    status = db.Column(db.Enum(RequestStatus), nullable=False, default=RequestStatus.PENDING)

    camp = db.relationship("Camp", back_populates="members")
    user = db.relationship("User", back_populates="camp_memberships")