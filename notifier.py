from interfaces import AbstractNotifier
from log_config import log
from models import Alert


class ConsoleNotifier(AbstractNotifier):
    async def notify(self, alert: Alert):
        log.info("This is root alert", str(alert))
