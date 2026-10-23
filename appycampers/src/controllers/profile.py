from flask import Blueprint, redirect, render_template, url_for, session, request, flash
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
        user = user,
        incoming_requests = incoming_requests,
        outgoing_requests = outgoing_requests,
        friends = friends_list,
    )

@profile_controller.post("/profile/friends/request")
def send_request():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))

    username = request.form.get("username", "").strip().lstrip("@")
    target = User.query.filter_by(username = username).first()

    if not target:
        flash("No user found with that username.")
        return redirect(url_for("profile.friends"))
    
    if target.id == user_id:
        flash("You can't send a friend request to yourself.")
        return redirect(url_for("profile.friends"))
        

    # search for matches 
    existing = Friendship.query.filter(
        or_(
            and_(Friendship.senderId == user_id, Friendship.receiverId == target.id),
            and_(Friendship.senderId == target.id, Friendship.receiverId == user_id),
        )
    ).first()

    if existing:
        if existing.status == "accepted":
            flash(f"You are already friends with @{target.username}.")
        elif existing.senderId == user_id:
            flash(f"You already sent a request to @{target.username}.")
        else:
            flash(f"@{target.username} already sent you a request. Accept it below.")
        return redirect(url_for("profile.friends"))

    db.session.add(Friendship(senderId = user_id, receiverId = target.id, status = "pending"))
    db.session.commit()
    flash(f"Friend request sent to @{target.username}!")
    
    return redirect(url_for("profile.friends"))

@profile_controller.post("/profile/friends/accept/<friendship_id>")
def accept_request(friendship_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))

    friendship = Friendship.query.filter_by(
        id = friendship_id, receiverId = user_id, status = "pending"
    ).first_or_404()

    friendship.status = "accepted"
    db.session.commit()

    return redirect(url_for("profile.friends"))

@profile_controller.post("/profile/friends/decline/<friendship_id>")
def decline_request(friendship_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))

    friendship = Friendship.query.filter_by(
        id = friendship_id, receiverId = user_id, status = "pending"
    ).first_or_404()

    db.session.delete(friendship)
    db.session.commit()
    
    return redirect(url_for("profile.friends"))

@profile_controller.post("/profile/friends/cancel/<friendship_id>")
def cancel_request(friendship_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))

    friendship = Friendship.query.filter_by(
        id = friendship_id, senderId = user_id, status = "pending"
    ).first_or_404()

    db.session.delete(friendship)
    db.session.commit()

    flash(f"Friend request cancelled")
    return redirect(url_for("profile.friends"))

@profile_controller.post("/profile/friends/remove/<friend_id>")
def remove_friend(friend_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))

    friendship = Friendship.query.filter(
        Friendship.status == "accepted",
        or_(
            and_(Friendship.senderId == user_id, Friendship.receiverId == friend_id),
            and_(Friendship.senderId == friend_id, Friendship.receiverId == user_id),
        ),
    ).first_or_404()

    db.session.delete(friendship)
    db.session.commit()
    
    return redirect(url_for("profile.friends"))