import asyncio

from listner import HTTPListener

from log_config import log
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
    log.info("Starting server the detector application.")

    await asyncio.gather(detector.start(), httpserver.listen())


if __name__ == "__main__":
    asyncio.run(main())
