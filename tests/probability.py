import asyncio
import datetime
import itertools
import _path
import logging
from src.message_queue import AsyncQueue
from src.detector import ProbabilityDetector
from src.graph import ServiceGraph
from src.notifier import BaseNotifier
from src.models import AlertGroup, Alert, FeedBack
from src.storage import DictStore


_path.thing = None  # this is to make sure the import is not removed.

log = logging.getLogger(__package__)

alerts = [
    {
        "labels": {
            "job": "database",
            "instance": "1",
            "severity": "critical",
        },
        "startsAt": datetime.datetime(2025, 3, 1, 12, 30, 2).isoformat() + "Z",
        "endsAt": datetime.datetime(2025, 3, 1, 12, 30, 53).isoformat() + "Z",
        "status": "firing",
        "annotations": {
            "description": "database alert 1.",
            "summary": "'database instance 1 down'",
        },
    },
    {
        "labels": {
            "job": "database",
            "instance": "2",
            "severity": "critical",
        },
        "startsAt": datetime.datetime(2025, 3, 1, 12, 30, 1).isoformat() + "Z",
        "endsAt": datetime.datetime(2025, 3, 1, 12, 30, 57).isoformat() + "Z",
        "status": "firing",
        "annotations": {
            "description": "database alert 2.",
            "summary": "'database instance 2 down'",
        },
    },
    {
        "labels": {
            "job": "knn",
            "instance": "1",
            "severity": "critical",
        },
        "startsAt": datetime.datetime(2025, 3, 1, 12, 30, 7).isoformat() + "Z",
        "endsAt": datetime.datetime(2025, 3, 1, 12, 31, 0).isoformat() + "Z",
        "status": "firing",
        "annotations": {
            "description": "knn alert 1.",
            "summary": "knn service 1 down.",
        },
    },
    {
        "labels": {
            "instance": "2",
            "job": "knn",
            "severity": "critical",
        },
        "startsAt": datetime.datetime(2025, 3, 1, 12, 30, 8).isoformat() + "Z",
        "endsAt": datetime.datetime(2025, 3, 1, 12, 31, 10).isoformat() + "Z",
        "status": "firing",
        "annotations": {
            "description": "knn alert 2.",
            "summary": "'knn instance 2 down'",
        },
    },
    {
        "labels": {
            "instance": "1",
            "job": "backend",
            "severity": "critical",
        },
        "startsAt": datetime.datetime(2025, 3, 1, 12, 31, 40).isoformat() + "Z",
        "endsAt": datetime.datetime(2025, 3, 1, 12, 32, 10).isoformat() + "Z",
        "status": "firing",
        "annotations": {
            "description": "backend alert 1.",
            "summary": "'backend instance 1 down'",
        },
    },
    {
        "labels": {
            "instance": "2",
            "job": "backend",
            "severity": "critical",
        },
        "startsAt": datetime.datetime(2025, 3, 1, 12, 31, 45).isoformat() + "Z",
        "endsAt": datetime.datetime(2025, 3, 1, 12, 32, 11).isoformat() + "Z",
        "status": "firing",
        "annotations": {
            "description": "backend alert 2.",
            "summary": "'backend instance 2 down'",
        },
    },
]


class TestNotifier(BaseNotifier):
    def __init__(self) -> None:
        self.to_raise = set()

    async def notify(self, alertg: AlertGroup):
        root = alertg.root
        # print("--------> : ", alertg.root.id)
        # print("--------> : ", alertg.group)
        if root.id not in self.to_raise:
            # print(self.to_raise)
            log.critical("A false prediction.")
        else:
            log.info(f"found an alert with needed root `{alertg.root}`")


async def test_detector():
    global alerts

    graph = ServiceGraph()
    alerts = [*map(Alert, alerts)]
    for i, a in enumerate(alerts):
        a.id = str(i + 1001)
    unq_fbs = [
        FeedBack(f"""
            [
                ["{alerts[0].id}", "{alerts[2].id}", true],
                ["{alerts[2].id}", "{alerts[4].id}", true]
            ]
            """),
        FeedBack(f"""
            [
                ["{alerts[1].id}", "{alerts[0].id}", false],
                ["{alerts[0].id}", "{alerts[1].id}", false],
                ["{alerts[1].id}", "{alerts[3].id}", true],
                ["{alerts[0].id}", "{alerts[2].id}", true],
                ["{alerts[3].id}", "{alerts[5].id}", true],
                ["{alerts[3].id}", "{alerts[4].id}", false],
                ["{alerts[5].id}", "{alerts[4].id}", true],
                ["{alerts[2].id}", "{alerts[4].id}", true]
            ]
            """),
        FeedBack("[]"),
    ]

    patterns = [alerts[::2], alerts[1::2], alerts[::2], alerts[1::2], alerts]
    results = [
        [alerts[0]],
        [alerts[1]],
        [alerts[0]],
        [alerts[1]],
        [alerts[0], alerts[1]],
    ]
    fbs = [unq_fbs[0], unq_fbs[1], unq_fbs[2], unq_fbs[2], unq_fbs[2]]
    mq = AsyncQueue()
    nf = TestNotifier()
    a_store = DictStore("test/probability")
    gd = ProbabilityDetector(graph, mq, a_store, nf)

    for p, res, f in zip(patterns, results, fbs):
        for r in res:
            nf.to_raise.add(r.id)
        for al in p:
            await a_store.put(al.id, al)
            await gd.process_alert(al)

        await asyncio.gather(
            *itertools.chain(*[t.notify_tasks.values() for t in gd.batches])
        )

        for al in p:
            await a_store.remove(al.id)
        nf.to_raise.clear()
        await gd.feedback_handler(f)


async def test():
    await test_detector()


if __name__ == "__main__":
    asyncio.run(test())
