from interfaces import AbstractMessageQueue, AbstractListener
from aiohttp import web


class HTTPListener(AbstractListener):
    def __init__(self, work_queue: AbstractMessageQueue) -> None:
        self.work_queue = work_queue
        self.app = web.Application()
        self.app.add_routes([web.post("/alert", self.receive_alert)])

        self.runner = web.AppRunner(self.app)
        self.site = None

    async def listen(self):
        await self.runner.setup()
        host = "0.0.0.0"
        port = 8080
        self.site = web.TCPSite(self.runner, host=host, port=port)
        print(f"HTTPListener is running on http://{host}:{port}")
        await self.site.start()

    async def receive_alert(self, request: web.Request):
        try:
            alerts = await request.json()
        except Exception:
            return web.Response(status=400)

        print(f"Received alert: {alerts}")

        # self.work_queue.put_nowait([Alert(x) for x in alerts])
        self.work_queue.put_nowait(alerts)

        return web.Response(status=200)
