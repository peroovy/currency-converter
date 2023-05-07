from abc import ABC, abstractmethod


class Error(Exception, ABC):
    @property
    @abstractmethod
    def message(self) -> str:
        raise NotImplementedError

    @property
    def status_code(self) -> int:
        return 400
