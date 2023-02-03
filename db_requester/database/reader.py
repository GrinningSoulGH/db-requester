import json
import logging
import queue
import threading
import time
from contextlib import closing
from typing import Any, Callable, Generator, Iterable

from ..models import Request
from ..threads import IterableQueue
from .connector import RDBMS_ERROR, DatabaseConnector

log = logging.getLogger(__name__)


GET_LAST_REQUEST_ID_QUERY = (
    "select request_id from queue_requests ORDER BY request_id DESC LIMIT 1;"
)

GET_LAST_RESPONSE_ID_QUERY = (
    "select request_id from queue_responses ORDER BY request_id DESC LIMIT 1;"
)

GET_ROWS_QUERY = "select request_id, uri, method, params, headers from queue_requests where request_id > ? ORDER BY request_id"


class DatabaseReader(DatabaseConnector):
    def __init__(
        self,
        connect: Callable,
        shutdown_flag: threading.Event,
    ) -> None:
        super().__init__(connect)
        self._shutdown_flag = shutdown_flag

    def start(self) -> Iterable[Request]:
        return self.get_requests()

    def wait(self) -> None:
        pass

    def get_requests(self) -> Generator[Request, None, None]:
        """Returns a blocking generator of Requests from the database until shutdown flag is set.
        Database connection is re-established every cycle due to a considerable simplification of
        error handling."""
        last_queried_id = 0
        while not self._shutdown_flag.is_set():
            for request in self._get_requests(last_queried_id):
                yield request
                last_queried_id = request.id
            time.sleep(5)

    def _get_requests(self, last_id: int) -> Generator[Request, None, None]:
        """Returns a blocking generator of Requests from the database. Generator stops yielding
        on either a database error or end of old requests"""
        try:
            with self._connect(timeout=5) as connection:
                yield from self._query_requests(connection, last_id)
        except RDBMS_ERROR as e:
            log.error(f"Error while trying to read from the database: {e}")

    def _query_requests(
        self, connection, last_id: int
    ) -> Generator[Request, None, None]:
        with closing(connection.cursor()) as cursor:
            last_response_id = (
                last_id if last_id != 0 else self.get_last_response_id(cursor)
            )
            if self.get_last_request_id(cursor) > last_response_id:
                yield from map(
                    lambda row: Request(
                        id=row[0],
                        uri=row[1],
                        method=row[2],
                        params=json.loads(row[3]) if row[3] is not None else None,
                        headers=json.loads(row[4]) if row[4] is not None else None,
                    ),
                    self.read_rows(cursor, last_response_id),
                )

    @staticmethod
    def get_last_request_id(cursor) -> int:
        cursor.execute(GET_LAST_REQUEST_ID_QUERY)
        if (row := cursor.fetchone()) is None:
            return 0
        return row[0]

    @staticmethod
    def get_last_response_id(cursor) -> int:
        cursor.execute(GET_LAST_RESPONSE_ID_QUERY)
        if (row := cursor.fetchone()) is None:
            return 0
        return row[0]

    @staticmethod
    def read_rows(cursor, last_response_id: int) -> Generator[list[Any], None, None]:
        cursor.execute(GET_ROWS_QUERY, (last_response_id,))
        while results := cursor.fetchmany(10):
            yield from results


class ThreadedDatabaseReader(DatabaseReader):
    _thread: threading.Thread | None = None

    def start(self) -> Iterable[Request]:
        result = IterableQueue(100)

        def add_results_to_queue():
            for request in self.get_requests():
                result.put(request)
            result.close()

        self._thread = threading.Thread(target=add_results_to_queue)
        self._thread.start()

        return result

    def wait(self):
        if self._thread is not None:
            self._thread.join()
