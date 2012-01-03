from flask import Flask, g
import sqlite3


def connect_db(path_provider, config_key="DB_PATH"):
    if isinstance(path_provider, Flask):
        return sqlite3.connect(path_provider.config[config_key])
    else:
        return sqlite3.connect(path_provider)


def query_db(query, args=(), include_header=True, conn=None):
    conn = conn if conn else g.db
    assert conn is not None, "No connection provided"

    cur = conn.execute(query, args)

    if include_header:
        yield [desc[0] for desc in cur.description]

    row = cur.fetchone()
    while row is not None:
        yield row
        row = cur.fetchone()
