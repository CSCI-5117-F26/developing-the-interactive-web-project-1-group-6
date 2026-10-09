from flask import Flask, render_template

from database import check_database_connection

app = Flask(__name__)


# Show the homepage and introduce the site and its functionality
@app.get("/")
def home():
    return render_template("index.html")

# TODO REMOVE THIS AND IMPLEMENT AUTH0 FOR LOGIN MANAGEMENT
@app.get("/login")
def login():
    return render_template("index.html")


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

    return {
        "status": "error", 
        "database": "unavailable"
    }