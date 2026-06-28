from __future__ import annotations

import sqlite3
from pathlib import Path


def sqlite_path_from_url(database_url: str) -> Path:
    """Resolve a sqlite URL or path into a filesystem path."""
    if database_url.startswith("sqlite:///"):
        return Path(database_url.removeprefix("sqlite:///"))
    if database_url.startswith("sqlite://"):
        return Path(database_url.removeprefix("sqlite://"))
    return Path(database_url)


def connect(database_url: str) -> sqlite3.Connection:
    """Create a SQLite connection with row dictionaries enabled."""
    db_path = sqlite_path_from_url(database_url)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection
