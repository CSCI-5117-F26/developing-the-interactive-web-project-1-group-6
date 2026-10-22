from flask import Blueprint, redirect, render_template, url_for

from models import User

profile_controller = Blueprint("profile", __name__)

@profile_controller.get("/profile")
def profile():
    return render_template("profile.html")