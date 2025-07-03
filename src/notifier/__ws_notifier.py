import logging
from aiohttp import web
from src.notifier.__base import BaseNotifier
from src.models import AlertGroup


logger = logging.getLogger(__name__)


class WsNotifier(BaseNotifier):
    def __init__(self) -> None:
        super().__init__()

        self.wsockets: set[web.WebSocketResponse] = set()
        self.groups = {}

    async def notify(self, alertg: AlertGroup):
        try:
            print("came")
            logger.info(
                f"Seding data about alert group to all the websockets. {str(alertg)}"
            )
            self.groups[alertg.grp_id] = alertg
            for soc in self.wsockets:
                await soc.send_str(str(alertg))
        except Exception as e:
            logger.error("Some error occoured while sending data", e)
            raise

    async def delete_websocket(self, soc: web.WebSocketResponse):
        self.wsockets.remove(soc)

    async def add_wsocket(self, soc: web.WebSocketResponse):
        logger.debug(
            "Seding data about all alert groups to all the new websocket coneection.",
        )
        self.wsockets.add(soc)
        for g in self.groups:
            await soc.send_str(str(g))

    async def free_wsockets(self):
        for ws in list(self.wsockets):
            if ws.closed:
                continue

            await ws.close()

    async def delete_group(self, gid):
        del self.groups[gid]
