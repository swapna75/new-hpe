from . import BaseNotifier, log
from src.models import AlertGroup


class ConsoleNotifier(BaseNotifier):
    async def notify(self, alertg: AlertGroup):
        log.info(
            "*******************************\n"
            f"This is root alert {str(alertg)}\n"
            "*******************************\n"
        )
