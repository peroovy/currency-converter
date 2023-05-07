from abc import ABC
from enum import IntEnum
from functools import partial

from _decimal import Decimal
from pydantic import BaseModel, Field, validator

from app.config import CURRENCY_CODE_LENGTH, CURRENCY_DECIMAL_PLACES
from app.domain.utils import camelize_snakecase


class UpdatingMode(IntEnum):
    FLUSH = 0
    MERGE = 1


CodeField = partial(Field, regex=f"^[a-zA-Z]{{{CURRENCY_CODE_LENGTH}}}")
QuoteField = partial(Field, ge=0, decimal_places=CURRENCY_DECIMAL_PLACES)


class Entity(BaseModel, ABC):
    class Config:
        allow_mutation = False
        alias_generator = camelize_snakecase
        allow_population_by_field_name = True


class ConversionIn(Entity):
    from_currency: str = CodeField(alias="from")
    to_currency: str = CodeField(alias="to")
    amount: Decimal = QuoteField()


class ConversionOut(Entity):
    amount: Decimal = QuoteField()


class CurrencyIn(Entity):
    code: str = CodeField()
    direct_quote: Decimal = QuoteField(ge=None, gt=0)
    reverse_quote: Decimal = QuoteField(ge=None, gt=0)


class UpdatingOptions(Entity):
    mode: UpdatingMode = Field(alias="merge")


class UpdatingIn(Entity):
    currencies: list[CurrencyIn]

    @validator("currencies")
    def currencies_should_be_unique(cls, value: list[CurrencyIn]) -> list[CurrencyIn]:
        unique_codes = set(curr.code for curr in value)

        if len(value) != len(unique_codes):
            raise ValueError("Currencies should be unique")

        return value
