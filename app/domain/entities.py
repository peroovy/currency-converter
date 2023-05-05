from abc import ABC
from enum import IntEnum

from _decimal import Decimal
from pydantic import BaseModel, Field, validator

from app.config import CURRENCY_CODE_LENGTH, CURRENCY_DECIMAL_PLACES
from app.domain.utils import camelize_snakecase


class UpdatingMode(IntEnum):
    FLUSH = 0
    MERGE = 1


class Entity(BaseModel, ABC):
    class Config:
        allow_mutation = False
        alias_generator = camelize_snakecase
        allow_population_by_field_name = True


class ConversionIn(Entity):
    from_currency: str = Field(alias="from", min_length=CURRENCY_CODE_LENGTH, max_length=CURRENCY_CODE_LENGTH)
    to_currency: str = Field(alias="to", min_length=CURRENCY_CODE_LENGTH, max_length=CURRENCY_CODE_LENGTH)
    amount: Decimal = Field(gt=0, decimal_places=CURRENCY_DECIMAL_PLACES)


class ConversionOut(Entity):
    amount: Decimal = Field(gt=0)


class CurrencyIn(Entity):
    code: str = Field(min_length=CURRENCY_CODE_LENGTH, max_length=CURRENCY_CODE_LENGTH)
    direct_quote: Decimal = Field(decimal_places=CURRENCY_DECIMAL_PLACES)
    reverse_quote: Decimal = Field(decimal_places=CURRENCY_DECIMAL_PLACES)


class UpdatingParams(Entity):
    merge: UpdatingMode


class UpdatingIn(Entity):
    currencies: list[CurrencyIn]

    @validator("currencies")
    def currencies_should_be_unique(cls, value: list[CurrencyIn]) -> list[CurrencyIn]:
        unique_codes = set(curr.code for curr in value)

        if len(value) != len(unique_codes):
            raise ValueError("Currencies should be unique")

        return value
