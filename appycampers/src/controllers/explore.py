from flask import Blueprint, render_template, request, abort
from sqlalchemy import func, literal_column, or_
from datetime import date

from models import Camp
from models.camp import VisibilityType


explore_controller = Blueprint("explore", __name__)


@explore_controller.get("/explore")
def explore():

    today = date.today()

    # strip whitespace and limit inputs to first 200 characters
    search = request.args.get("search", "").strip()
    search = search[:200] 

    location = request.args.get("location", "").strip()
    location = location[:200]

    # retrieve filters
    timing = request.args.get("timing", "upcoming")
    if timing not in ("upcoming", "ongoing", "past", "all"):
        abort(400)

    start_date = request.args.get("start_date", "")
    end_date = request.args.get("end_date", "")

    # convert the date inputs
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
    query = Camp.query.filter_by(Visibility=VisibilityType.PUBLIC)

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
        query = query.order_by(Camp.startDate.desc())
    else:
        query = query.order_by(Camp.startDate.asc())

    camps = query.order_by(Camp.id.asc()).all()
    filters = {
        "search": search, 
        "timing": timing, 
        "location": location,
        "start_date": start_date,
        "end_date": end_date
    }
    default_filters = {
        "search": "",
        "location": "",
        "timing": "upcoming",
        "start_date": "",
        "end_date": ""
    }

    return render_template(
        "explore.html",
        camps=camps,
        filters=filters,
        has_filters= filters != default_filters
    )