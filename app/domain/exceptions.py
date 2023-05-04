from app.errors import APIError


class UnknownCurrencyError(APIError):
    @property
    def message(self) -> str:
        return "Quotes are not set for one of the currencies"
