"""Runtime database configuration for local development.

Defaults to SQLite so the project can run locally with zero external
infrastructure. MySQL is still supported if matching environment variables are
provided.
"""

from __future__ import annotations

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_SQLITE_PATH = BASE_DIR / "instance" / "internship.sqlite3"

dbbackend = os.environ.get("APP_DB_BACKEND", "sqlite").lower()
dbuser = os.environ.get("APP_DB_USER", "")
dbpass = os.environ.get("APP_DB_PASSWORD", "")
dbhost = os.environ.get("APP_DB_HOST", "127.0.0.1")
dbport = int(os.environ.get("APP_DB_PORT", "3306"))
dbname = os.environ.get("APP_DB_NAME", str(DEFAULT_SQLITE_PATH))
