import argparse
import sqlite3

from .util import query_requests, query_responses


def main():
    parser = argparse.ArgumentParser(description="HTTP request relay service.")
    parser.add_argument("-p", "--path", help="Path to sqlite DB", required=True)

    cmd_args = parser.parse_args()
    with sqlite3.connect(cmd_args.path) as sqlite_connection:
        cursor = sqlite_connection.cursor()
        print(
            "Contents of the queue_requests table: ", query_requests(cursor), flush=True
        )
        print(
            "Contents of the queue_responses table: ",
            query_responses(cursor),
            flush=True,
        )
        cursor.close()
