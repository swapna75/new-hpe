from abc import ABC, abstractmethod
from src.graph import BaseGraph
from src.message_queue import BaseMessageQueue


class BaseDetector(ABC):
    @abstractmethod
    def __init__(self, graph: BaseGraph, work_queue: BaseMessageQueue) -> None:
        pass

    @abstractmethod
    async def start(self):
        """this is the main func that needs to start and then listen for alerts and process it."""
        pass
