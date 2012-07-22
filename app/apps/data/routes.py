from flask import Blueprint
from hip_pocket import Mapper

routes = Blueprint("data", __name__)
mapper = Mapper(routes,
                base_import_name="apps.data",
                methods=["GET", "POST"])

mapper.add_url_rule("/add-tag-map",
                        "tag_mapper.add_tag_map")

mapper.add_url_rule("/import",
                        "load.provide_file")
mapper.add_url_rule("/import/<path:filename>",
                        "load.data_mapping")

mapper.add_url_rule("/search", "search.search")
mapper.add_url_rule("/search/<model>", "search.search")
