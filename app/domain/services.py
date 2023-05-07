from abc import ABC, abstractmethod
from decimal import Decimal

from loguru import logger

from app.config import CURRENCY_DECIMAL_PLACES
from app.db.models import Currency
from app.domain.entities import ConversionIn, ConversionOut, UpdatingIn, UpdatingMode, UpdatingOptions
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
        from_currency = await self._currency_repo.find_by_code(conversion.from_currency)
        to_currency = await self._currency_repo.find_by_code(conversion.to_currency)

        if not from_currency or not to_currency:
            raise UnknownCurrencyError

        amount = self._round_currency(from_currency.direct_quote / to_currency.direct_quote * conversion.amount)
        logger.info(f"Conversion {conversion.amount} of {from_currency.dict()} -> {amount} of {to_currency.dict()}")

        return ConversionOut(amount=amount)

    async def update(self, data: UpdatingIn, options: UpdatingOptions) -> None:
        currencies = list(
            Currency(code=currency.code, direct_quote=currency.direct_quote) for currency in data.currencies
        )

        if options.mode == UpdatingMode.FLUSH:
            await self._currency_repo.flush()
            logger.info("Flush database")

        await self._currency_repo.put(*currencies)
        logger.info(f"Put {[currency.dict() for currency in currencies]}")

    @staticmethod
    def _round_currency(amount: Decimal) -> Decimal:
        return Decimal(round(amount, ndigits=CURRENCY_DECIMAL_PLACES))
