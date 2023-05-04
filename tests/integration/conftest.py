from asyncio import AbstractEventLoop, get_event_loop_policy
from decimal import Decimal
from typing import Awaitable, Callable

import pytest
from aiohttp.abc import Application
from aiohttp.test_utils import TestClient
from redis.asyncio import Redis

from app.config import RedisSettings
from app.db.models import Currency
from app.main import create_app


@pytest.fixture
def rub() -> Currency:
    return Currency(code="RUB", direct_quote=Decimal(50), reverse_quote=Decimal("0.0001"))


@pytest.fixture
def eur() -> Currency:
    return Currency(code="EUR", direct_quote=Decimal(10), reverse_quote=Decimal("0.1"))


@pytest.fixture
async def client(app: Application, aiohttp_client: Callable[[Application], Awaitable[TestClient]]) -> TestClient:
    client = await aiohttp_client(app)

    yield client

    await client.close()


@pytest.fixture(scope="session")
async def redis(redis_settings: RedisSettings) -> Redis:
    connection = Redis(
        host=redis_settings.host,
        port=redis_settings.port,
        password=redis_settings.password.get_secret_value(),
        decode_responses=True,
    )

    yield connection

    await connection.close()


@pytest.fixture(autouse=True)
async def prepare_redis(redis: Redis, eur: Currency, rub: Currency) -> None:
    pipe = redis.pipeline()

    for curr in (eur, rub):
        pipe = pipe.rpush(curr.code, str(curr.direct_quote), str(curr.reverse_quote))

    await pipe.execute()

    yield

    await redis.flushdb()


@pytest.fixture(scope="session")
def redis_settings() -> RedisSettings:
    return RedisSettings()


@pytest.fixture(scope="session")
def app() -> Application:
    return create_app()


@pytest.fixture(scope="session")
def event_loop() -> AbstractEventLoop:
    policy = get_event_loop_policy()
    loop = policy.new_event_loop()

    yield loop

    loop.close()


def error(code: str, message: str) -> dict:
    return {"error": {"code": code, "msg": message}}
