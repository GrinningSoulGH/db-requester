import logging
import json
import threading
from urllib.parse import urljoin

import requests
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from db_requester.config import S2Settings

from .db import RequestState, Response, Session, Request

log = logging.getLogger(__name__)


def process_requests(s2_settings: S2Settings) -> None:
    try:
        _process_requests(s2_settings)
    except SQLAlchemyError:
        log.exception("Database error occured")


def _process_requests(s2_settings: S2Settings) -> None:
    with Session() as session:
        for request in session.execute(
            select(Request)
            .where(Request.state == RequestState.pending)
            .with_for_update(skip_locked=True)
            .limit(5)
        ).scalars():
            try:
                result = requests.request(
                    request.method.value,
                    urljoin(s2_settings.url, request.uri),
                    params=json.loads(request.params)
                    if request.params is not None
                    else None,
                    headers=json.loads(request.headers)
                    if request.headers is not None
                    else None,
                    timeout=s2_settings.timeout,
                    auth=(s2_settings.login, s2_settings.password),
                )
            except requests.ConnectTimeout:
                log.warn("Timed out while connecting to S2")
                continue
            except requests.RequestException:
                log.exception("Unrecoverable error while connecting to S2")
                request.state = RequestState.failed
                continue
            request.response = Response(
                status_code=result.status_code, body=result.text
            )
            request.state = RequestState.processed
        session.commit()
