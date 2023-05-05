from abc import ABC, abstractmethod
from decimal import Decimal

from app.config import CURRENCY_DECIMAL_PLACES
from app.db.models import Currency
from app.domain.entities import ConversionIn, ConversionOut, UpdatingIn, UpdatingMode, UpdatingParams
from app.domain.exceptions import UnknownCurrencyError


class ICurrencyRepository(ABC):
    @abstractmethod
    async def find_by_code(self, code: str) -> Currency | None:
        raise NotImplementedError

    @abstractmethod
    async def put(self, *currencies: Currency) -> None:
        raise NotImplementedError

    @abstractmethod
    async def flush(self) -> None:
        raise NotImplementedError


class Converter:
    def __init__(self, currency_repository: ICurrencyRepository):
        self._currency_repo = currency_repository

    async def convert(self, conversion: ConversionIn) -> ConversionOut:
        from_currency = await self._currency_repo.find_by_code(conversion.from_currency.upper())
        to_currency = await self._currency_repo.find_by_code(conversion.to_currency.upper())

        if not from_currency or not to_currency:
            raise UnknownCurrencyError

        amount = self._round_currency(conversion.amount * from_currency.reverse_quote * to_currency.direct_quote)

        return ConversionOut(amount=amount)

    async def update(self, data: UpdatingIn, parameters: UpdatingParams) -> None:
        currencies = (
            Currency(code=curr_in.code, direct_quote=curr_in.direct_quote, reverse_quote=curr_in.reverse_quote)
            for curr_in in data.currencies
        )

        if parameters.merge == UpdatingMode.FLUSH:
            await self._currency_repo.flush()

        await self._currency_repo.put(*currencies)

    @staticmethod
    def _round_currency(amount: Decimal) -> Decimal:
        return Decimal(round(amount, ndigits=CURRENCY_DECIMAL_PLACES))
