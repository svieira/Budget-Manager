from base_model import BaseModel, db


class Account(db.Model, BaseModel):
    __tablename__ = "Accounts"

    accountID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    isCredit = db.Column(db.Boolean, default=0, nullable=False)

    transactions = db.relationship("Transaction", backref="account")

    def __repr__(self):
        return "{} Account".format(self.name)


class Category(db.Model, BaseModel):
    __tablename__ = "Categories"

    categoryID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)

    tags = db.relationship("TransactionTag", backref="category")

    def __repr__(self):
        return self.name


class TransactionType(db.Model, BaseModel):
    __tablename__ = "TransactionTypes"

    transactionTypeID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    isIncome = db.Column(db.Boolean, default=0, nullable=False)

    transactions = db.relationship("Transaction", backref="transaction_type")

    def __repr__(self):
        kind = "Income" if self.isIncome else "Spending"
        return "{} ({})".format(self.name, kind)

TransactionToTagMapping = db.Table("TransactionsToTags", db.metadata,
    db.Column("transactionID", db.Integer, db.ForeignKey("Transactions.transactionID"), primary_key=True),
    db.Column("tagID", db.Integer, db.ForeignKey("TransactionTags.tagID"), primary_key=True)
)


class Transaction(db.Model, BaseModel):
    __tablename__ = "Transactions"

    transactionID = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric, nullable=False)
    description = db.Column(db.String, nullable=False)
    transactionDate = db.Column(db.DateTime, nullable=False)
    transactionTypeID = db.Column(db.Integer,
                                    db.ForeignKey("TransactionTypes.transactionTypeID"),
                                    nullable=False)
    accountID = db.Column(db.Integer,
                            db.ForeignKey("Accounts.accountID"),
                            nullable=False)

    tags = db.relationship("TransactionTag", secondary=TransactionToTagMapping)

    def __repr__(self):
        return "{} for {} on {}".format(self.description, self.amount, self.transactionDate)


class TransactionTag(db.Model, BaseModel):
    __tablename__ = "TransactionTags"

    tagID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    categoryID = db.Column(db.Integer, db.ForeignKey("Categories.categoryID"))

    def __repr__(self):
        return "{} ({})".format(self.name, self.category.name)
