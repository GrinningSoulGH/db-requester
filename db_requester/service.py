import functools
import logging
import signal
import threading
import time
from multiprocessing.pool import ThreadPool
from pathlib import Path

import click
import sqlalchemy

from .config import S2Settings, ServiceSettings, config_from_yaml
from .db import Session
from .request import process_requests

log = logging.getLogger(__name__)


def graceful_shutdown(shutdown_flag: threading.Event, sig, frame) -> None:
    log.info("Starting service shutdown")
    shutdown_flag.set()


def setup_signal_handlers(handler) -> None:
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)


def run_service(settings: S2Settings, shutdown_flag: threading.Event) -> None:
    while not shutdown_flag.is_set():
        process_requests(settings)
        time.sleep(5)


def run_service_multithreaded(
    available_threads: int,
    settings: S2Settings,
    shutdown_flag: threading.Event,
) -> None:
    with ThreadPool() as thread_pool:
        while not shutdown_flag.is_set():
            for _ in range(available_threads):
                thread_pool.apply_async(functools.partial(process_requests, settings))
            thread_pool.join()
            time.sleep(5)


@click.command()
@click.option("--config", type=click.Path(exists=True))
def run(config: Path) -> None:
    shutdown_flag = threading.Event()
    setup_signal_handlers(functools.partial(graceful_shutdown, shutdown_flag))

    app_config = config_from_yaml(config)

    service_settings = ServiceSettings()

    s2_settings = S2Settings(
        url=app_config.s2.url,
        timeout=app_config.s2.response_timeout,
        login=service_settings.s2_login,
        password=service_settings.s2_password,
    )

    engine = sqlalchemy.create_engine(service_settings.db_url)

    Session.configure(bind=engine)

    # Main thread counts, so we subtract one
    available_threads = app_config.general.thread_count - 1

    log.info("Service start")
    if available_threads == 0:
        run_service(s2_settings, shutdown_flag)
    else:
        run_service_multithreaded(available_threads, s2_settings, shutdown_flag)
    log.info("Service shutdown")
