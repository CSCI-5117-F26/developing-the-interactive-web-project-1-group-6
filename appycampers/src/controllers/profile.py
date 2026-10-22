from flask import Blueprint, redirect, render_template, url_for

from models import User
from models.user import VisibilityType

profile_controller = Blueprint("profile", __name__)