from decimal import Decimal
from unittest.mock import MagicMock, Mock

import pytest

from app.db.models import Currency
from app.domain.entities import ConversionIn, CurrencyIn, UpdatingIn, UpdatingMode, UpdatingOptions
from app.domain.exceptions import UnknownCurrencyError
from app.domain.services import Converter
from tests.unit.conftest import MockCurrencyRepository


pytestmark = [pytest.mark.unit]


@pytest.mark.parametrize(
    ["amount", "from_quote", "to_quote", "expected"],
    [
        ["1", "12", "2", "6"],
        ["1", "1", "10_000", "0.0001"],
        ["1", "1", "100_000", "0"],
        ["1", "15", "100_000", "0.0002"],
        ["1337.228", "1.2345", "67.89", "24.3159"],
    ],
)
async def test_correct_conversion(
    converter: Converter,
    currency_repository: MockCurrencyRepository,
    conversion_in: ConversionIn,
    amount: str,
    from_quote: str,
    to_quote: str,
    expected: str,
):
    def find_by_code(code: str) -> Currency:
        return Currency(
            code=code, direct_quote=Decimal(from_quote) if code == conversion_in.from_currency else Decimal(to_quote)
        )

    currency_repository.find_by_code_mock = MagicMock(side_effect=find_by_code)
    conversion_in = ConversionIn(
        from_currency=conversion_in.from_currency, to_currency=conversion_in.to_currency, amount=Decimal(amount)
    )

    actual = await converter.convert(conversion_in)
    assert actual.amount == Decimal(expected)


@pytest.mark.parametrize(
    ["exists_from_currency", "exists_to_currency"],
    [
        [True, False],
        [False, True],
        [False, False],
    ],
    ids=[
        "unknown to_currency",
        "unknown from_currency",
        "unknown both currencies",
    ],
)
async def test_conversion_with_unknown_currency(
    converter: Converter,
    currency_repository: MockCurrencyRepository,
    conversion_in: ConversionIn,
    exists_from_currency: bool,
    exists_to_currency: bool,
):
    def find_by_code(code: str) -> Mock | None:
        if (
            code == conversion_in.from_currency
            and exists_from_currency
            or code == conversion_in.to_currency
            and exists_to_currency
        ):
            return Mock()

        return None

    currency_repository.find_by_code_mock = MagicMock(side_effect=find_by_code)

    with pytest.raises(UnknownCurrencyError):
        await converter.convert(conversion_in)


@pytest.mark.parametrize("mode", UpdatingMode)
async def test_updating(
    converter: Converter, currency_repository: MockCurrencyRepository, updating_in: UpdatingIn, mode: UpdatingMode
):
    options = UpdatingOptions(mode=mode)

    await converter.update(updating_in, options)

    if mode == UpdatingMode.FLUSH:
        currency_repository.flush_mock.assert_called_once()
    else:
        currency_repository.flush_mock.assert_not_called()

    actual_put_args: tuple[Currency] = currency_repository.put_mock.call_args_list[0][0][0]
    actual_currencies = [curr.dict() for curr in actual_put_args]
    expected_currencies = [curr.dict() for curr in updating_in.currencies]

    assert actual_currencies == expected_currencies


@pytest.fixture
def conversion_in(from_currency: str = "FRO", to_currency: str = "TOO", amount: int = 14) -> ConversionIn:
    return ConversionIn(from_currency=from_currency, to_currency=to_currency, amount=Decimal(amount))


@pytest.fixture
def updating_in() -> UpdatingIn:
    currencies = [
        CurrencyIn(code="RUB", direct_quote=Decimal(1)),
        CurrencyIn(code="EUR", direct_quote=Decimal(10)),
    ]

    return UpdatingIn(currencies=currencies)
