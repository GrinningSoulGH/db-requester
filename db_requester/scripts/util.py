import sqlite3
import json
from typing import Any


def populate_requests(cursor: sqlite3.Cursor) -> None:
    cursor.execute(
        "create table IF NOT EXISTS queue_requests (request_id INTEGER PRIMARY KEY, uri varchar(255) not null, method char(7) not null, params text, headers text)"
    )
    params = {"things": "stuff", "a": "b"}
    headers = {"Content-Stuff": "stuff", "Content-Length": "b"}
    cursor.execute(
        f"insert into queue_requests (uri, method, params, headers) values ('/wiki', 'GET', '{json.dumps(params)}', '{json.dumps(headers)}')"
    )
    cursor.execute(f"insert into queue_requests (uri, method) values ('/wiki', 'GET')")


def populate_responses(cursor: sqlite3.Cursor) -> None:
    cursor.execute(
        "create table IF NOT EXISTS queue_responses (response_id INTEGER PRIMARY KEY, request_id INTEGER REFERENCES queue_requests UNIQUE, status_code INTEGER, body TEXT)"
    )


def query_requests(cursor: sqlite3.Cursor) -> list[Any]:
    return _query("queue_requests", cursor)


def query_responses(cursor: sqlite3.Cursor) -> list[Any]:
    return _query("queue_responses", cursor)


def _query(table_name: str, cursor: sqlite3.Cursor) -> list[Any]:
    sqlite_select_query = f"select * from {table_name};"
    cursor.execute(sqlite_select_query)
    return cursor.fetchall()


def cleanup_requests(cursor: sqlite3.Cursor) -> None:
    _cleanup("queue_requests", cursor)


def cleanup_responses(cursor: sqlite3.Cursor) -> None:
    _cleanup("queue_responses", cursor)


def _cleanup(table_name: str, cursor: sqlite3.Cursor) -> None:
    cursor.execute(f"drop table {table_name}")
