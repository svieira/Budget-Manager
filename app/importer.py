import csv
from datetime import datetime
from decimal import Decimal
from itertools import izip, starmap
from models.base_model import db
from models.data_models import Transaction
from wtforms import Form
from wtforms.fields import FileField, SelectField, SubmitField
from wtforms.validators import Required


class FileUploadForm(Form):
    file = FileField("Data file")
    mode = SelectField("File Type",
                        choices=[("", ""),
                            ("mixed", "Intermixed save and spend"),
                            ("seperate", "Seperate save and spend columns")],
                        validators=[Required()])
    action = SubmitField("Upload")


class FieldMappingForm(Form):
    action = SubmitField("Import")


def load_from_file(f, skip_lines=0, filter_blanks=True, **csv_options):
    f = csv.reader(f, **csv_options)
    f = iter(f)
    while skip_lines > 0:
        next(f)
        skip_lines -= 1
    for line in f:
        if filter_blanks and not line:
            continue
        yield line


def _strip_formating(value):
    return "".join("".join(value.split("$")).split(","))


def _process_row(date, desc, amount):
    return [datetime.strptime(date, "%Y/%m/%d"), desc, _strip_formating(amount)]


# Select_* functions must return a tuple with t[0] containing
# the data and t[1] containing a boolean specifying if the data
# is income.
def select_seperate(date, desc, spend, save, *args):
    if spend:
        yield _process_row(date, desc, spend), False
    if save:
        yield _process_row(date, desc, save), True


def select_mixed(date, desc, amount):
    amount = _strip_formating(amount)
    yield _process_row(date, desc, amount), float(amount) < 0


def exhaust_substreams(stream):
    for s in stream:
        for entry in list(s):
            yield entry


def inject_data(val, stream, replace=False):
    is_func = callable(val)
    if replace and not is_func:
        raise ValueError("Mode is replace but val is not callable")
    for datum in stream:
        if not replace:
            datum.append(val if not is_func else val(datum))
        else:
            datum = val(datum)
        yield datum


def process_amount(*data):
    """Convert amounts to valid decimals"""
    data = list(data)
    data[2] = abs(Decimal(data[2]))
    return data


def prepare_data(stream, mode, spend_type, save_type, account):

    def inject_types(data):
        if data[1] is False:
            return data[0] + [spend_type.transactionTypeID, account.accountID]
        else:
            return data[0] + [save_type.transactionTypeID, account.accountID]

    assert mode in ["mixed", "seperate"], "Unknown mode provided: {}".format(mode)
    if mode == "mixed":
        stream = starmap(select_mixed, stream)
    else:
        stream = starmap(select_seperate, stream)

    stream = exhaust_substreams(stream)
    stream = inject_data(inject_types, stream, True)
    for datum in stream:
        yield process_amount(*datum)


def import_data(rows, field_names=["transactionDate", "description", "amount", "transactionTypeID", "accountID"], Model=Transaction, session=None):
    field_names = field_names if field_names else []
    session = session if session is not None else db.session

    i = 0
    for row in rows:
        assert len(row) == len(field_names), \
                "Provided row's length does not match length of field names"
        session.add(Model(**dict(izip(field_names, row))))
        i += 1

    session.commit()
    return i
