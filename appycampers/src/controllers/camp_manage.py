from datetime import date
from flask import abort, redirect, render_template, request, url_for
from extensions import db
from models import Camp, CampMember, CampItem, GearRequirement, GearClaim
from models.camp import VisibilityType
from models.campMember import MemberRole, RequestStatus
from controllers.camp_plan import text_field
from utils.auth import get_current_user

def save_action(camp, members):
    action = request.form.get("action")
    if action == "edit_details":
        start_date = date.fromisoformat(request.form.get("start_date", ""))
        end_date = date.fromisoformat(request.form.get("end_date", ""))
        capacity = int(request.form.get("expected_campers", ""))
        if end_date < start_date:
            raise ValueError("The end date must be on or after the start date.")
        if capacity < 1 or capacity < len(members) or capacity > 10000:
            raise ValueError("Capacity must be between 1 and 10000, with room for all current members.")
        campsite = request.form.get("campsite_number", "").strip()
        if len(campsite) > 50:
            raise ValueError("Campsite number must be at most 50 characters.")
        
        camp.name = text_field("name", 255)
        camp.state = text_field("state", 100)
        camp.city = text_field("city", 100)
        camp.addres = text_field("address", 255)
        camp.campSiteNumber = campsite or None
        camp.campoutDescription = request.form.get("description", "").strip()
        camp.startDate = start_date
        camp.endDate = end_date
        camp.expectedCampers = capacity
    elif action == "edit_settings":
        camp.Visibility = VisibilityType(request.form.get("visibility", ""))
        join_requests = request.form.get("allow_join_requests")
        if join_requests not in ("true", "false"):
            raise ValueError("Choose whether to allow join requests.")
        camp.allowJoinRequets = join_requests == "true"
    elif action in ("add_requirement", "edit_requirement", "delete_requirement"):
        if action == "add_requirement":
            requirement = GearRequirement(campId=camp.id)
        else:
            requirement = GearRequirement.query.filter_by(
                id=request.form.get("requirement_id"),
                campId=camp.id,
            ).first_or_404()
            
        if action == "delete_requirement":
            db.session.delete(requirement)
        else:
            quantity = int(request.form.get("quantity", ""))
            claimed = sum(claim.quantityCovered for claim in requirement.claims)
            if quantity < 1 or quantity > 10000:
                raise ValueError("Quantity must be a whole number between 1 and 10000.")
            if quantity < claimed:
                raise ValueError("Quantity cannot be less than campers have already claimed.")
            
            requirement.itemName = text_field("item_name", 255)
            requirement.quantity = quantity
            db.session.add(requirement)
    elif action in ("approve", "reject", "promote", "demote", "remove_member"):
        member = CampMember.query.filter_by(
            id=request.form.get("member_id"),
            campId=camp.id,
        ).first_or_404()
        if member.userId == camp.creatorId:
            raise ValueError("The camp owner cannot be removed or have their role changed.")
        
        if action in ("approve", "reject"):
            if member.status != RequestStatus.PENDING:
                raise ValueError("This request has already been handled.")
            if action == "approve":
                if len(members) >= camp.expectedCampers:
                    raise ValueError("This campout is full.")
                existing = CampMember.query.filter_by(
                    campId=camp.id,
                    userId=member.userId,
                    status=RequestStatus.APPROVED,
                ).first()
                if existing:
                    raise ValueError("This camper is already a member.")
                member.status = RequestStatus.APPROVED
                member.role = MemberRole.CAMP_MEMBER
            else:
                member.status = RequestStatus.REJECTED
        else:
            if member.status != RequestStatus.APPROVED:
                raise ValueError("Only approved members can be managed.")
            if action == "promote":
                member.role = MemberRole.CAMP_MASTER
            elif action == "demote":
                member.role = MemberRole.CAMP_MEMBER
            else:
                requirement_ids = [item.id for item in camp.gear_requirements]
                GearClaim.query.filter(
                    GearClaim.gearRequirementId.in_(requirement_ids),
                    GearClaim.claimedByUserId == member.userId,
                ).delete()
                CampItem.query.filter_by(campId=camp.id, userId=member.userId).delete()
                db.session.delete(member)
    else:
        abort(400)
    db.session.commit()
    return redirect(url_for("camp_manage", camp_id=camp.id))

def show_controls(camp_id):
    user = get_current_user()
    if user is None:
        return redirect(url_for("auth.login"))
        
    camp = Camp.query.filter_by(id=camp_id).first_or_404()
    
    membership = CampMember.query.filter_by(
        campId=camp.id,
        userId=user.id,
        status=RequestStatus.APPROVED,
    ).first()
    if membership is None or membership.role not in (MemberRole.ADMIN, MemberRole.CAMP_MASTER):
        abort(403)
        
    members = CampMember.query.filter_by(
        campId=camp.id,
        status=RequestStatus.APPROVED,
    ).all()
    
    error = None
    status = 200
    if request.method == "POST":
        try:
            return save_action(camp, members)
        except ValueError as exc:
            db.session.rollback()
            error = str(exc)
            status = 400
            
    pending_requests = CampMember.query.filter_by(
        campId=camp.id,
        status=RequestStatus.PENDING,
    ).all()
            
    return render_template(
        "camp_manage.html",
        camp_id=camp.id,
        camp=camp,
        user=user,
        members=members,
        pending_requests=pending_requests,
        requirements=camp.gear_requirements,
        visibility_options=VisibilityType,
        error=error,
        form=request.form if status == 400 else {},
    ), status