from datetime import date

from flask import Blueprint, redirect, render_template, url_for

from models import CampMember
from models.campMember import RequestStatus
from utils.auth import get_current_user
from utils.constants import CAMPOUT_TYPES, STATES

my_camps_controller = Blueprint("my_camps", __name__)


@my_camps_controller.get("/my-camps")
def my_camps():
    user = get_current_user()
    if user is None:
        return redirect(url_for("auth.login"))

    memberships = (
        CampMember.query.filter_by(
            userId=user.id,
            status=RequestStatus.APPROVED,
        )
        .join(CampMember.camp)
        .order_by(CampMember.campId)
        .all()
    )
    pending_memberships = (
    CampMember.query.filter_by(
        userId=user.id,
        status=RequestStatus.PENDING,
    )
    .all()
    )

    pending_memberships = [
        membership
        for membership in pending_memberships
        if membership.camp.creatorId != user.id
    ]
    created_camps = user.created_camps

    today = date.today()

    upcoming_memberships = []
    past_memberships = []

    for membership in memberships:
        camp = membership.camp

        if camp.endDate >= today:
            upcoming_memberships.append(membership)
        else:
            past_memberships.append(membership)

    upcoming_created_camps = []
    past_created_camps = []

    for camp in created_camps:
        user_is_already_a_member = False

        for membership in memberships:
            if membership.campId == camp.id:
                user_is_already_a_member = True
                break

        if user_is_already_a_member:
            continue

        if camp.endDate >= today:
            upcoming_created_camps.append(camp)
        else:
            past_created_camps.append(camp)

    return render_template(
        "my_camps.html",
        user=user,
        upcoming_memberships=upcoming_memberships,
        upcoming_created_camps=upcoming_created_camps,
        pending_memberships=pending_memberships,
        past_memberships=past_memberships,
        past_created_camps=past_created_camps,
        states=STATES,
        campout_types=CAMPOUT_TYPES,
    )
