import os

from flask import Flask, render_template, redirect, url_for, session, jsonify
from database import check_database_connection, db, User
from authlib.integrations.flask_client import OAuth
from urllib.parse import quote_plus, urlencode

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
db.init_app(app)

with app.app_context():
    db.create_all()

oauth = OAuth(app)

app.secret_key = os.environ.get("SECRET_KEY")

oauth.register(
    "auth0",
    client_id = os.environ["AUTH0_CLIENT_ID"],
    client_secret = os.environ["AUTH0_CLIENT_SECRET"],
    client_kwargs = {"scope": "openid profile email offline_access"},
    server_metadata_url=f'https://{os.environ["AUTH0_DOMAIN"]}/.well-known/openid-configuration'
)


# Show the homepage and introduce the site and its functionality
@app.get("/")
def home():
    return render_template("index.html")

@app.route("/callback", methods = ["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token

    userinfo = token.get("userinfo")

    user = User.query.filter_by(email = userinfo["email"]).first()
    if not user: 
        user = User(
            username = userinfo.get("nickname", userinfo["email"]),
            email = userinfo["email"],
            fullname = userinfo.get("name"),
            avatar = userinfo.get("picture"),
            accessToken = token.get("access_token"),
            refreshToken = token.get("refresh_token"),
        )
        db.session.add(user)

    else: 
        user.accessToken = token.get("access_token")
        user.refreshToken = token.get("refresh_token")

    db.session.commit()

    return jsonify({"message": "Logged in!", "user_id": user.id})


@app.get("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri = url_for('callback', _external = True)
    )


@app.get("/logout")
def logout():
    session.clear()
    return redirect(
        "https://"
        + os.getenv("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": os.getenv("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

# Browse and search public camps
@app.get("/explore")
def explore():
    return render_template("explore.html")


# Show the user's active/past camps and pending camp requests/invitations
@app.get("/my-camps")
def my_camps():
    return render_template("my_camps.html")


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


# Show a camp's details, participants, and shared gear plan
@app.get("/camps/<int:camp_id>")
def camp_plan(camp_id):
    return render_template("camp_plan.html", camp_id=camp_id)


# Shows the campmaster controls for managing a camp
@app.get("/camps/<int:camp_id>/manage")
def camp_manage(camp_id):
    return render_template("camp_manage.html", camp_id=camp_id)


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


@app.get("/health")
def health_check():
    if check_database_connection():
        return{
            "status": "ok",
            "database": "connected",
        }, 200 
    
    else: 
        return {
            "status": "error", 
            "database": "unavailable"
        }