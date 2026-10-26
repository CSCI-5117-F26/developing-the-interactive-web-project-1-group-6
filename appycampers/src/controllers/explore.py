from flask import Blueprint, render_template, request, abort, redirect, url_for
from sqlalchemy import func, literal_column, or_
from datetime import date

from models import Camp, Friendship
from models.camp import VisibilityType
from utils.auth import get_current_user
from utils.constants import STATES


explore_controller = Blueprint("explore", __name__)


@explore_controller.get("/explore")
def explore():

    today = date.today()
    page = request.args.get("page", 1, type=int)

    # strip whitespace and limit inputs to first 200 characters
    search = request.args.get("search", "").strip()
    search = search[:200] 

    location = request.args.get("location", "").strip()
    location = location[:200]

    # retrieve filters and validate incoming values
    visibility = request.args.get("visibility", "public")
    if visibility not in ("public", "friends"):
        abort(400)

    timing = request.args.get("timing", "upcoming")
    if timing not in ("upcoming", "ongoing", "past", "all"):
        abort(400)

    start_date = request.args.get("start_date", "")
    end_date = request.args.get("end_date", "")

    ## convert the date inputs
    from_date = None
    to_date = None

    try:
        if start_date:
            from_date = date.fromisoformat(start_date)
        if end_date:
            to_date = date.fromisoformat(end_date)
    except ValueError:
        abort(400)

    if from_date and to_date:
        if from_date > to_date:
            abort(400)

    # implement the standard filters
    ## visibility
    user = get_current_user()
    query = Camp.query

    if visibility == "friends":
        if user is None:
            return redirect(url_for("auth.login"))

        # get all accepted friendships involving the current user
        friendships = Friendship.query.filter(
            Friendship.status == "accepted",
            or_(Friendship.senderId == user.id, Friendship.receiverId == user.id)
        ).all()

        # the other user in each friendship is the friend
        friend_ids = []
        for friendship in friendships:
            if friendship.senderId == user.id:
                friend_ids.append(friendship.receiverId)
            else:
                friend_ids.append(friendship.senderId)

        # filter to include only public and friends-only camps created by friends
        query = query.filter(Camp.Visibility.in_([VisibilityType.PUBLIC, VisibilityType.FRIENDS_ONLY]))
        query = query.filter(Camp.creatorId.in_(friend_ids))
    else:
        query = query.filter_by(Visibility=VisibilityType.PUBLIC)

    ## timing
    if timing == "upcoming":
        query = query.filter(Camp.startDate > today)
    elif timing == "ongoing":
        query = query.filter(Camp.startDate <= today, Camp.endDate >= today)
    elif timing == "past":
        query = query.filter(Camp.endDate < today)

    ## date range
    if from_date:
        query = query.filter(Camp.startDate >= from_date)
    if to_date:
        query = query.filter(Camp.endDate <= to_date)

    # I referenced the following sources while implementing the searching approach:
    # https://www.postgresql.org/docs/current/textsearch-tables.html
    # https://www.postgresql.org/docs/current/textsearch-controls.html
    # https://docs.sqlalchemy.org/en/20/dialects/postgresql.html#full-text-search
    if search:

        # combine the name and description (empty string if no description)
        description = func.coalesce(Camp.campoutDescription, literal_column("''"))
        search_text = Camp.name + literal_column("' '") + description

        # prepare the camp text and user search then filter for matching camps
        search_vector = func.to_tsvector(literal_column("'english'"), search_text)
        search_query = func.websearch_to_tsquery("english", search)
        query = query.filter(search_vector.bool_op("@@")(search_query))

        # add sorting by relevance
        relevance = func.ts_rank(search_vector, search_query)
        query = query.order_by(relevance.desc())

    # filter by city and/or state
    if location:
        location_words = location.replace(",", " ").split()

        for word in location_words:
            location_pattern = f"%{word}%"

            city_matches = Camp.city.ilike(location_pattern)
            state_matches = Camp.state.ilike(location_pattern)

            query = query.filter(or_(city_matches, state_matches))

    # sort by date & id (if search then this will order by relevance -> date -> id)
    if timing == "past":
        # for past reverse date order so more recently finished trips show up first
        query = query.order_by(Camp.endDate.desc())
    else:
        query = query.order_by(Camp.startDate.asc())

    # I referenced the following source while implementing pagination:
    # https://flask-sqlalchemy.palletsprojects.com/en/stable/pagination/
    # add pagination and clamp values outside valid range to closest valid value
    camps = query.paginate(page=max(1, page), per_page=6, error_out=False)
    if camps.pages > 0 and page > camps.pages:
        camps = query.paginate(page=camps.pages, per_page=6, error_out=False)

    filters = {
        "search": search, 
        "timing": timing, 
        "location": location,
        "start_date": start_date,
        "end_date": end_date,
        "visibility": visibility
    }
    default_filters = {
        "search": "",
        "location": "",
        "timing": "upcoming",
        "start_date": "",
        "end_date": "",
        "visibility": "public"
    }

    return render_template(
        "explore.html",
        camps=camps,
        filters=filters,
        has_filters=filters != default_filters,
        logged_in=user is not None,
        states=STATES
    )