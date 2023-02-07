import logging

from db_requester.service import run

logging.basicConfig(
    format="[%(asctime)s]: %(levelname)s %(message)s", level=logging.INFO
)

if __name__ == "__main__":
    run()
