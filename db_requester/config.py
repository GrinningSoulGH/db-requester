from pathlib import Path

import yaml
from pydantic import BaseModel, BaseSettings, AnyHttpUrl, confloat, conint


class ServiceSettings(BaseSettings):
    """Env variables supported by service"""

    db_url: str
    s2_login: str
    s2_password: str


class GeneralConfig(BaseModel):
    """Service's general config section"""

    thread_count: conint(ge=1, le=100)


class S2Config(BaseModel):
    """Service's s2 config section"""

    response_timeout: confloat(gt=0)
    url: AnyHttpUrl


class ServiceConfig(BaseModel):
    """Service's config file"""

    general: GeneralConfig
    s2: S2Config


def config_from_yaml(path: Path) -> ServiceConfig:
    with open(path) as f:
        config = yaml.safe_load(f)
    return ServiceConfig(**config)


class S2Settings(BaseModel):
    """Settings for making requests to S2"""

    url: AnyHttpUrl
    login: str
    password: str
    timeout: confloat(gt=0)
