import csv
from itertools import izip_longest
from models import Account, db, Transaction
from wtforms import Form
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields import FileField, SubmitField
from wtforms.validators import Required


class FileUploadForm(Form):
    file = FileField("Data file")
    action = SubmitField("Upload")


class FieldMappingForm(Form):
    account = QuerySelectField("Account", query_factory=lambda: Account.query, allow_blank=True, validators=[Required("Please select an account")])
    action = SubmitField("Import")


def load_from_file(f, skip_lines=0, **csv_options):
    f = csv.reader(f, **csv_options)
    f = iter(f)
    while skip_lines > 0:
        next(f)
        skip_lines -= 1
    for line in f:
        yield line


def import_data(rows, field_names=None, Model=Transaction, session=None):
    field_names = field_names if field_names else []
    session = session if session else db.session

    for row in rows:
        session.add(Model(**dict(izip_longest(field_names, row, fillvalue=None))))

    session.commit()
