from flask import Blueprint, redirect, render_template, url_for, session, request
from extensions import db

from models import User

profile_controller = Blueprint("profile", __name__)

@profile_controller.route("/profile", methods=["GET", "POST"])
def profile():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))

    user = User.query.get_or_404(user_id)

    if request.method == "POST":
        user.fullname = request.form.get("display_name", "").strip()
        db.session.commit()
        return redirect(url_for("profile.profile"))

    return render_template("profile.html", user=user)