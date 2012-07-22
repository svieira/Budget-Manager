from flask import abort, current_app, flash, redirect, render_template, request, url_for
from os import path, remove
from werkzeug import secure_filename
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields import SelectField
from wtforms.validators import Required

from importer import FieldMappingForm, FileUploadForm, load_from_file, import_data
from models.data_models import Account, Transaction, TransactionType


def provide_file():
    form = FileUploadForm(request.form)

    if request.method == "POST" and form.validate():
        f = request.files["file"]
        filename = secure_filename(f.filename)
        if filename is None or not filename:
            flash("Please provide a file", category="error")
        else:
            f.save(path.join(current_app.config["UPLOAD_FOLDER"], filename))
            return redirect(url_for(".data_mapping", filename=filename, mode=form.mode.data))

    return render_template("edit_layout.html", form=form, title="Import Data")


def data_mapping(filename=None):
    filepath = path.join(current_app.config["UPLOAD_FOLDER"], filename)

    try:
        data_file = open(filepath, "r")
    except IOError:
        return abort(404)

    data_file = load_from_file(data_file)
    headers = next(data_file)
    lowercase_headers = [h.lower() for h in headers]
    headers_ = [""] + headers
    header_list = zip(headers_, headers_)
    table_columns = Transaction.__table__.columns
    mode = request.args.get("mode", None)

    class NewForm(FieldMappingForm):
        pass

    for field in table_columns:
        if not field.primary_key:
            i = lowercase_headers.index(field.name.lower()) if field.name.lower() in lowercase_headers else -1
            default_ = headers[i] if i >= 0 else None
            NewForm = _generate_field(NewForm, field, choices=header_list, default=default_, mode=mode)

    form = NewForm(request.form)

    if request.method == "POST" and form.validate():
        total_imported = import_data(data_file,
                                mode,
                                form["spend_transactions"].data,
                                form["income_transactions"].data,
                                form["accountID"].data)
        flash("{} records have been imported".format(total_imported))

        data_file.close()
        remove(filepath)

        return redirect(url_for('admin.list', model_name='Transaction'))

    return render_template("edit_layout.html", form=form, title="Map Fields")


def _generate_field(form, db_field, choices=None, default=None, mode=None):
    if db_field.name.lower() == "transactiontypeid":
        income_transactions = lambda val: lambda: TransactionType.query.filter(TransactionType.isIncome == val)
        income_field = QuerySelectField("Map income values to", query_factory=income_transactions(1), allow_blank=True, validators=[Required()])
        spend_field = QuerySelectField("Map spending values to", query_factory=income_transactions(0), allow_blank=True, validators=[Required()])
        setattr(form, "income_transactions", income_field)
        setattr(form, "spend_transactions", spend_field)
        return form
    elif db_field.name.lower() == "amount" and mode == "seperate":
        income_column = SelectField("Field containing income values", choices=choices, default=default)
        spend_column = SelectField("Field containing spending values", choices=choices, default=default)
        setattr(form, "income_column", income_column)
        setattr(form, "spend_column", spend_column)
        return form
    elif db_field.name.lower() == "accountid":
        field = QuerySelectField("Account", query_factory=lambda: Account.query, allow_blank=True, validators=[Required("Please select an account")])
    else:
        field = SelectField(db_field.name, choices=choices, default=default)

    setattr(form, db_field.name, field)
    return form
