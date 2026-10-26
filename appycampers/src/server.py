import os
import models
from flask import Flask, render_template, session
from extensions import db, oauth
from controllers.camp_plan import show_plan
from controllers.camp_manage import show_controls
from controllers import (auth_controller, explore_controller, health_controller, home_controller, my_camps_controller, create_controller, profile_controller,)

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
app.register_blueprint(create_controller)
app.register_blueprint(profile_controller)

# Show a camp's details, participants, and shared gear plan
@app.get("/camps/<camp_id>")
def camp_plan(camp_id):
    return show_plan(camp_id)


# Shows the campmaster controls for managing a camp
@app.route("/camps/<camp_id>/manage", methods=["GET", "POST"])
def camp_manage(camp_id):
    return show_controls(camp_id)

@app.context_processor
def inject_user():
    """
    Context processor for injecting user data into navigation bar.
    Adapted from flask docs: https://flask.palletsprojects.com/en/stable/templating/
    """
    user_id = session.get("user_id")
    
    if user_id:
        return {"current_user": db.session.get(models.User, user_id)}
    else:
        return {"current_user": None}

