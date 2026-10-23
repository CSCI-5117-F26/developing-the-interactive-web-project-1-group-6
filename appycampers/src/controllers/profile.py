from flask import Blueprint, redirect, render_template, url_for, session, request
from extensions import db
from sqlalchemy import and_, or_

from models import User, Friendship

profile_controller = Blueprint("profile", __name__)

@profile_controller.route("/profile", methods=["GET", "POST"])
def profile():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))

    user = User.query.get_or_404(user_id)

    if request.method == "POST":
        user.fullname = request.form.get("display_name", "").strip()
        user.about_me = request.form.get("about_me", "").strip()
        db.session.commit()
        return redirect(url_for("profile.profile"))

    return render_template("profile.html", user=user)

@profile_controller.get("/profile/friends")
def friends():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))

    user = User.query.get_or_404(user_id)

    incoming_requests = Friendship.query.filter_by(receiverId = user_id, status = "pending").all()
    outgoing_requests = Friendship.query.filter_by(senderId = user_id, status = "pending").all()

    # get all accepted friendships involving the current user
    accepted = Friendship.query.filter(
        Friendship.status == "accepted",
        or_(Friendship.senderId == user_id, Friendship.receiverId == user_id)
    ).all()

    friends_list = []

    for f in accepted:
        if f.senderId == user_id:
            friends_list.append(f.receiver)
        else:
            friends_list.append(f.sender)

    def friend_name(friend):
        return (friend.fullname or friend.username).lower()

    friends_list.sort(key = friend_name)
    
    return render_template (
        "profile_friends.html",
        user=user,
        incoming_requests = incoming_requests,
        outgoing_requests = outgoing_requests,
        friends = friends_list,
    )

@profile_controller.get("/profile/friends/request")
def send_request():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))

    user = User.query.get_or_404(user_id)

    incoming_requests = Friendship.query.filter_by(receiverId = user_id, status = "pending").all()
    outgoing_requests = Friendship.query.filter_by(senderId = user_id, status = "pending").all()

    # get all accepted friendships involving the current user
    accepted = Friendship.query.filter(
        Friendship.status == "accepted",
        or_(Friendship.senderId == user_id, Friendship.receiverId == user_id)
    ).all()

    friends_list = []

    for f in accepted:
        if f.senderId == user_id:
            friends_list.append(f.receiver)
        else:
            friends_list.append(f.sender)

    def friend_name(friend):
        return (friend.fullname or friend.username).lower()

    friends_list.sort(key = friend_name)
    
    return render_template (
        "profile_friends.html",
        user=user,
        incoming_requests = incoming_requests,
        outgoing_requests = outgoing_requests,
        friends = friends_list,
    )
