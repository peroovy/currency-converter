from decimal import Decimal
from typing import Awaitable, Callable

import pytest
from aiohttp.abc import Application
from aiohttp.test_utils import TestClient
from dependency_injector.containers import DeclarativeContainer, override
from dependency_injector.providers import Configuration, Object
from redis.asyncio import Redis

from app.config import RedisSettings
from app.db.models import Currency
from app.main import Container, create_app


@pytest.fixture
async def rub(redis: Redis) -> Currency:
    curr = Currency(code="RUB", direct_quote=Decimal(50), reverse_quote=Decimal("0.0001"))
    await redis.rpush(curr.code, *map(str, [curr.direct_quote, curr.reverse_quote]))

    return curr


@pytest.fixture
async def eur(redis: Redis) -> Currency:
    curr = Currency(code="EUR", direct_quote=Decimal(10), reverse_quote=Decimal("0.1"))
    await redis.rpush(curr.code, *map(str, [curr.direct_quote, curr.reverse_quote]))

    return curr


@pytest.fixture
async def client(app: Application, aiohttp_client: Callable[[Application], Awaitable[TestClient]]) -> TestClient:
    client = await aiohttp_client(app)

    yield client

    await client.close()


@pytest.fixture(scope="session")
async def redis(test_redis_settings: RedisSettings) -> Redis:
    connection = Redis(
        host=test_redis_settings.host,
        port=test_redis_settings.port,
        password=test_redis_settings.password.get_secret_value(),
        decode_responses=True,
    )

    yield connection

    await connection.close()


@pytest.fixture(autouse=True)
async def flush_redis(redis: Redis) -> None:
    yield

    await redis.flushdb()


@pytest.fixture(scope="session")
def test_redis_settings() -> RedisSettings:
    return RedisSettings()


@pytest.fixture(scope="session")
async def app(redis: Redis, test_redis_settings: RedisSettings) -> Application:
    @override(Container)
    class TestContainer(DeclarativeContainer):
        redis_settings = Configuration(pydantic_settings=[test_redis_settings])
        redis_session = Object(redis)

    return await create_app()


def error(code: str, message: str) -> dict:
    return {"error": {"code": code, "msg": message}}


def success() -> dict:
    return {"msg": "Success"}
