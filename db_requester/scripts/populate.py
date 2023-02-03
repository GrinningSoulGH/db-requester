import argparse
import sqlite3

from .util import populate_requests, populate_responses


def main():
    parser = argparse.ArgumentParser(description="HTTP request relay service.")
    parser.add_argument("-p", "--path", help="Path to sqlite DB", required=True)

    cmd_args = parser.parse_args()
    with sqlite3.connect(cmd_args.path) as sqlite_connection:
        cursor = sqlite_connection.cursor()
        populate_requests(cursor)
        populate_responses(cursor)
        cursor.close()
