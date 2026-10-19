from extensions import db 

class GearClaim(db.Model):
    __tablename__ = "gear_claims"

    gearRequirementId = db.Column(db.String(36), db.ForeignKey("gear_requirements.id", ondelete = "CASCADE"), primary_key = True)
    claimedByUserId = db.Column(db.String(36), db.ForeignKey("users.id", ondelete = "CASCADE"), primary_key = True)
    quantityCovered = db.Column(db.Integer, nullable = False, default = 1)

    gear_requirement = db.relationship("GearRequirement", back_populates = "claims")
    claimed_by_user = db.relationship("User", back_populates = "gear_claims")