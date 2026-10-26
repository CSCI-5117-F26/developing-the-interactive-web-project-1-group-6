from datetime import date
from flask import abort, redirect, render_template, request, url_for
from extensions import db
from models import Camp, CampMember, CampItem, GearRequirement, GearClaim
from models.camp import VisibilityType
from models.campMember import MemberRole, RequestStatus
from controllers.camp_plan import text_field
from utils.auth import get_current_user

def save_action(camp, members):
    # Action handlers
    abort(400)

def show_controls(camp_id):
    user = get_current_user()
    if user is None:
        return redirect(url_for("auth.login"))
        
    camp = Camp.query.filter_by(id=camp_id).first_or_404()
    
    # Verify user role
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
    pending_requests = []
            
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