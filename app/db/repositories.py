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
