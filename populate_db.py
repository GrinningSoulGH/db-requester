import json
import random
import string
from http import HTTPMethod

from pydantic import BaseSettings
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from db_requester.db import Base, Request, RequestState


class ScriptSettings(BaseSettings):
    db_url: str


def get_random_string(length: int) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=length))


def get_random_dict() -> dict[str, str]:
    result = {}
    for i in range(random.randint(0, 5)):
        result[get_random_string(i + 1)] = get_random_string(i + 1)
    return result


def get_random_json_or_none() -> str | None:
    random_dict = get_random_dict()
    if len(random_dict) == 0:
        return None
    return json.dumps(random_dict)


def randomize_request() -> Request:
    return Request(
        uri=f"/{get_random_string(10)}",
        method=str(random.choice(list(HTTPMethod))),
        params=get_random_json_or_none(),
        headers=get_random_json_or_none(),
        state=RequestState.pending,
    )


def main():
    settings = ScriptSettings()
    engine = create_engine(settings.db_url)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        for request in [randomize_request() for _ in range(random.randint(20, 40))]:
            session.add(request)
        session.commit()


if __name__ == "__main__":
    main()
