from flask import Blueprint, render_template

from models import Camp, Friendship
from models.camp import VisibilityType


create_controller = Blueprint("create", __name__)

@create_controller.get("/camps/create")
def create_camp():
    return render_template("create_camp.html")

@create_controller.post("/camps/create")
def 