from dotenv import load_dotenv
load_dotenv()
import os
import models
from flask import Flask, render_template
from extensions import db, oauth
from controllers import (auth_controller, explore_controller, health_controller, home_controller, my_camps_controller, create_controller, profile_controller,)

app = Flask(__name__)

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
    return render_template("camp_plan.html", camp_id=camp_id)


# Shows the campmaster controls for managing a camp
@app.get("/camps/<camp_id>/manage")
def camp_manage(camp_id):
    return render_template("camp_manage.html", camp_id=camp_id)

