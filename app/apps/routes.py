from flask import Blueprint
from hip_pocket import Mapper

routes = Blueprint("app", __name__)
mapper = Mapper(routes, base_import_name="apps")

mapper.add_url_rule("/", "index.index")
mapper.add_url_rule("/<table_name>", "index.view_table")
