from interfaces import AbstractAlertStore


class DictStore(AbstractAlertStore):
    def __init__(self) -> None:
        self.store = {}

    async def put(self, id, alert):
        self.store[id] = alert

    async def get(self, id):
        return self.store[id]
