from flask import g
import sqlite3


def connect_db(app):
    return sqlite3.connect(app.config["DB_PATH"])


def query_db(query, args=(), include_header=True):
    results = []
    cur = g.db.execute(query, args)
    if include_header:
        results.append([desc[0] for desc in cur.description])
    results += [row for row in cur.fetchall()]
    return results
