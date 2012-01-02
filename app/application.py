from flask import abort, flash, Flask, g, Markup, redirect, render_template, request, url_for
from flask.ext import admin
from importer import FieldMappingForm, FileUploadForm, load_from_file
from models import db
from models import Account, Category, TransactionType, Transaction, TransactionTag, TransactionsToTags
from os import path
from re import compile, IGNORECASE
from server.database import connect_db, query_db
from werkzeug import secure_filename
from wtforms.fields import SelectField


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
    def provide_file():
        form = FileUploadForm(request.form)

        if request.method == "POST" and form.validate():
            f = request.files["file"]
            filename = secure_filename(f.filename)
            f.save(path.join(app.config["UPLOAD_FOLDER"], filename))
            return redirect(url_for("data_mapping", filename=filename))

        return render_template("edit_layout.html", form=form, title="Import Data")

    @app.route("/import/<path:filename>", methods=["GET", "POST"])
    def data_mapping(filename=None):
        f = open(path.join(app.config["UPLOAD_FOLDER"], filename), "r")
        f = load_from_file(f)
        headers = next(f)
        lowercase_headers = [h.lower() for h in headers]
        headers_ = [""] + headers
        header_list = zip(headers_, headers_)
        table_columns = Transaction.__table__.columns

        class NewForm(FieldMappingForm):
            pass

        for field in table_columns:
            if not field.primary_key:
                i = lowercase_headers.index(field.name.lower()) if field.name.lower() in lowercase_headers else -1
                default_ = headers[i] if i >= 0 else None
                setattr(NewForm, field.name, SelectField(field.name, choices=header_list, default=default_))

        form = NewForm(request.form)

        if request.method == "POST" and form.validate():
            results = {}
            for field in form:
                if field.data and field.name in table_columns:
                    results[field.name] = field.data
            return str(results)

        return render_template("edit_layout.html", form=form, title="Map Fields")

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
