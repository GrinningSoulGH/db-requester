from pydantic import BaseSettings
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from db_requester.db import Request, RequestState


class ScriptSettings(BaseSettings):
    db_url: str


def main() -> None:
    settings = ScriptSettings()
    engine = create_engine(settings.db_url)
    with Session(engine) as session:
        print(
            "Unprocessed requests: ",
            session.execute(
                select(Request.request_id).where(Request.state == RequestState.pending)
            ).all(),
        )


if __name__ == "__main__":
    main()
