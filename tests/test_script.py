import asyncio
import datetime

from src.message_queue import AsyncQueue
from src.dependancy import GraphDetector
from src.graph import ServiceGraph
from src.interfaces import BaseNotifier
from src.models import AlertGroup
from src.store import DictStore
from src.models import Alert


alerts = [
    {
        "labels": {
            "job": "database",
            "severity": "critical",
        },
        "startsAt": datetime.datetime(2025, 3, 1, 12, 30, 2).isoformat() + "Z",
        "endsAt": datetime.datetime(2025, 3, 1, 12, 30, 53).isoformat() + "Z",
        "status": "firing",
        "annotations": {
            "description": "temp description of database",
            "summary": "DatabaseDown",
        },
    },
    {
        "labels": {
            "job": "knn",
            "severity": "critical",
        },
        "startsAt": datetime.datetime(2025, 3, 1, 12, 30, 10).isoformat() + "Z",
        "endsAt": datetime.datetime(2025, 3, 1, 12, 30, 55).isoformat() + "Z",
        "status": "firing",
        "annotations": {
            "description": "temp description of knn",
            "summary": "RPCFailure",
        },
    },
    {
        "labels": {
            "job": "backend",
            "severity": "critical",
        },
        "startsAt": datetime.datetime(2025, 3, 1, 12, 30, 20).isoformat() + "Z",
        "endsAt": datetime.datetime(2025, 3, 1, 12, 31, 10).isoformat() + "Z",
        "status": "firing",
        "annotations": {
            "description": "temp description of backend",
            "summary": "HttpFailure",
        },
    },
]


class TestNotifier(BaseNotifier):
    def __init__(self) -> None:
        self.to_raise = {}

    async def notify(self, alert: AlertGroup):
        # check in the to_raise thing.
        pass


async def test_detector():
    patterns = [
        alerts[:1],
        alerts[:2],
        alerts[:3],
        alerts[1:2],
        alerts[1:3],
        alerts[2:3],
    ]
    results = []
    graph = ServiceGraph()
    mq = AsyncQueue()
    nf = TestNotifier()
    a_store = DictStore("/test")
    gd = GraphDetector(graph, mq, a_store, nf)

    for i in patterns:
        for al in map(Alert, i):
            await gd.process_alert(al)


async def test():
    await test_detector()


if __name__ == "__main__":
    asyncio.run(test())
