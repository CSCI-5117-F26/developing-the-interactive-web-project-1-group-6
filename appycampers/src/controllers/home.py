from flask import Blueprint, render_template

from models import Camp
from models.camp import VisibilityType


home_controller = Blueprint("home", __name__)


@home_controller.get("/")
def home():
    camps = (
        Camp.query.filter_by(Visibility=VisibilityType.PUBLIC)
        .order_by(Camp.startDate.asc())
        .limit(3)
        .all()
    )
    return render_template("index.html", camps=camps)
