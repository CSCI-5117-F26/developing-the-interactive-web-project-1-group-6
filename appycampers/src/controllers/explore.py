from flask import Blueprint, render_template

from models import Camp
from models.camp import VisibilityType


explore_controller = Blueprint("explore", __name__)


@explore_controller.get("/explore")
def explore():
    camps = (
        Camp.query.filter_by(Visibility=VisibilityType.PUBLIC)
        .order_by(Camp.startDate.asc())
        .all()
    )
    return render_template("explore.html", camps=camps)
