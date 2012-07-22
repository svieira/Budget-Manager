from flask import abort, flash, Markup, render_template, request, url_for
from sqlalchemy import or_

from models.base_model import db
from models.data_models import Account, Category, TransactionType, Transaction, TransactionTag


MANAGED_MODEL_MAP = dict(account=Account,
                            category=Category,
                            transactiontype=TransactionType,
                            transaction=Transaction,
                            transactiontag=TransactionTag)


def search(model=None):
    query = request.form.get("query", None) or request.args.get("query", None)
    results = []
    if not query:
        return render_template("search.html")

    def generate_search_terms(model):
        search_terms = []
        for term in ["name", "description", "amount", "transactionDate"]:
            if hasattr(model, term):
                search_terms.append(term)
        return [getattr(model, term).like(query) for term in search_terms]

    def generate_links(query_list, model=None, model_key=None):
        link = Markup("""<a href="{}">{}</a> - <a href="{}">Delete</a>""")
        model_key = [key.key for key in model_key.columns][0]
        for entry in query_list:
            key = getattr(entry, model_key, 1)
            name = model.__name__
            edit_url = url_for('admin.edit', model_name=name, model_url_key=key)
            delete_url = url_for('admin.delete', model_name=name, model_url_key=key)
            yield link.format(edit_url, entry, delete_url)

    flash("""Searching for "{}" ...""".format(query))
    if query.count("%") == 0:
        query = "%{}%".format(query)
    if model is None:
        for model_name, model in MANAGED_MODEL_MAP.items():
            search_terms = generate_search_terms(model)
            data = db.session.query(model).filter(or_(*search_terms)).all()
            data = list(generate_links(data, model, model.__table__.primary_key))
            results.append((model_name, data))
        return render_template("search.html", results=results)
    else:
        if not model.lower() in MANAGED_MODEL_MAP:
            return abort(404)
        flash("""Searching for "{}" in {} ...""".format(query, model))
        model_ = MANAGED_MODEL_MAP.get(model)
        search_terms = generate_search_terms(model_)
        results = [(model, db.session.query(model_).filter(or_(*search_terms)))]
        return render_template("search.html", results=results)
