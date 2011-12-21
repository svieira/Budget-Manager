from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

db = SQLAlchemy()


class Account(db.Model):
    __tablename__ = "Accounts"
    __table_args__ = {'sqlite_autoincrement': True}

    accountID = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    isCredit = db.Column(db.Boolean, default=0, nullable=False)

    transactions = db.relationship("Transaction", backref="account")

    def __repr__(self):
        return "{} Account".format(self.name)


class Category(db.Model):
    __tablename__ = "Categories"
    __table_args__ = {'sqlite_autoincrement': True}

    categoryID = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)

    tags = db.relationship("TransactionTag", backref="category")

    def __repr__(self):
        return "{}".format(self.name)


class TransactionType(db.Model):
    __tablename__ = "TransactionTypes"
    __table_args__ = {'sqlite_autoincrement': True}

    transactionTypeID = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    isIncome = db.Column(db.Boolean, default=0, nullable=False)

    transactions = db.relationship("Transaction", backref="transaction_type")

    def __repr__(self):
        kind = "Income" if self.isIncome else "Spending"
        return "{} ({})".format(self.name, kind)


class TransactionsToTags(db.Model):
    __tablename__ = "TransactionsToTags"
    transactionID = db.Column(db.Integer, db.ForeignKey("Transactions.transactionID"), primary_key=True)
    tagID = db.Column(db.Integer, db.ForeignKey("TransactionTags.tagID"), primary_key=True)


def get_trans_id():
    max_trans_id = Transaction.query.with_entities(func.max(Transaction.transactionID).label("transactionID")).first().transactionID
    return max_trans_id + 1


class Transaction(db.Model):
    __tablename__ = "Transactions"
    __table_args__ = {'sqlite_autoincrement': True}

    transactionID = db.Column(db.Integer, primary_key=True, nullable=False, default=get_trans_id)
    amount = db.Column(db.Numeric, nullable=False)
    description = db.Column(db.String, nullable=False)
    transactionDate = db.Column(db.DateTime, nullable=False)
    transactionTypeID = db.Column(db.Integer,
                                    db.ForeignKey("TransactionTypes.transactionTypeID"),
                                    nullable=False)
    accountID = db.Column(db.Integer,
                            db.ForeignKey("Accounts.accountID"),
                            nullable=False)

    tags = db.relationship("TransactionTag", secondary=TransactionsToTags.__table__)

    def __repr__(self):
        return "{} for {} on {}".format(self.description, self.amount, self.transactionDate)


class TransactionTag(db.Model):
    __tablename__ = "TransactionTags"
    __table_args__ = {'sqlite_autoincrement': True}

    tagID = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    categoryID = db.Column(db.Integer, db.ForeignKey("Categories.categoryID"), nullable=False)

    def __repr__(self):
        return "{} ({})".format(self.name, self.category.name)
