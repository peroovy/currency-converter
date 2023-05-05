from redis.asyncio.client import Redis

from app.db.models import Currency
from app.domain.services import ICurrencyRepository


class CurrencyRepository(ICurrencyRepository):
    def __init__(self, session: Redis):
        self._session = session

    async def find_by_code(self, code: str) -> Currency | None:
        quotes = await self._session.lrange(code, 0, -1)

        if not quotes:
            return None

        direct_quote, reverse_quote = quotes

        return Currency(code=code, direct_quote=direct_quote, reverse_quote=reverse_quote)

    async def put(self, *currencies: Currency) -> None:
        pipe = self._session.pipeline()

        for curr in currencies:
            code = self._prepare_code(curr.code)
            pipe = pipe.delete(code)
            pipe = pipe.rpush(code, str(curr.direct_quote), str(curr.reverse_quote))

        await pipe.execute()

    async def flush(self) -> None:
        await self._session.flushdb()

    @staticmethod
    def _prepare_code(code: str) -> str:
        return code.upper()
