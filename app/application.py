from flask import Flask
from flask.ext import admin
from hip_pocket.tasks import autoload
from models.base_model import db
from models.app_models import AutoTagElement
from models.data_models import Account, Category, TransactionType, Transaction, TransactionTag

MANAGED_MODELS = [Account, AutoTagElement, Category, TransactionType, Transaction, TransactionTag]


def create_app(config_path=None, name=None):
    """Creates a flask application instance and loads its config from config_path

    :param config_path: A string representing either a file path or an import path
    :returns: An instance of `flask.Flask`."""

    app = Flask(name or __name__)
    app.config.from_object('server.config.DebugConfig')
    app.config.from_envvar(config_path or '', silent=True)

    db.init_app(app)

    admin_blueprint = admin.create_admin_blueprint(MANAGED_MODELS, db.session)
    app.register_blueprint(admin_blueprint, url_prefix="/tables")

    autoload(app)

    return app
