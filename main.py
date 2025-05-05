import asyncio

from listner import HTTPListener

from dependancy import GraphDetector
from graph import ServiceGraph
from notifier import ConsoleNotifier
from message_queue import AsyncQueue


async def main():
    notifier = ConsoleNotifier()
    graph = ServiceGraph()
    mq = AsyncQueue()
    detector = GraphDetector(graph, mq, notifier)

    httpserver = HTTPListener(mq)

    await asyncio.gather(detector.start(), httpserver.listen())


if __name__ == "__main__":
    asyncio.run(main())
