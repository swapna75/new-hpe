from abc import ABC, abstractmethod
from typing import Generator
from src.models import GraphNode


class InvalidOperationError(Exception):
    pass


class BaseGraph(ABC):
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
