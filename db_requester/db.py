import enum
from http import HTTPMethod

from sqlalchemy import ForeignKey
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    scoped_session,
    sessionmaker,
)
from sqlalchemy.types import String, Text

Session = scoped_session(sessionmaker())


class Base(DeclarativeBase):
    pass


class RequestState(enum.Enum):
    pending = "PENDING"
    processed = "PROCESSED"
    failed = "FAILED"


class Request(Base):
    __tablename__ = "queue_requests"

    request_id: Mapped[int] = mapped_column(primary_key=True)
    uri: Mapped[str] = mapped_column(String(255))
    method: Mapped[HTTPMethod]
    params: Mapped[str | None] = mapped_column(Text)
    headers: Mapped[str | None] = mapped_column(Text)
    state: Mapped[RequestState]

    response: Mapped["Response"] = relationship(back_populates="request")

    def __repr__(self) -> str:
        return f"QueueRequests(request_id={self.request_id!r}, uri={self.uri!r}, method={self.method!r}, params={self.params!r}, headers={self.headers!r})"


class Response(Base):
    __tablename__ = "queue_responses"

    response_id: Mapped[int] = mapped_column(primary_key=True)
    status_code: Mapped[int]
    body: Mapped[str | None] = mapped_column(Text)

    request_id: Mapped[int] = mapped_column(ForeignKey("queue_requests.request_id"))
    request: Mapped["Request"] = relationship(back_populates="response")

    def __repr__(self) -> str:
        return f"QueueRepsonses(response_id={self.id!r}, status_code={self.status_code!r}, body = {self.body!r})"
