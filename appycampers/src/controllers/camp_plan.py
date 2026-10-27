from decimal import Decimal, InvalidOperation
from flask import current_app, abort, redirect, render_template, request, url_for
from sqlalchemy.exc import SQLAlchemyError
from extensions import db
from models import Camp, CampMember, CampItem, GearRequirement, GearClaim, CampExpense, ExpenseSplit, CampDiscussion
from models.campMember import MemberRole, RequestStatus
from utils.auth import get_current_user
from sqlalchemy import and_, or_
from models import Friendship
from models.camp import VisibilityType

def expense_totals(expenses, members):
    # Calculate in cents
    people = {}
    for member in members:
        people[member.userId] = {"name": member.user.username, "paid": 0, "share": 0}
    total = 0
    for expense in expenses:
        cents = int(expense.amount * 100)
        total += cents
        people.setdefault(expense.paidByUserId, {"name": expense.paid_by_user.username, "paid": 0, "share": 0})
        people[expense.paidByUserId]["paid"] += cents
        splits = {split.userId: split.user for split in expense.splits}
        if not splits:
            raise ValueError("An existing expense has no participants. Ask a campmaster to remove and recreate it.")
        share, remainder = divmod(cents, len(splits))
        for index, user_id in enumerate(sorted(splits)):
            people.setdefault(user_id, {"name": splits[user_id].username, "paid": 0, "share": 0})
            people[user_id]["share"] += share
            if index < remainder:
                people[user_id]["share"] += 1
    for person in people.values():
        person["balance"] = person["share"] - person["paid"]
    return total, people

def text_field(name, limit):
    value = request.form.get(name, "").strip()
    if not value or len(value) > limit:
        label = name.replace("_", " ")
        raise ValueError(f"Enter {label} between 1 and {limit} characters.")
    return value

def save_action(camp, user, membership, members):
    action = request.form.get("action")
    if action in ("claim", "cancel_claim"):
        item = GearRequirement.query.filter_by(id = request.form.get("requirement_id"), campId = camp.id).first_or_404()
        claim = db.session.get(GearClaim, (item.id, user.id))
        if action == "cancel_claim":
            if claim:
                db.session.delete(claim)
        else:
            try:
                quantity = int(request.form.get("quantity", ""))
            except ValueError:
                raise ValueError("Quantity must be a positive whole number.")
            others = sum(c.quantityCovered for c in item.claims if c.claimedByUserId != user.id)
            if quantity < 1 or quantity > item.quantity - others:
                raise ValueError("The given quantity exceeds the remaining requirement.")
            if claim is None:
                claim = GearClaim(gearRequirementId = item.id, claimedByUserId = user.id)
                db.session.add(claim)
            claim.quantityCovered = quantity
    elif action in ("add_item", "edit_item", "delete_item"):
        if action == "add_item":
            db.session.add(CampItem(campId = camp.id, userId = user.id, itemName = text_field("item_name", 255)))
        else:
            item = CampItem.query.filter_by(id = request.form.get("item_id"), campId = camp.id, userId = user.id).first_or_404()
            if action == "delete_item":
                db.session.delete(item)
            else:
                item.itemName = text_field("item_name", 255)
    elif action == "add_expense":
        title = text_field("title", 255)
        try:
            amount = Decimal(request.form.get("amount", ""))
            if not amount.is_finite():
                raise ValueError("Enter a valid amount.")
            if amount <= 0 or amount > Decimal("99999999.99"):
                raise ValueError("Enter an amount between 0.01 and 99999999.99.")
            if amount != amount.quantize(Decimal(".01")):
                raise ValueError("Enter a positive amount with two decimal places.")
        except InvalidOperation:
            raise ValueError("Enter a valid amount.")
        participants = set(request.form.getlist("participants"))
        if not participants or not participants.issubset({m.userId for m in members}):
            raise ValueError("Choose at least one current camper to share the cost.")
        expense = CampExpense(campId = camp.id, paidByUserId = user.id, title = title, amount = amount)
        expense.splits = [ExpenseSplit(userId = person) for person in sorted(participants)]
        db.session.add(expense)
    elif action == "delete_expense":
        expense = CampExpense.query.filter_by(id = request.form.get("expense_id"), campId = camp.id).first_or_404()
        if expense.paidByUserId != user.id and membership.role not in (MemberRole.ADMIN, MemberRole.CAMP_MASTER):
            abort(403)
        db.session.delete(expense)
    elif action == "message":
        db.session.add(CampDiscussion(campId = camp.id, userId = user.id, message = text_field("message", 2000)))
    elif action == "leave":
        if camp.creatorId == user.id:
            raise ValueError("The owner must transfer ownership before leaving.")
        requirement_ids = [item.id for item in camp.gear_requirements]
        GearClaim.query.filter(GearClaim.gearRequirementId.in_(requirement_ids), GearClaim.claimedByUserId == user.id).delete()
        CampItem.query.filter_by(campId = camp.id, userId = user.id).delete()
        # Keep past expenses and their participants unchanged when someone leaves.
        CampMember.query.filter_by(campId = camp.id, userId = user.id).delete()
    else:
        abort(400)
    db.session.commit()
    if action == "leave":
        return redirect(url_for("my_camps.my_camps"))
    # Return to the section the change was made in.
    section = {"claim": "requirements", "cancel_claim": "requirements",
               "add_item": "extra-items", "edit_item": "extra-items", "delete_item": "extra-items",
               "add_expense": "expenses", "delete_expense": "expenses", "message": "discussion"}[action]
    return redirect(url_for("camp_plan", camp_id = camp.id, _anchor = section))

def show_plan(camp_id):
    try:
        return render_plan(camp_id)
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.error("Shared camp plan database operation failed.")
        abort(503, description = "The database is unavailable. Please try again.")

def render_plan(camp_id):
    user = get_current_user()
    if user is None:
        return redirect(url_for("auth.login"))
    error = None
    status = 200
    try:
        camp = Camp.query.filter_by(id = camp_id).first_or_404()
        members = CampMember.query.filter_by(campId = camp.id, status = RequestStatus.APPROVED).all()
        membership = None
        for member in members:
            if member.userId == user.id:
                membership = member
                break
        if membership is None:
            if request.method == "POST":
                abort(403)
            if camp.Visibility == VisibilityType.FRIENDS_ONLY:
                friendship = Friendship.query.filter(
                    Friendship.status == "accepted",
                    or_(
                        and_(
                            Friendship.senderId == user.id,
                            Friendship.receiverId == camp.creatorId,
                        ),
                        and_(
                            Friendship.senderId == camp.creatorId,
                            Friendship.receiverId == user.id,
                        ),
                    ),
                ).first()
                if friendship is None:
                    abort(403)
            elif camp.Visibility != VisibilityType.PUBLIC:
                abort(403)
        if request.method == "POST":
            return save_action(camp, user, membership, members)
    except ValueError as exc:
        db.session.rollback()
        error, status = str(exc), 400
    requirements = camp.gear_requirements
    covered = {}
    my_claims = {}
    covered_total = 0
    required_total = 0
    requirements_met = 0
    for item in requirements:
        covered[item.id] = 0
        for claim in item.claims:
            covered[item.id] += claim.quantityCovered
            if claim.claimedByUserId == user.id:
                my_claims[item.id] = claim.quantityCovered
        covered_total += min(covered[item.id], item.quantity)
        required_total += item.quantity
        if covered[item.id] >= item.quantity:
            requirements_met += 1
    expenses = camp.expenses
    try:
        total, balances = expense_totals(expenses, members)
    except ValueError as exc:
        total, balances = None, {}
        error = str(exc)
    extra_items = (
        CampItem.query.filter_by(campId = camp.id)
        .order_by(CampItem.itemName)
        .all()
    )
    messages = (
        CampDiscussion.query.filter_by(campId = camp.id)
        .order_by(CampDiscussion.createdAt, CampDiscussion.id)
        .all()
    )
    return render_template(
        "camp_plan.html",
        camp_id = camp.id,
        camp = camp,
        user = user,
        members = members,
        requirements = requirements,
        requirements_met = requirements_met,
        covered = covered,
        covered_total = covered_total,
        required_total = required_total,
        my_claims = my_claims,
        can_edit = membership is not None,
        is_campmaster = (
            membership is not None
            and membership.role in (MemberRole.ADMIN, MemberRole.CAMP_MASTER)
        ),
        extra_items = extra_items,
        messages = messages,
        expenses = expenses,
        total = total,
        balances = balances,
        error = error,
        form = request.form if status == 400 else {},
    ), status

