from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declared_attr

_PLURALS = {"y": "ies"}

db = SQLAlchemy()


class BaseModel(object):
    __table_args__ = {'sqlite_autoincrement': True}

    # FIXME: Removing the `__tablename__` attrs from the
    # child tables results in `sqlalchemy.exc.ArgumentError`
    # exceptions.  What is the root cause?
    @declared_attr
    def __tablename__(cls):
        name = cls.__name__
        if _PLURALS.get(name[-1].lower(), False):
            name = name[:-1] + _PLURALS[name[-1].lower()]
        else:
            name = name + "s"
        return name
