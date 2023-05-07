from decimal import Decimal

from redis.asyncio.client import Redis

from app.db.models import Currency
from app.domain.services import ICurrencyRepository


class CurrencyRepository(ICurrencyRepository):
    def __init__(self, session: Redis, base_currency_code: str):
        self._session = session
        self._base_currency_code = self._prepare_code(base_currency_code)

    async def find_by_code(self, code: str) -> Currency | None:
        code = self._prepare_code(code)

        if code == self._base_currency_code:
            return Currency(code=code, direct_quote=Decimal(1))

        direct_quote = await self._session.get(code)

        if direct_quote is None:
            return None

        return Currency(code=code, direct_quote=Decimal(direct_quote))

    async def put(self, *currencies: Currency) -> None:
        pipe = self._session.pipeline()

        for currency in currencies:
            pipe = pipe.set(self._prepare_code(currency.code), str(currency.direct_quote))

        await pipe.execute()

    async def flush(self) -> None:
        await self._session.flushdb()

    @staticmethod
    def _prepare_code(code: str) -> str:
        return code.upper()
