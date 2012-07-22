from flask import abort, flash, Markup, render_template, url_for

from models.base_model import db
from utils.database import generate_result_set


def index():
        li = Markup("""<li><a href="{}">{}</a></li>""")
        results = db.metadata.tables.keys()
        results.sort()
        results = [li.format(url_for("app.view_table", table_name=tbl_name), tbl_name) for tbl_name in results]

        results = Markup("<ul>") + Markup("\n").join(results) + Markup("</ul>")

        return render_template("layout.html", content=results)


def view_table(table_name=None):
    if table_name is None:
        abort(404)
    else:

        results = []

        try:
            table = db.metadata.tables.get(table_name, None)
            query = db.session.query(table)
            results = generate_result_set(query)
        except Exception:
            abort(404)

        if len(results) < 2:
            flash("The table contains no data")

        return render_template("report_layout.html",
                                results=results,
                                title="Table View for {}".format(table_name))
