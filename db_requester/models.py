from pydantic import BaseModel


class Request(BaseModel):
    id: int
    uri: str
    method: str
    params: dict[str, str] | None
    headers: dict[str, str] | None


class Response(BaseModel):
    request_id: int
    status_code: int
    body: str
