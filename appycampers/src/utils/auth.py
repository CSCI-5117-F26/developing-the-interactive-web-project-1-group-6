from __future__ import annotations

from flask import session

from models import User


def get_current_user():
    user_id = session.get("user_id")
    if user_id:
        user = User.query.get(user_id)
        if user is not None:
            return user

    token = session.get("user", {})
    userinfo = token.get("userinfo", {}) if isinstance(token, dict) else {}
    email = userinfo.get("email")
    if not email:
        return None

    return User.query.filter_by(email=email).one_or_none()
