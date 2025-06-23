from . import BaseNotifier
from src.models import AlertGroup


class ConsoleNotifier(BaseNotifier):
    async def notify(self, alertg: AlertGroup):
        print(
            f"*******************************\nThis is root alert {str(alertg.root)}\n"
        )
        for a in alertg.group:
            print(a)
        print("*******************************\n")
