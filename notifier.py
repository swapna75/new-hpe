from interfaces import BaseNotifier
from log_config import log
from models import Alert


class ConsoleNotifier(BaseNotifier):
    async def notify(self, alert: Alert):
        log.info(
            "*******************************\n"
            f"This is root alert {str(alert)}\n"
            "*******************************\n"
        )
