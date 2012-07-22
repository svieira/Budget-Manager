from flask import flash, request, render_template
from flask.ext.admin.datastore.sqlalchemy import _form_for_model
from wtforms.fields import SubmitField

from models.base_model import db
from models.app_models import AutoTagElement
from models.data_models import Transaction


def add_tag_map():
        AutoTagElementForm = _form_for_model(AutoTagElement, db.session)
        AutoTagElementForm.submit = SubmitField("Search")
        AutoTagElementForm.continue_ = SubmitField("Add and Tag")

        results = []

        form = AutoTagElementForm(request.form)
        valid_post = request.method == "POST" and form.validate()

        if valid_post:
            results = [["Transaction"]]
            autotag = AutoTagElement()
            form.populate_obj(autotag)
            matches = [el for el in Transaction.query.all() if autotag.matches(el.description)]

        if valid_post and form.submit.data:
            flash("There are {} elements that will also be tagged.".format(len(matches)))

            results += [[unicode(el)] for el in matches]

        elif valid_post and form.continue_.data:
            db.session.add(autotag)
            db.session.commit()

            flash("{} added.".format(autotag))

            new_tags = set(autotag.tags)
            i = 0
            for transaction in matches:
                transaction.tags = list(set(transaction.tags) | new_tags)
                db.session.add(transaction)
                i += 1
            db.session.commit()
            flash("{} added to {} transactions.".format(new_tags, i))

        return render_template("report_with_form.html",
                                title="Add New Tag Map",
                                form=form,
                                results=results)
