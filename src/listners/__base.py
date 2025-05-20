from abc import ABC, abstractmethod
from src.detector import BaseDetector
from src.message_queue import BaseMessageQueue


class BaseListener(ABC):
    @abstractmethod
    def __init__(self, detector: BaseDetector, work_queue: BaseMessageQueue) -> None:
        pass

    @abstractmethod
    async def listen(self):
        """this is to start the listner."""
        pass

    @abstractmethod
    def set_feedback_listner(self, handler):
        pass
