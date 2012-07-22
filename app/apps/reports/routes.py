from flask import Blueprint
from hip_pocket import Mapper

routes = Blueprint("reports", __name__, url_prefix="/reports")
mapper = Mapper(routes, base_import_name="apps.reports")

mapper.add_url_rule("/expense-by-category",
                        "static_reports.expense_by_category")
mapper.add_url_rule("/transactions-with-tags",
                        "static_reports.transactions_with_tags")
