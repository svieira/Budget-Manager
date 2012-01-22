from base_model import BaseModel, db
from re import compile, IGNORECASE
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func

AutoTagMapping = db.Table("AutoTagToTags", db.metadata,
    db.Column("autoTagID", db.Integer, db.ForeignKey("AutoTagElements.autoTagID")),
    db.Column("tagID", db.Integer, db.ForeignKey("TransactionTags.tagID"))
)


class AutoTagElement(db.Model, BaseModel):
    __tablename__ = "AutoTagElements"
    autoTagID = db.Column(db.Integer, primary_key=True, nullable=False)
    SearchString = db.Column("search_string", db.String, nullable=False)
    IsRegex = db.Column("isRegex", db.Boolean, nullable=False, default=0)
    created = db.Column(db.Date, nullable=False)  # , default=func.now
    last_updated = db.Column(db.Date, nullable=True)

    tags = db.relationship("TransactionTag", secondary=AutoTagMapping)

    @hybrid_property
    def search_string(self):
        # TODO: Check werkzeug's cachedproperty decorator to see
        # if it can cover this use case.
        search_string = self.SearchString
        is_cached = getattr(self, "_search_string_cached", False) and \
                        self._search_string_cached.pattern == self.SearchString

        if self.isRegex and not is_cached:
            search_string = compile(search_string, IGNORECASE)
            self._search_string_cached = search_string
        elif self.isRegex:
            search_string = self._search_string_cached

        return search_string

    @search_string.setter
    def search_string(self, search_string):
        self.SearchString = search_string

    @hybrid_property
    def isRegex(self):
        return self.IsRegex

    @isRegex.setter
    def isRegex(self, val):
        self.IsRegex = 1 if val else 0
        if self.IsRegex and isinstance(self.search_string, (str, unicode)):
            self.search_string = self.search_string
        else:
            self.search_string = self.search_string.pattern

    def __repr__(self):
        addenda = " (Regex)" if self.isRegex else ""
        search_string = getattr(self.search_string, "pattern", self.search_string)
        return "{} {}{}".format(search_string, self.tags, addenda)

    def matches(self, entry):
        search_string = self.search_string
        if self.isRegex:
            return (search_string.search(entry) is not None)
        else:
            return entry.count(search_string) > 0
