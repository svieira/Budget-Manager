import csv
from itertools import izip_longest
from models import db, Transaction
from wtforms import Form
from wtforms.fields import FileField, SelectField, SubmitField
from wtforms.validators import Required


class FileUploadForm(Form):
    file = FileField("Data file")
    mode = SelectField("File Type", choices=[("", ""), ("mixed", "Intermixed save and spend"), ("seperate", "Seperate save and spend columns")], validators=[Required()])
    action = SubmitField("Upload")


class FieldMappingForm(Form):
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
    session = session if session is not None else db.session

    for row in rows:
        session.add(Model(**dict(izip_longest(field_names, row, fillvalue=None))))

    session.commit()
