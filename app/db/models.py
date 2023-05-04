from _decimal import Decimal
from pydantic import BaseModel, Field

from app.config import CURRENCY_CODE_LENGTH, CURRENCY_DECIMAL_PLACES


class Currency(BaseModel):
    code: str = Field(min_length=CURRENCY_CODE_LENGTH, max_length=CURRENCY_CODE_LENGTH)
    direct_quote: Decimal = Field(decimal_places=CURRENCY_DECIMAL_PLACES)
    reverse_quote: Decimal = Field(decimal_places=CURRENCY_DECIMAL_PLACES)
