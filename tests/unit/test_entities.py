from decimal import Decimal
from typing import TypeVar

import pytest
from pydantic import ValidationError

from app.domain.entities import (
    ConversionIn,
    ConversionOut,
    CurrencyIn,
    Entity,
    UpdatingIn,
    UpdatingMode,
    UpdatingOptions,
)


T = TypeVar("T", bound=Entity)


@pytest.mark.parametrize(
    ["from_currency", "to_currency", "amount", "is_valid"],
    [
        ["RUB", "EUR", "10", True],
        ["rub", "eur", "10", True],
        ["rUb", "Eur", "10", True],
        ["R2B", ".UR", "10", False],
        ["RUB", "EU", "10", False],
        ["RUB", "EURO", "10", False],
        ["RU", "EUR", "10", False],
        ["RUBY", "EUR", "10", False],
        ["", "", "10", False],
        ["RUB", "EUR", "-1", False],
        ["RUB", "EUR", "-0.0001", False],
        ["RUB", "EUR", "0", True],
        ["RUB", "EUR", "0.0001", True],
        ["RUB", "EUR", "1", True],
        ["RUB", "EUR", "1.12345", False],
    ],
    ids=[
        "code is in upper case",
        "code is in lower case",
        "code is in mixed case",
        "code has not only letters",
        "to_currency code length is 2",
        "to_currency code length is not 4",
        "from_currency code length is 2",
        "from_currency code length is not 4",
        "code length is 0",
        "amount is negative",
        "amount is negative with 4 decimal places",
        "amount is 0",
        "amount has 4 decimal places",
        "amount is integer",
        "amount has 5 decimal places",
    ],
)
def test_conversion_in(from_currency: str | None, to_currency: str | None, amount: str, is_valid: bool):
    _test_entities(
        ConversionIn, {"from_currency": from_currency, "to_currency": to_currency, "amount": amount}, is_valid
    )


@pytest.mark.parametrize(
    ["amount", "is_valid"],
    [
        ["-1", False],
        ["-0.0001", False],
        ["0", True],
        ["0.0001", True],
        ["1", True],
        ["1.1234", True],
        ["1.12345", False],
    ],
)
def test_conversion_out(amount: str, is_valid: bool):
    _test_entities(ConversionOut, {"amount": Decimal(amount)}, is_valid)


@pytest.mark.parametrize(
    ["code", "direct_quote", "reverse_quote", "is_valid"],
    [
        ["RUB", "10", "10", True],
        ["rub", "10", "10", True],
        ["rUb", "10", "10", True],
        ["", "10", "10", False],
        ["RU", "10", "10", False],
        ["RUBY", "10", "10", False],
        ["r2 ", "10", "10", False],
        ["RUB", "-1", "-1", False],
        ["RUB", "0", "0", False],
        ["RUB", "0.0001", "0.0001", True],
        ["RUB", "0.12345", "0.12345", False],
    ],
    ids=[
        "code is in upper case",
        "code is in lower case",
        "code is in mixed case",
        "code is empty",
        "code length is 2",
        "code length is 4",
        "code has not only letters",
        "quotes are negative",
        "quotes is 0",
        "quotes is positive with 4 decimal places",
        "quotes have 5 decimal places",
    ],
)
def test_currency_in(code: str, direct_quote: str, reverse_quote: str, is_valid: bool):
    _test_entities(CurrencyIn, {"code": code, "direct_quote": direct_quote, "reverse_quote": reverse_quote}, is_valid)


@pytest.mark.parametrize(
    ["mode", "is_valid"],
    [
        [-1, False],
        [0, True],
        [1, True],
        [2, False],
    ],
)
def test_updating_options(mode: int, is_valid: bool):
    entity = _test_entities(UpdatingOptions, {"mode": mode}, is_valid)

    match mode:
        case 0:
            assert entity.mode == UpdatingMode.FLUSH
        case 1:
            assert entity.mode == UpdatingMode.MERGE


@pytest.mark.parametrize(
    ["currencies", "is_valid"],
    [
        [[], True],
        [[CurrencyIn(code="RUB", direct_quote=Decimal(1), reverse_quote=Decimal(1))], True],
        [
            [
                CurrencyIn(code="RUB", direct_quote=Decimal(1), reverse_quote=Decimal(1)),
                CurrencyIn(code="EUR", direct_quote=Decimal(2), reverse_quote=Decimal(2)),
            ],
            True,
        ],
        [
            [
                CurrencyIn(code="RUB", direct_quote=Decimal(1), reverse_quote=Decimal(1)),
                CurrencyIn(code="RUB", direct_quote=Decimal(2), reverse_quote=Decimal(2)),
            ],
            False,
        ],
    ],
    ids=[
        "not currencies",
        "one currency",
        "two different currencies",
        "two identical currencies",
    ],
)
def test_updating_in(currencies: list[CurrencyIn], is_valid: bool):
    _test_entities(UpdatingIn, {"currencies": currencies}, is_valid)


def _test_entities(entity_cls: type[T], data: dict, is_valid: bool) -> T:
    if is_valid:
        return entity_cls(**data)
    else:
        with pytest.raises(ValidationError):
            return entity_cls(**data)
