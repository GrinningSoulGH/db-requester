from ..config import AppConfig, S2Config, GeneralConfig
import pytest
from pydantic.error_wrappers import ValidationError


def test_sqlite():
    config = {
        "general": {"thread_count": 1},
        "database": {"rdbms": "sqlite", "database_path": "/test"},
        "s2": {"url": "http://example.com", "response_timeout": 10},
    }
    AppConfig(**config)


def test_postgresql():
    config = {
        "general": {"thread_count": 1},
        "database": {
            "rdbms": "postgresql",
            "dbname": "test",
            "host": "192.168.100.101",
            "port": 5432,
        },
        "s2": {"url": "http://example.com", "response_timeout": 10},
    }
    with pytest.raises(ValidationError):
        AppConfig(**config)


def test_mysql():
    config = {
        "general": {"thread_count": 1},
        "database": {
            "rdbms": "mysql",
            "dbname": "test",
            "host": "192.168.100.101",
            "port": 5432,
        },
        "s2": {"url": "http://example.com", "response_timeout": 10},
    }
    with pytest.raises(ValidationError):
        AppConfig(**config)


def test_valid_s2_http_address():
    config = {
        "url": "http://example.com",
        "response_timeout": 10,
    }
    S2Config(**config)


def test_s2_http_address_no_schema():
    config = {
        "url": "something.ru",
        "response_timeout": 10,
    }
    with pytest.raises(ValidationError):
        S2Config(**config)


def test_negative_thread_count():
    config = {"thread_count": -1}
    with pytest.raises(ValidationError):
        GeneralConfig(**config)


def test_unsupported_thread_count():
    config = {"thread_count": 1000}
    with pytest.raises(ValidationError):
        GeneralConfig(**config)
