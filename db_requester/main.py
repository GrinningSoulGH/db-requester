import logging
from pathlib import Path
import logging
import argparse
from .config import parse_config, parse_credentials
from .service import run_service

logging.basicConfig(
    format="[%(asctime)s]: %(levelname)s %(message)s", level=logging.INFO
)

log = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="HTTP request database relay service.")
    parser.add_argument("-c", "--config", help="Path to config file", required=True)
    parser.add_argument("--cred", help="Path to credentials file", required=True)

    cmd_args = parser.parse_args()
    config = parse_config(Path(cmd_args.config))
    credentials = parse_credentials(Path(cmd_args.cred))

    run_service(config, credentials)
