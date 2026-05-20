"""Database helpers for Flask request-scoped access.

The original project targeted MySQL. This version keeps MySQL support, but
adds a SQLite backend so the app can run locally from source only.
"""

from __future__ import annotations

from pathlib import Path
import sqlite3

from flask import Flask, g

try:
    import MySQLdb  # type: ignore
except ImportError:  # pragma: no cover - optional dependency for local runs
    MySQLdb = None


connection_params: dict[str, object] = {}


class SQLiteCursorWrapper:
    def __init__(self, cursor: sqlite3.Cursor):
        self._cursor = cursor

    @staticmethod
    def _adapt_query(query: str) -> str:
        return query.replace("%s", "?")

    def execute(self, query: str, params=None):
        sql = self._adapt_query(query)
        if params is None:
            self._cursor.execute(sql)
        else:
            self._cursor.execute(sql, params)
        return self

    def fetchone(self):
        row = self._cursor.fetchone()
        return dict(row) if row is not None else None

    def fetchall(self):
        rows = self._cursor.fetchall()
        return [dict(row) for row in rows]

    @property
    def lastrowid(self):
        return self._cursor.lastrowid

    def close(self):
        self._cursor.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False


def init_db(
    app: Flask,
    user: str,
    password: str,
    host: str,
    database: str,
    port: int = 3306,
    autocommit: bool = True,
    backend: str = "mysql",
):
    connection_params["user"] = user
    connection_params["password"] = password
    connection_params["host"] = host
    connection_params["database"] = database
    connection_params["port"] = port
    connection_params["autocommit"] = autocommit
    connection_params["backend"] = backend

    app.config["DB_BACKEND"] = backend
    app.config["DATABASE"] = database
    app.teardown_appcontext(close_db)


def _connect_sqlite(database: str, autocommit: bool):
    db_path = Path(database)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    if autocommit:
        connection.isolation_level = None
    return connection


def _connect_mysql():
    if MySQLdb is None:
        raise RuntimeError(
            "MySQL backend requested but mysqlclient is not installed."
        )
    mysql_params = {
        key: value
        for key, value in connection_params.items()
        if key in {"user", "password", "host", "database", "port", "autocommit"}
    }
    return MySQLdb.connect(**mysql_params)


def get_db():
    if "db" not in g:
        backend = connection_params.get("backend", "mysql")
        if backend == "sqlite":
            g.db = _connect_sqlite(
                str(connection_params["database"]),
                bool(connection_params.get("autocommit", True)),
            )
        else:
            g.db = _connect_mysql()
    return g.db


def get_cursor():
    connection = get_db()
    if connection_params.get("backend") == "sqlite":
        return SQLiteCursorWrapper(connection.cursor())
    return connection.cursor(cursorclass=MySQLdb.cursors.DictCursor)


def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def ensure_schema(app: Flask):
    if app.config["DB_BACKEND"] != "sqlite":
        return

    schema_path = Path(__file__).with_name("schema.sql")
    with app.app_context():
        connection = get_db()
        with schema_path.open("r", encoding="utf-8") as schema_file:
            connection.executescript(schema_file.read())
        _migrate_sqlite_schema(connection)


def _migrate_sqlite_schema(connection: sqlite3.Connection):
    columns = {
        row["name"]
        for row in connection.execute("PRAGMA table_info(internships)").fetchall()
    }
    if "skills_required" not in columns:
        connection.execute("ALTER TABLE internships ADD COLUMN skills_required TEXT")
    if "number_of_opening" not in columns:
        connection.execute(
            "ALTER TABLE internships ADD COLUMN number_of_opening INTEGER DEFAULT 1"
        )
    if "number_opening" in columns and "number_of_opening" in {
        row["name"]
        for row in connection.execute("PRAGMA table_info(internships)").fetchall()
    }:
        connection.execute(
            """
            UPDATE internships
            SET number_of_opening = COALESCE(number_of_opening, number_opening)
            """
        )
    connection.execute(
        """
        UPDATE users
        SET profile_image = 'images/default.jpg'
        WHERE profile_image = 'images/default.JPG'
        """
    )
    connection.execute(
        """
        UPDATE employers
        SET logo_path = 'images/default.jpg'
        WHERE logo_path = 'images/default.JPG'
        """
    )
