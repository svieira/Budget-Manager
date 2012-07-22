from flask import render_template
from sqlalchemy import func

from models.base_model import db
from models.data_models import (Category, Transaction, TransactionTag,
                                TransactionToTagMapping)
from utils.database import generate_result_set


def transactions_with_tags():
    results = Transaction.query.outerjoin(Transaction.tags).all()
    results = [["Transaction", "Tags"]] + [[unicode(el), unicode(el.tags)] for el in results]
    return render_template("report_layout.html", results=results, title="Transactions with tags")


def expense_by_category():
    results = db.session.query(Category.name.label("Category Name"),
                                Category.description.label("Category Description"),
                                func.sum(Transaction.amount).label("Total Spend")). \
                            outerjoin(TransactionTag). \
                            outerjoin(TransactionToTagMapping). \
                            outerjoin(Transaction). \
                            group_by(Category.name, Category.description)
    results = generate_result_set(results)
    return render_template("report_layout.html", results=results, title="Expense by category")
