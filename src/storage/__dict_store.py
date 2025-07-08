import json
from datetime import datetime
from . import BaseAlertStore

class DictStore(BaseAlertStore):
    def __init__(self, file_path: str) -> None:
        self.store = {}
        self.file_path = file_path
        self.file = open(self.file_path, 'a')  # open once in append mode

    async def put(self, id, alert):
        self.store[id] = [alert, self.store.get(id, [None, 0])[1] + 1]
        # stream the alert to file
        date_str = datetime.utcnow().strftime('%Y-%m-%d')
        record = {
            "date": date_str,
            "id": id,
            "alert": alert.to_dict() if hasattr(alert, 'to_dict') else str(alert)
        }
        self.file.write(json.dumps(record) + '\n')
        self.file.flush()

    async def get(self, id):
        return self.store.get(id, [None, 0])

    async def has(self, id):
        return id in self.store

    async def get_count(self, id):
        return self.store.get(id, [None, 0])[1]

    async def remove(self, id):
        self.store[id][1] = 0

    def __del__(self):
        if not self.file.closed:
            self.file.close()
