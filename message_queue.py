import asyncio
from interfaces import AbstractMessageQueue


class AsyncQueue(AbstractMessageQueue):
    def __init__(self) -> None:
        self.q = asyncio.Queue()

    def put_nowait(self, event):
        self.q.put_nowait(event)

    async def put(self, event):
        await self.q.put(event)

    async def get(self):
        return await self.q.get()
