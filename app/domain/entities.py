from _decimal import Decimal
from pydantic import Field

from app.config import CURRENCY_CODE_LENGTH, CURRENCY_DECIMAL_PLACES
from app.entities import Entity


class ConversionIn(Entity):
    from_currency: str = Field(alias="from", min_length=CURRENCY_CODE_LENGTH, max_length=CURRENCY_CODE_LENGTH)
    to_currency: str = Field(alias="to", min_length=CURRENCY_CODE_LENGTH, max_length=CURRENCY_CODE_LENGTH)
    amount: Decimal = Field(gt=0, decimal_places=CURRENCY_DECIMAL_PLACES)


class ConversionOut(Entity):
    amount: Decimal = Field(gt=0)
