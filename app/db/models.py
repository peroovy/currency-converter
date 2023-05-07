from decimal import Decimal

from pydantic import BaseModel


class Currency(BaseModel):
    code: str
    direct_quote: Decimal
