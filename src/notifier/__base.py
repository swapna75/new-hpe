from abc import ABC, abstractmethod
from src.models import AlertGroup


class BaseNotifier(ABC):
    @abstractmethod
    async def notify(self, alert: AlertGroup):
        pass
