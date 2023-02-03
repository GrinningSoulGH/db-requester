import logging
import threading
import time
from contextlib import closing
from itertools import islice
from typing import Callable, Iterable

from ..models import Response
from .connector import DatabaseConnector, RDBMS_ERROR

log = logging.getLogger(__name__)


def batched(iterable: Iterable, n: int):
    "Batch data into lists of length n. The last batch may be shorter."
    # batched('ABCDEFG', 3) --> ABC DEF G
    it = iter(iterable)
    while True:
        batch = list(islice(it, n))
        if not batch:
            return
        yield batch


class DatabaseWriter(DatabaseConnector):
    def start(self, responses: Iterable[Response]) -> None:
        self.insert_responses(responses)

    def wait(self) -> None:
        pass

    def insert_responses(self, responses: Iterable[Response]) -> None:
        for batched_responses in batched(responses, 2):
            self._insert_responses(batched_responses)

    def _insert_responses(self, responses: Iterable[Response]) -> None:
        timer = time.time()
        while time.time() - timer < 10.0:
            try:
                with self._connect(timeout=5) as connection:
                    with closing(connection.cursor()) as cursor:
                        cursor.executemany(
                            "INSERT INTO queue_responses (request_id, status_code, body) VALUES (?, ?, ?);",
                            map(
                                lambda response: [
                                    response.request_id,
                                    response.status_code,
                                    response.body,
                                ],
                                responses,
                            ),
                        )
                        return
            except RDBMS_ERROR as e:
                log.error(f"Error while trying to write to the database: {e}")
                time.sleep(1)
        log.error("Failed to write data to database: %s", list(responses))


class ThreadedDatabaseWriter(DatabaseWriter):
    _threads: list[threading.Thread] | None = None

    def __init__(self, connect: Callable, thread_count: int) -> None:
        super().__init__(connect)
        self._thread_count = thread_count

    def start(self, responses: Iterable[Response]) -> None:
        self._threads = []
        for _ in range(self._thread_count):
            thread = threading.Thread(target=self.insert_responses, args=[responses])
            thread.start()
            self._threads.append(thread)

    def wait(self) -> None:
        if self._threads is None:
            return
        for thread in self._threads:
            thread.join()
