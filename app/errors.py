from abc import ABC, abstractmethod


class APIError(Exception, ABC):
    @property
    @abstractmethod
    def message(self) -> str:
        raise NotImplementedError

    @property
    def status_code(self) -> int:
        return 400

    def dict(self) -> dict:
        return {"error": {"code": self.__class__.__name__, "msg": self.message}}
