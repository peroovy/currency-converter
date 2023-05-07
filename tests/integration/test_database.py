from decimal import Decimal

import pytest
from aiohttp import ClientResponse
from aiohttp.test_utils import TestClient
from redis.asyncio.client import Redis

from app.db.models import Currency
from tests.integration.conftest import success


pytestmark = [pytest.mark.integration]


async def put_currencies(client: TestClient, merge: bool, *currencies: Currency) -> ClientResponse:
    body = [{"code": currency.code, "directQuote": str(currency.direct_quote)} for currency in currencies]

    return await _put_currency(client, int(merge), body)


async def _put_currency(client: TestClient, merge: int | None, body: list[dict]) -> ClientResponse:
    uri = "/database" + (f"?merge={merge}" if merge is not None else "")

    return await client.post(uri, json=body)


@pytest.mark.parametrize(
    ["delete", "merge"],
    [
        [True, True],
        [True, False],
        [False, True],
        [False, False],
    ],
    ids=[
        "creating with merging",
        "creating with flushing",
        "updating with merging",
        "updating with flushing",
    ],
)
async def test(client: TestClient, redis: Redis, rub: Currency, eur: Currency, delete: bool, merge: bool):
    if delete:
        await redis.delete(rub.code)

    new_rub = Currency(code=rub.code, direct_quote=Decimal("12345678"))

    response = await put_currencies(client, merge, new_rub)

    assert response.status == 200, await response.text()
    assert await response.json() == success()

    if merge:
        assert await exists_currency(redis, new_rub) is True
        assert await exists_currency(redis, eur) is True
    else:
        assert await exists_currency(redis, new_rub) is True
        assert await exists_currency(redis, eur) is False


@pytest.mark.parametrize(
    ["body", "merge", "is_valid"],
    [
        [None, 0, False],
        [[{"code": "RUB", "directQuote": 1}], -1, False],
        [[{"code": "RUB", "directQuote": 1}], 0, True],
        [[{"code": "RUB", "directQuote": 1}], 1, True],
        [[{"code": "RUB", "directQuote": 1}], 2, False],
        [[{"code": "RUB", "directQuote": 0}], 2, False],
        [[{"code": "RUB", "directQuote": 0.1234}], 1, True],
        [[{"code": "RUB", "directQuote": 0.12345}], 1, False],
        [[{"code": "rub", "directQuote": 1}], 0, True],
        [[{"code": "rUb", "directQuote": 1}], 0, True],
        [[{"code": "RU", "directQuote": 1}], 0, False],
        [[{"code": "RUBY", "directQuote": 1}], 0, False],
        [
            [
                {"code": "RUB", "directQuote": 1},
                {"code": "EUR", "directQuote": 1},
            ],
            0,
            True,
        ],
        [
            [
                {"code": "RUB", "directQuote": 1},
                {"code": "RUB", "directQuote": 2},
            ],
            0,
            False,
        ],
    ],
    ids=[
        "no body",
        "merge param is less than 0",
        "merge param is 0",
        "merge param is 1",
        "merge param is greater than 1",
        "quote is less than 0",
        "number of quote decimal places is 4",
        "number of quote decimal places is greater than 4",
        "code is in lower case",
        "code is in mixed case",
        "code length is 2",
        "code length is 4",
        "two different currencies",
        "two identical currencies",
    ],
)
async def test_validation(client: TestClient, redis: Redis, merge: int | None, body: list[dict], is_valid: bool):
    response = await _put_currency(client, merge, body)

    if is_valid:
        assert response.status == 200, await response.text()
        assert len(await redis.keys()) > 0
    else:
        assert response.status == 422, await response.text()
        assert len(await redis.keys()) == 0


async def exists_currency(redis: Redis, currency: Currency) -> bool:
    return str(currency.direct_quote) == await redis.get(currency.code)
