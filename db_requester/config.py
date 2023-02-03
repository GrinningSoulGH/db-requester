import yaml
from pydantic import BaseModel, constr, conint, AnyHttpUrl
from pathlib import Path
import logging


log = logging.getLogger(__name__)


class RealDatabaseCredentialsConfig(BaseModel):
    user: str
    password: str


DatabaseCredentialsConfig = RealDatabaseCredentialsConfig | None


class S2CredentialsConfig(BaseModel):
    login: str
    password: str


class CredentialsConfig(BaseModel):
    database: DatabaseCredentialsConfig
    s2: S2CredentialsConfig


class SqliteConfig(BaseModel):
    rdbms: constr(regex=r"^sqlite$")
    database_path: Path


DatabaseConfig = SqliteConfig


class GeneralConfig(BaseModel):
    thread_count: conint(ge=1, le=100)


class S2Config(BaseModel):
    response_timeout: int
    url: AnyHttpUrl


class AppConfig(BaseModel):
    general: GeneralConfig
    database: DatabaseConfig
    s2: S2Config


def parse_from_yaml(path):
    with open(path) as f:
        config = yaml.safe_load(f)
    return config


def parse_config(path: Path) -> AppConfig:
    return AppConfig(**parse_from_yaml(path))


def parse_credentials(path: Path) -> CredentialsConfig:
    return CredentialsConfig(**parse_from_yaml(path))
