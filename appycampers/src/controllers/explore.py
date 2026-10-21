from flask import Blueprint, render_template, request
from sqlalchemy import func, literal_column

from models import Camp
from models.camp import VisibilityType


explore_controller = Blueprint("explore", __name__)


@explore_controller.get("/explore")
def explore():

    # I referenced the following sources while implementing the searching approach:
    # https://www.postgresql.org/docs/current/textsearch-tables.html
    # https://www.postgresql.org/docs/current/textsearch-controls.html
    # https://docs.sqlalchemy.org/en/20/dialects/postgresql.html#full-text-search
    search = request.args.get("search", "").strip()
    search = search[:200] # Limit search to first 200 characters
    query = Camp.query.filter_by(Visibility=VisibilityType.PUBLIC)

    
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

    # sort by date & id (if search then this will order by relevance -> date -> id)
    camps = query.order_by(Camp.startDate.asc(), Camp.id.asc()).all()
    return render_template("explore.html", camps=camps, search=search)