from flask import Blueprint, redirect, session, url_for
from extensions import oauth, db
from models import User
from urllib.parse import quote_plus, urlencode
import os

auth_controller = Blueprint("auth", __name__)


@auth_controller.get("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri = url_for('auth.callback', _external = True)
    )

@auth_controller.route("/callback", methods=["GET", "POST"]) 
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
    session["user_id"] = user.id

    return redirect(url_for("home.home"))


@auth_controller.get("/logout")
def logout():
    session.clear()
    return redirect(
        "https://"
        + os.getenv("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home.home", _external=True),
                "client_id": os.getenv("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )