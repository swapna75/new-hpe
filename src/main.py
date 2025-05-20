import asyncio

from src.notifier import ConsoleNotifier
from src.graph import ServiceGraph
from src.listners import HTTPListener
from src.message_queue import AsyncQueue
from src.detector import GraphDetector
from src.storage import DictStore


async def main():
    notifier = ConsoleNotifier()
    graph = ServiceGraph()
    mq = AsyncQueue()
    store = DictStore("test/alerts")
    detector = GraphDetector(graph, mq, store, notifier)

    httpserver = HTTPListener(mq)
    httpserver.set_feedback_listner(detector.feedback_handler)
    await asyncio.gather(detector.start(), httpserver.listen())


def test():
    pass


if __name__ == "__main__":
    test()
    asyncio.run(main())
