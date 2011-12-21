from flask import abort, flash, Flask, g, Markup, render_template, request, url_for
from flask.ext import admin
from importer import FileUploadForm
from models import db
from models import Account, Category, TransactionType, Transaction, TransactionTag, TransactionsToTags
from re import compile, IGNORECASE
from server.database import connect_db, query_db
from werkzeug import secure_filename


VALID_TABLENAME = compile("^[a-z]+[a-z0-9_]$", IGNORECASE)


def create_app(config_path=None, name=None):
    """Creates a flask application instance and loads its config from config_path

    :param config_path: A string representing either a file path or an import path
    :returns: An instance of `flask.Flask`."""

    app = Flask(name or __name__)
    app.config.from_object('server.config.DebugConfig')
    app.config.from_envvar(config_path or '', silent=True)

    db.init_app(app)

    admin_blueprint = admin.create_admin_blueprint([Account, Category, TransactionType, Transaction, TransactionTag, TransactionsToTags], db.session)

    app.register_blueprint(admin_blueprint, url_prefix="/tables")

    configure_routes(app, db)
    configure_request_details(app)

    return app


def configure_request_details(app):
    @app.before_request
    def before_request():
        g.db = connect_db(app)

    @app.teardown_request
    def teardown_request(exception):
        g.db.close()

    return app


def configure_routes(app, db):

    @app.route("/")
    def index():
        results = query_db("""
            SELECT name
                , tbl_name
            FROM sqlite_master
            WHERE name NOT LIKE 'sqlite%'
            AND type = 'table'""")

        results = [Markup("""<li><a href="{}">{}</a></li>""").format(url_for("view_table", table_name=tbl_name), name) for name, tbl_name in results[1:]]

        results = Markup("<ul>") + Markup("\n").join(results) + Markup("</ul>")

        return render_template("layout.html", content=results)

    @app.route("/import", methods=["GET", "POST"])
    def data_import():
        form = FileUploadForm(request.form)

        if request.method == "POST" and form.validate():
            f = request.files["file"]
            filename = secure_filename(f.filename)
            flash("Received {}".format(filename))

        return render_template("edit_layout.html", form=form, title="Import Data")

    @app.route("/<table_name>")
    def view_table(table_name=None):
        if table_name is None or not VALID_TABLENAME.findall(table_name):
            abort(404)
        else:

            results = []

            try:
                results = query_db("SELECT * FROM {}".format(table_name))
            except Exception:
                abort(404)

            if len(results) < 2:
                flash("The table contains no data")

            return render_template("report_layout.html",
                                    results=results,
                                    title="Table View for {}".format(table_name))

    return app
