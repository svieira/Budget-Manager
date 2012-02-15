from application import create_app
from models.base_model import db
from flask.ext.script import Manager

app = create_app()
command_runner = Manager(app)


@command_runner.command
def create_db():
    """Creates the necessary tables in the database
    specified in the `DB_PATH` config variable."""

    print "Initializing budget tables ..."
    db.metadata.create_all(db.engine)


if __name__ == "__main__":
    command_runner.run()
