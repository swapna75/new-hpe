from abc import ABC, abstractmethod
from typing import  Optional
import asyncio


class AbstractNotifier(ABC):
    @abstractmethod
    async def notify(self):
        pass

class GraphNode:
    def __init__(
        self, 
        id: int, 
        parents: list | None = None, 
        children: list | None = None
    ) -> None:
        self.id = id
        # edges with dependency information.
        self.parents: list[GraphNode] = parents or []
        self.children: list[GraphNode]= children or []

class AbstractGraph(ABC):
    @abstractmethod
    def add(self, Node: GraphNode):
        """Add a node to the graph"""
        pass

    @abstractmethod
    def remove(self, id):
        """remove a node in the graph."""
        pass

    @abstractmethod
    def get_dependents(self, id):
        """Get the services that are depended by the required service"""
        pass

    @abstractmethod
    async def update(self):
        """this func get scheduled or will be ticked with some delta time."""
        pass
    
    @abstractmethod
    def get_parents(self):
        """This func must yield the parents. according to their depth."""
        pass

    @abstractmethod
    def get_node(self, id: int) -> Optional[GraphNode]:
        """Fetch a node by its ID to inspect dependencies."""
        pass

    @abstractmethod
    def get_roots(self) -> list[GraphNode]:
        """Return all root nodes (no parents)."""
        pass

    @abstractmethod
    def has_node(self, id: int) -> bool:
        """Check if a node exists in the graph."""
        pass
    

class AbstractDetector(ABC)

    @abstractmethod
    def __init__(self, graph: AbstractGraph, work_queue: asyncio.Queue) -> None:
        pass

    @abstractmethod
    async def start(self):
        """this is the main func that needs to start and then listen for alerts and process it."""
        pass


class AbstractListner(ABC):
    @abstractmethod
    def __init__(self, detector: AbstractDetector, work_queue: asyncio.Queue) -> None:
        pass

    @abstractmethod
    async def listen(self):
        pass

    @staticmethod
    @abstractmethod
    async def recieve_alert():
        pass
