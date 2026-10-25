from datetime import date
from typing import Annotated

from flask import Blueprint, current_app, jsonify, redirect, render_template, request, url_for
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, ValidationError, ValidationInfo, field_validator
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError

from utils.auth import get_current_user
from extensions import db
from models import Camp, CampMember, Friendship, GearRequirement, User
from models.camp import VisibilityType
from models.campMember import MemberRole, RequestStatus

create_controller = Blueprint("create", __name__)

MAX_GEAR_ITEMS = 100
MAX_INVITEES = 150
class GearItemIn(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    itemName: Annotated[str, StringConstraints(min_length=1, max_length=255)] = Field(validation_alias="name")
    quantity: int = Field(ge=1, validation_alias="qty")

class MemberIn(BaseModel):
    userId: str
    role: MemberRole = MemberRole.CAMP_MEMBER
    status: RequestStatus = RequestStatus.APPROVED

class CampCreate(BaseModel):
    """Validated payload for POST /camps/create"""

    model_config = ConfigDict(populate_by_name=True)

    # Form Data (Part 1)
    name: Annotated[str, StringConstraints(min_length=5, max_length=255)]
    state: Annotated[str, StringConstraints(min_length=1, max_length=100)]
    city: Annotated[str, StringConstraints(min_length=1, max_length=100)]
    addres: Annotated[str, StringConstraints(min_length=1, max_length=255)] = Field(validation_alias="location")
    campoutType: Annotated[str, StringConstraints(min_length=1, max_length=100)] | None = Field(default=None, validation_alias="type")
    campSiteNumber: Annotated[str, StringConstraints(strip_whitespace=True, max_length=50)] | None = Field(default=None, validation_alias="site")
    startDate: date = Field(validation_alias="start")
    endDate: date = Field(validation_alias="end")
    expectedCampers: int = Field(ge=1, validation_alias="campers")
    campoutDescription: Annotated[str, StringConstraints(strip_whitespace=True, max_length=5000)] | None = Field(default=None, validation_alias="description")
    Visibility: VisibilityType = Field(validation_alias="visibility")

    # Gear Requirement Data (Items, Part 2 of wizard)
    items: list[GearItemIn] = Field(default_factory=list, max_length=MAX_GEAR_ITEMS)
    # Invite Data (Part 3 of wizard)
    invitees: list[str] = Field(default_factory=list, max_length=MAX_INVITEES)

    @field_validator("campSiteNumber", "campoutDescription", mode="before")
    @classmethod
    def blank_to_none(cls, value):
        if isinstance(value, str) and not value.strip():
            return None
        return value
    
    @field_validator("Visibility", mode="before")
    @classmethod
    def visibility_by_name(cls, value):
        if isinstance(value, VisibilityType):
            return value
        try:
            return VisibilityType[str(value).strip().upper()]
        except KeyError:
            raise ValueError("Choose Public, Private, or Friends Only")

    @field_validator("endDate")
    @classmethod
    def end_not_before_start(cls, value, info: ValidationInfo):
        start = info.data.get("startDate")
        if start and value < start:
            raise ValueError("End date can't be before the start date.")
        return value

    def camp_columns(self):
        """Returns Dictionary with keys matching real columns in Camp model"""
        return self.model_dump(exclude={"items", "invitees"})

    def gear_rows(self):
        """Returns list of Dictionaries with keys matching real columns in GearRequirements model"""
        rows = []
        for item in self.items:
          rows.append(item.model_dump())
        return rows

    def member_rows(self, user_id, invitees):
        rows = [MemberIn(userId=user_id, role=MemberRole.CAMP_MASTER, status=RequestStatus.APPROVED)] # Add camp master to members
        for friend_id in invitees:
            rows.append(MemberIn(userId=friend_id)) # Add everyone invited
        return [r.model_dump() for r in rows]

FIELD_LABELS = {
    "name": "Campout name",
    "state": "State",
    "city": "City",
    "location": "Location",
    "site": "Campsite number",
    "start": "Start date",
    "end": "End date",
    "campers": "Expected campers",
    "description": "Description",
    "visibility": "Visibility",
}

def valerror_to_json(exc):
    """Turn a ValidationError into {json_key: readable message}."""
    errors = {}
    for err in exc.errors():
        key = str(err["loc"][0]) if err["loc"] else "_form"
        if key in errors:
            continue  # one message per field is enough
        kind = err["type"]
        ctx = err.get("ctx", {})
        label = FIELD_LABELS.get(key, key)
        if key == "items":
            if kind == "too_long":
                msg = f"Gear list must have {MAX_GEAR_ITEMS} items or fewer."
            else:
                msg = "Each gear item needs a name (255 characters or fewer) and a quantity of at least 1."
        elif key == "invitees":
            msg = "Invalid invite list."
        elif kind in ("missing", "string_too_short"):
            msg = f"{label} is required."
        elif kind == "string_too_long":
            msg = f"{label} must be {ctx.get('max_length')} characters or fewer."
        elif kind in ("date_parsing", "date_from_datetime_parsing", "date_type"):
            msg = f"{label} must be a valid date."
        elif kind in ("int_parsing", "int_type", "int_from_float"):
            msg = f"{label} must be a whole number."
        elif kind == "greater_than_equal":
            msg = f"{label} must be at least {ctx.get('ge')}."
        elif kind == "value_error":
            msg = err["msg"].removeprefix("Value error, ")
        else:
            msg = f"{label} is invalid."
        errors[key] = msg
    return errors


def get_friends(user_id):
    """Accepted friends of the user, checks both ends of friendship."""
    friendships = Friendship.query.filter(
        Friendship.status == "accepted",
        or_(Friendship.senderId == user_id, Friendship.receiverId == user_id),
    ).all()
    friend_ids = {
        f.receiverId if f.senderId == user_id else f.senderId
        for f in friendships
    }
    friend_ids.discard(user_id)  # never list (or let someone invite) themselves
    if not friend_ids:
        return []
    return (
        User.query.filter(User.id.in_(friend_ids))
        .order_by(User.username)
        .all()
    )


def build_camp(user_id, camp_in, invitees):
    """Returns data model for SQLAlchemy camp row from form data."""
    camp = Camp(creatorId=user_id, **camp_in.camp_columns())
    for row in camp_in.member_rows(user_id, invitees):
        CampMember(camp=camp, **row)
    for row in camp_in.gear_rows():
        GearRequirement(camp=camp, **row)
    return camp

# Routes

@create_controller.get("/camps/create")
def create_camp():
    user = get_current_user()
    if user is None:
        return redirect(url_for("auth.login")) # not sure if this works
    friends = []
    for u in get_friends(user.id):
      friends.append({"id": u.id, "name": u.fullname or u.username})
    return render_template("create_camp.html", friends=friends)


@create_controller.post("/camps/create")
def process_create_camp():
    user = get_current_user()
    if user is None:
        return jsonify(errors={"_form": "Please log in to create a campout."}), 401
    user_id = user.id

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(errors={"_form": "Invalid request."}), 400

    try:
        camp_in = CampCreate.model_validate(data)
    except ValidationError as exc:
        return jsonify(errors=valerror_to_json(exc)), 400

    # Check: Members must be organizers friends
    friend_ids = {u.id for u in get_friends(user_id)}
    invitees = list(dict.fromkeys(camp_in.invitees))
    if not all(i in friend_ids for i in invitees):
        return jsonify(errors={"invitees": "You can only invite your accepted friends."}), 400

    try:
        camp = build_camp(user_id, camp_in, invitees)
        db.session.add(camp)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Failed to create campout")
        return jsonify(errors={"_form": "Something went wrong saving your campout. Please try again."}), 500

    # NOTE: CHANGE TO NEW CAMPSITE PAGE WHEN DONE
    return jsonify(id=camp.id, redirect=url_for("home.home")), 201