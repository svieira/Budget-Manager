from base_model import BaseModel, db

AutoTagMapping = db.Table("AutoTagToTags", db.metadata,
    db.Column("autoTagID", db.Integer, db.ForeignKey("AutoTagElements.autoTagID")),
    db.Column("tagID", db.Integer, db.ForeignKey("TransactionTags.tagID"))
)


class AutoTagElement(db.Model, BaseModel):
    __tablename__ = "AutoTagElements"
    autoTagID = db.Column(db.Integer, primary_key=True, nullable=False)
    search_string = db.Column(db.String, nullable=False)
    isRegex = db.Column(db.Boolean, nullable=False, default=0)
    created = db.Column(db.Date, nullable=False)
    last_updated = db.Column(db.Date, nullable=True)

    tags = db.relationship("TransactionTag", secondary=AutoTagMapping)
