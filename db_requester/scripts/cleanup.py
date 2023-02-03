import argparse
import sqlite3

from .util import cleanup_requests
from .util import cleanup_responses


def main():
    parser = argparse.ArgumentParser(description="HTTP request relay service.")
    parser.add_argument("-p", "--path", help="Path to sqlite DB", required=True)

    cmd_args = parser.parse_args()
    with sqlite3.connect(cmd_args.path) as sqlite_connection:
        cursor = sqlite_connection.cursor()
        cleanup_requests(cursor)
        cleanup_responses(cursor)
        cursor.close()
