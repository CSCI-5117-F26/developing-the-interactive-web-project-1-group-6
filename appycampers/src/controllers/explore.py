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
    query = Camp.query.filter_by(Visibility=VisibilityType.PUBLIC)
    
    if search:
        description = func.coalesce(Camp.campoutDescription, literal_column("''"))
        search_text = Camp.name + literal_column("' '") + description

        search_vector = func.to_tsvector(literal_column("'english'"), search_text)
        search_query = func.websearch_to_tsquery("english", search)

        query = query.filter(search_vector.bool_op("@@")(search_query))

    camps = query.order_by(Camp.startDate.asc()).all()
    return render_template("explore.html", camps=camps, search=search)