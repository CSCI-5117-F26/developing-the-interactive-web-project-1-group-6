from flask import Blueprint, render_template

from models import Camp
from models.camp import VisibilityType
from utils.constants import CAMPOUT_TYPES, STATES


home_controller = Blueprint("home", __name__)


@home_controller.get("/")
def home():
    camps = (
        Camp.query.filter_by(Visibility=VisibilityType.PUBLIC)
        .order_by(Camp.startDate.asc())
        .limit(3)
        .all()
    )

    return render_template(
        "index.html",
        camps=camps,
        states=STATES,
        campout_types=CAMPOUT_TYPES,
    )