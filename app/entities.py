from abc import ABC

from pydantic import BaseModel


def _camelize_snakecase(string: str) -> str:
    parts = string.split("_")

    return parts[0].lower() + "".join(part.title() for part in parts[1:]) if len(parts) > 1 else string


class Entity(BaseModel, ABC):
    class Config:
        allow_mutation = False
        alias_generator = _camelize_snakecase
        allow_population_by_field_name = True
