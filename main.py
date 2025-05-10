import asyncio

from listner import HTTPListener

from dependancy import GraphDetector
from graph import ServiceGraph
from notifier import ConsoleNotifier
from message_queue import AsyncQueue
from store import DictStore


async def main():
    notifier = ConsoleNotifier()
    graph = ServiceGraph()
    mq = AsyncQueue()
    store = DictStore("test/alerts")
    detector = GraphDetector(graph, mq, store, notifier)

    httpserver = HTTPListener(mq)
    await asyncio.gather(detector.start(), httpserver.listen())


def test():
    pass


if __name__ == "__main__":
    test()
    asyncio.run(main())
