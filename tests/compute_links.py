import json
from pathlib import Path
import _path

from src.models.alert import Alert
from src.preprocessing import batch_alerts

_path.m = None


data_path = Path(__file__).parent.parent / "test_data/data"


def get_batches(data_path):
    with open(data_path, "r") as f:
        rows = json.load(f)

    alerts = []
    for r in rows:
        a = Alert(r)
        alerts.append(a)

    batches = batch_alerts(alerts)
    return batches


async def test_splits_for_all():
    final_batches = []
    for f in data_path.iterdir():
        if f.is_file():
            final_batches.extend(get_batches(f))
    return final_batches


if __name__ == "__main__":
    pass
