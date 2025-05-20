import asyncio
import datetime
import itertools
import _path
import logging
from src.message_queue import AsyncQueue
from src.detector import ProbabilityDetector
from src.graph import ServiceGraph
from src.notifier import BaseNotifier
from src.models import AlertGroup, Alert
from src.storage import DictStore


_path.thing = None  # this is to make sure the import is not removed.

log = logging.getLogger(__package__)

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
        self.to_raise = set()

    async def notify(self, alertg: AlertGroup):
        root = alertg.root
        if root.id not in self.to_raise:
            log.critical("A false prediction.")
        else:
            log.info(f"found an alert with nedded root `{alertg.root}`")


async def test_detector():
    global alerts

    graph = ServiceGraph()
    alerts = [*map(Alert, alerts)]
    patterns = [
        # alerts[:1],
        # alerts[:2],
        # alerts[:3],
        # alerts[1:2],
        # alerts[1:3],
        # alerts[2:3],
        alerts
    ]
    results = [alerts[0].id]
    mq = AsyncQueue()
    nf = TestNotifier()
    a_store = DictStore("test/probability")
    gd = ProbabilityDetector(graph, mq, a_store, nf)

    for i, res in zip(patterns, results):
        nf.to_raise.add(res)
        for al in i:
            await a_store.put(al.id, al)
            await gd.process_alert(al)

    await asyncio.gather(
        *itertools.chain(*[t.notify_tasks.values() for t in gd.batches])
    )


async def test():
    await test_detector()


if __name__ == "__main__":
    asyncio.run(test())
