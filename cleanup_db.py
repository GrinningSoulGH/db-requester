from pydantic import BaseSettings
from sqlalchemy import create_engine

from db_requester.db import Base


class ScriptSettings(BaseSettings):
    db_url: str


def main() -> None:
    settings = ScriptSettings()
    engine = create_engine(settings.db_url)
    Base.metadata.drop_all(engine)


if __name__ == "__main__":
    main()
