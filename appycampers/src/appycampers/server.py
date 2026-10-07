from flask import Flask, render_template

app = Flask(__name__)

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/explore")
def explore():
    return render_template("explore.html")

@app.get("/my-camps")
def my_camps():
    return render_template("my_camps.html")


@app.get("/camps/create")
def create_camp():
    return render_template("create_camp.html")


@app.get("/camps/create/gear")
def create_camp_gear():
    return render_template("create_camp_gear.html")


@app.get("/camps/create/invite")
def create_camp_invite():
    return render_template("create_camp_invite.html")


@app.get("/camps/<int:camp_id>")
def camp_plan(camp_id):
    return render_template("camp_plan.html", camp_id=camp_id)


@app.get("/camps/<int:camp_id>/manage")
def camp_manage(camp_id):
    return render_template("camp_manage.html", camp_id=camp_id)


@app.get("/profile")
def profile():
    return render_template("profile.html")


@app.get("/profile/u/<int:user_id>")
def user_profile(user_id):
    return render_template("profile.html", user_id=user_id)