import logging
import random
import string
import threading
from typing import Generator, Iterable

from ..config import S2Config, S2CredentialsConfig
from ..models import Request, Response
from ..threads import IterableQueue

log = logging.getLogger(__name__)


class S2Communicator:
    def __init__(self, config: S2Config, credentials: S2CredentialsConfig) -> None:
        self._response_timeout = config.response_timeout
        self.response_code_getter = random_response_code
        self.body_getter = random_response_body

    def start(self, requests: Iterable[Request]) -> Iterable[Response]:
        return self.get_responses(requests)

    def wait(self) -> None:
        pass

    def get_responses(
        self, requests: Iterable[Request]
    ) -> Generator[Response, None, None]:
        for request in requests:
            yield Response(
                request_id=request.id,
                status_code=self.response_code_getter(),
                body=self.body_getter(),
            )


class ThreadedS2Communicator(S2Communicator):
    _threads: list[threading.Thread] | None = None

    def __init__(
        self, config: S2Config, credentials: S2CredentialsConfig, thread_count: int
    ) -> None:
        super().__init__(config, credentials)
        self._thread_count = thread_count

    def start(self, requests: IterableQueue) -> None:
        """Requests has to be IterableQueue, because this IterableQueue implementation doesn't work with spmc/mpmc"""
        self._threads = []
        result = IterableQueue(100)

        def add_responses_to_queue():
            for request in self.get_responses(requests):
                result.put(request)
            # Without this other threads still iterating over the queue won't stop iterating. Dirty.
            # TODO: design a mpmc thread-safe closable iterator.
            requests.close()
            result.close()

        for _ in range(self._thread_count):
            thread = threading.Thread(target=add_responses_to_queue)
            thread.start()
            self._threads.append(thread)

        return result

    def wait(self) -> None:
        if self._threads is None:
            return
        for thread in self._threads:
            thread.join()


def random_response_code() -> int:
    response_codes = [200, 202, 204, 301, 307, 400, 401, 403, 404, 500, 503]
    return random.choice(response_codes)


def random_response_body() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=30))
