from unittest.mock import Mock

import pytest

from app.db.models import Currency
from app.domain.services import Converter, ICurrencyRepository


class MockCurrencyRepository(ICurrencyRepository):
    def __init__(self):
        self.find_by_code_mock = Mock()
        self.put_mock = Mock()
        self.flush_mock = Mock()

    async def find_by_code(self, code: str) -> Currency | None:
        return self.find_by_code_mock(code)

    async def put(self, *currencies: Currency) -> None:
        self.put_mock(currencies)

    async def flush(self) -> None:
        self.flush_mock()


@pytest.fixture
def converter(currency_repository: MockCurrencyRepository) -> Converter:
    return Converter(currency_repository)


@pytest.fixture
def currency_repository() -> MockCurrencyRepository:
    return MockCurrencyRepository()
