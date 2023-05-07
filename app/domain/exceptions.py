from app.error import Error


class UnknownCurrencyError(Error):
    @property
    def message(self) -> str:
        return "Quotes are not set for one of the currencies"
