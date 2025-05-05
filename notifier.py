from interfaces import AbstractNotifier
from models import Alert


class ConsoleNotifier(AbstractNotifier):
    async def notify(self, alert: Alert):
        print("This is root alert", str(alert))
