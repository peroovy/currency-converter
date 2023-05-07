from decimal import Decimal

import pytest
from aiohttp.test_utils import TestClient

from app.db.models import Currency
from tests.integration.conftest import error


pytestmark = [pytest.mark.integration]


@pytest.mark.parametrize(
    ["params", "status_code"],
    [
        [{"from": "RUB", "to": "EUR", "amount": 42}, 200],
        [{"from": "EUR", "to": "RUB", "amount": 42}, 200],
        [{"from": "rub", "to": "eur", "amount": 42}, 200],
        [{"from": "rUB", "to": "Eur", "amount": 42}, 200],
        [{"from": "RUB", "to": "EUR", "amount": 42.1234}, 200],
        [{"from": "RUB", "to": "EUR", "amount": 42.12345}, 422],
        [{"from": "RU", "to": "EU", "amount": 42}, 422],
        [{"from": "RUBY", "to": "EURO", "amount": 42}, 422],
        [{}, 422],
        [{"from": "UNK", "to": "EUR", "amount": 42}, 400],
        [{"from": "RUB", "to": "UNK", "amount": 42}, 400],
    ],
    ids=[
        "rub to eur in upper case",
        "eur to rub in upper case",
        "lower case",
        "mixed case",
        "number of amount's decimal places can be less or equal than 4",
        "number of amount's decimal places cannot be greater than 4",
        "length of currency codes is 2",
        "length of currency codes is 4",
        "all fields should be required",
        "unknown currency from",
        "unknown currency to",
    ],
)
async def test(client: TestClient, eur: Currency, rub: Currency, params: dict, status_code: int):
    response = await client.get("/convert", params=params)

    assert response.status == status_code, await response.text()
    body = await response.json()

    match status_code:
        case 200:
            from_curr, to_curr = (rub, eur) if params["from"].lower() == rub.code.lower() else (eur, rub)
            expected = round(Decimal(params["amount"]) * from_curr.direct_quote / to_curr.direct_quote, 4)

            assert body == {"amount": float(expected)}

        case 400:
            assert body == error("UnknownCurrencyError", "Quotes are not set for one of the currencies")
