import os
import models
from flask import Flask, render_template
from extensions import db, oauth
from controllers.camp_plan import show_plan
from controllers.camp_manage import show_controls
from controllers import (auth_controller, explore_controller, health_controller, home_controller, my_camps_controller,)

app = Flask(__name__)

# Formats a date
@app.template_filter("campdate")
def format_camp_date(value):
    if not value:
        return ""
    return f"{value.strftime('%b')} {value.day}, {value.year}"

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
app.secret_key = os.environ.get("SECRET_KEY")

db.init_app(app)
oauth.init_app(app)


oauth.register(
    "auth0",
    client_id = os.environ["AUTH0_CLIENT_ID"],
    client_secret = os.environ["AUTH0_CLIENT_SECRET"],
    client_kwargs = {"scope": "openid profile email offline_access"},
    server_metadata_url=f'https://{os.environ["AUTH0_DOMAIN"]}/.well-known/openid-configuration'
)

app.register_blueprint(auth_controller)
app.register_blueprint(explore_controller)
app.register_blueprint(health_controller)
app.register_blueprint(home_controller)
app.register_blueprint(my_camps_controller)

# Section to enter the camp details when creating a new camp
@app.get("/camps/create")
def create_camp():
    return render_template("create_camp.html")

# Section to set gear requirements when creating a new camp
@app.get("/camps/create/gear")
def create_camp_gear():
    return render_template("create_camp_gear.html")

# Section to invite friends when creating a new camp
@app.get("/camps/create/invite")
def create_camp_invite():
    return render_template("create_camp_invite.html")


@app.route("/camps/<camp_id>", methods=["GET", "POST"])
def camp_plan(camp_id):
    return show_plan(camp_id)

# Shows the campmaster controls for managing a camp
@app.route("/camps/<camp_id>/manage", methods=["GET", "POST"])
def camp_manage(camp_id):
    return show_controls(camp_id)

# Show and edit the user's own profile details
@app.get("/profile")
def profile():
    return render_template("profile.html")


# Show friends and manage incoming and outgoing friend requests
@app.get("/profile/friends")
def profile_friends():
    return render_template("profile_friends.html")


# Show another user's public profile
@app.get("/profile/u/<int:user_id>")
def user_profile(user_id):
    return render_template("profile.html", user_id=user_id)
