from abc import ABC, abstractmethod
from typing import Generator
from models import Alert, GraphNode


class InvalidOperationError(Exception):
    pass


class AbstractNotifier(ABC):
    @abstractmethod
    async def notify(self, alert: Alert):
        pass


class AbstractGraph(ABC):
    @abstractmethod
    def add(self, node_id: int, parents: set[int], children: set[int]) -> GraphNode:
        """Add a node to the graph"""
        pass

    @abstractmethod
    def remove(self, id):
        """remove a node in the graph."""
        pass

    @abstractmethod
    def get_dependents(self, id) -> list:
        """Get the services that are depended by the required service"""
        pass

    @abstractmethod
    async def update(self):
        """this func get scheduled or will be ticked with some delta time."""
        pass

    @abstractmethod
    def get_parents(self, id: int) -> Generator:
        """This func must yield the parents. according to their depth."""
        pass

    @abstractmethod
    def get_node(self, id: int) -> GraphNode:
        """Fetch a node by its ID to inspect dependencies."""
        pass

    def get_roots(self) -> list[GraphNode]:
        """Return all root nodes (no parents)."""
        raise NotImplementedError

    @abstractmethod
    def has_node(self, id: int) -> bool:
        """Check if a node exists in the graph."""
        pass


class AbstractMessageQueue(ABC):
    @abstractmethod
    async def put(self, event):
        pass

    @abstractmethod
    def put_nowait(self, event):
        pass

    @abstractmethod
    async def get(self):
        pass


class AbstractDetector(ABC):
    @abstractmethod
    def __init__(self, graph: AbstractGraph, work_queue: AbstractMessageQueue) -> None:
        pass

    @abstractmethod
    async def start(self):
        """this is the main func that needs to start and then listen for alerts and process it."""
        pass


class AbstractListener(ABC):
    @abstractmethod
    def __init__(
        self, detector: AbstractDetector, work_queue: AbstractMessageQueue
    ) -> None:
        pass

    @abstractmethod
    async def listen(self):
        """this is to start the listner."""
        pass


class AbstractAlertStore(ABC):
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
