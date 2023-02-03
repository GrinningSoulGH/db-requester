import functools
import signal
import sqlite3
import threading
import logging
import time
import json

from .s2.communicator import S2Communicator, ThreadedS2Communicator
from .threads import ThreadCounter
from .database.connector import get_rdbms_connect
from .database.reader import DatabaseReader, ThreadedDatabaseReader
from .database.writer import DatabaseWriter, ThreadedDatabaseWriter
from .config import (
    AppConfig,
    CredentialsConfig,
    DatabaseConfig,
    DatabaseCredentialsConfig,
)

log = logging.getLogger(__name__)


def graceful_shutdown(shutdown_flag: threading.Event, sig, frame):
    """Graceful shutdown initiation."""
    log.info("Starting service shutdown")
    shutdown_flag.set()


def make_db_connection(
    db_config: DatabaseConfig, db_credentials: DatabaseCredentialsConfig
):
    """Function making the database connections. Returns PEP249 compliant Connection object."""
    match db_config.rdbms:
        case "sqlite":
            return sqlite3.connect(db_config.database_path)
        case _:
            raise RuntimeError(f"RDBMS {db_config.rdbms} not supported")


def setup_signal_handlers(handler):
    """Setup service signal handlers"""
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)


class Service:
    def __init__(
        self,
        config: AppConfig,
        credentials: CredentialsConfig,
        shutdown_flag: threading.Event,
    ) -> None:
        rdbms_connect = get_rdbms_connect(config.database, credentials.database)
        thread_counter = ThreadCounter(config.general.thread_count - 1)
        if thread_counter.one():
            self._database_reader = ThreadedDatabaseReader(rdbms_connect, shutdown_flag)
        else:
            self._database_reader = DatabaseReader(rdbms_connect, shutdown_flag)
        pools = thread_counter.pool(2)
        if pools[0] != 0:
            self._s2communicator = ThreadedS2Communicator(
                config.s2, credentials.s2, pools[0]
            )
        else:
            self._s2communicator = S2Communicator(config.s2, credentials.s2)
        if pools[1] != 0:
            self._database_writer = ThreadedDatabaseWriter(rdbms_connect, pools[1])
        else:
            self._database_writer = DatabaseWriter(rdbms_connect)

    def run(self) -> None:
        """Running the service. Blocks until shutdown_flag is set."""
        rows = self._database_reader.start()
        responses = self._s2communicator.start(rows)
        self._database_writer.start(responses)

        self._database_reader.wait()
        self._s2communicator.wait()
        self._database_writer.wait()


def run_service(config: AppConfig, credentials: CredentialsConfig) -> None:
    shutdown_flag = threading.Event()
    setup_signal_handlers(functools.partial(graceful_shutdown, shutdown_flag))

    log.info("Service running with config: %s", config.json())
    service = Service(config, credentials, shutdown_flag)
    service.run()
    log.info("Service shutdown")
