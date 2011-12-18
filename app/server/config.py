from os import path

here = path.dirname(path.abspath(__file__))

db_path = path.join(path.dirname(path.dirname(here)), "budget.sqlite")
db_path_dev = "sqlite://:memory:"


class BaseConfig(object):
    DB_PATH = db_path_dev
    DEBUG = False
    SECRET_KEY = "Don'tTell4ndIwon'tTattl3E1th3r!"
    SQLALCHEMY_DATABASE_URI = db_path
    TESTING = False


class DebugConfig(BaseConfig):
    DB_PATH = db_path
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + db_path
    TESTING = True
