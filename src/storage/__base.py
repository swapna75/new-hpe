from abc import ABC, abstractmethod
from src.models import Alert


class BaseAlertStore(ABC):
    @abstractmethod
    def __init__(self, url: str) -> None:
        pass

    @abstractmethod
    async def get(self, id) -> Alert:
        pass

    @abstractmethod
    async def put(self, id, alert: Alert):
        pass

    @abstractmethod
    async def has(self, id) -> bool:
        pass

    @abstractmethod
    async def remove(self, id):
        pass
