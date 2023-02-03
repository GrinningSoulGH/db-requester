import functools
import logging
import sqlite3
from typing import Any, Callable

from ..config import DatabaseConfig, DatabaseCredentialsConfig

log = logging.getLogger(__name__)


def get_rdbms_connect(
    config: DatabaseConfig, credentials: DatabaseCredentialsConfig
) -> Callable:
    """Returns a PEP 249 compliant connect function"""
    match config.rdbms:
        case "sqlite":
            if credentials is not None:
                raise RuntimeError("Expected no credentials for an sqlite database")
            return functools.partial(sqlite3.connect, database=config.database_path)
        case _:
            raise RuntimeError(f"Unexpected RDBMS type: {config.rdbms}")


RDBMS_ERROR = (sqlite3.Error,)


class DatabaseConnector:
    def __init__(self, connect: Callable) -> None:
        self._connect = connect
