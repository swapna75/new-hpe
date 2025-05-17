from . import BaseNotifier
from log_config import log
from models import AlertGroup


class ConsoleNotifier(BaseNotifier):
    async def notify(self, alert: AlertGroup):
        log.info(
            "*******************************\n"
            f"This is root alert {str(alert)}\n"
            "*******************************\n"
        )
