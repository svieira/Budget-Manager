import csv
from itertools import imap
from models import Account
from wtforms import Form
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields import FileField, SelectField, SubmitField
from wtforms.validators import Required

SINGLE, COMBINED = range(2)


class FileUploadForm(Form):
    file = FileField("Data file")
    type = SelectField("Format type", choices=[("", "Please choose an option"), ("single", "Single"), ("mixed", "Mixed")], validators=[Required("Please select a format type")])
    account = QuerySelectField("Account", query_factory=lambda: Account.query, allow_blank=True, validators=[Required("Please select an account")])
    action = SubmitField("Upload")


def load_from_file(f, skip_lines=1, **csv_options):
    f = csv.reader(f, **csv_options)
    f = iter(f)
    while skip_lines > 0:
        next(f)
        skip_lines -= 1
    for line in f:
        yield line


def load_data(file_path, mode=SINGLE, selector=lambda row, p=0: row):
    file_to_process = open(file_path, "rb")
    data = load_from_file(file_to_process)
    for row in data:
        if mode == COMBINED:
            yield selector(row, 0)
            yield selector(row, 1)
        else:
            yield selector(row)


def select_combined(row, pass_number=0):
    """We are dropping the balance value and returning either
    the spend or the deposit depending on the pass"""
    if pass_number == 0:
        return row[0:3]
    else:
        return row[0:2] + [row[3]]
