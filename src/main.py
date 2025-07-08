from pathlib import Path
import sys
import os

from src.graph.__base import BaseGraph
from src.storage.__base import BaseAlertStore

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import json

from src.notifier import WsNotifier
from src.graph import ServiceGraph
from src.listners import HTTPListener
from src.message_queue import AsyncQueue
from src.detector import ProbabilityDetector
from src.storage import DictStore
from src.preprocessing.causal_inference import compute_alpha_beta_links
from src.models.alert import Alert
from src.preprocessing.csv_preprocessor import load_and_preprocess


async def preprocess(graph: BaseGraph, store: BaseAlertStore):
    """
    The original preprocessing: reads historical JSON alerts and computes α/β links.
    """
    data_path = Path(__file__).parent.parent / "test_data/data"
    alert_jsons = []
    for f in data_path.iterdir():
        if f.suffix != ".json":  
            continue
        with open(f, "r") as fp:
            alerts = json.load(fp)
            alert_jsons.extend(alerts)
    historical_alerts = [Alert(a) for a in alert_jsons]

    # Compute α/β link strengths using valid historical alerts
    precomputed_links = await compute_alpha_beta_links(historical_alerts, store, graph)
    print("Preprocessing summary:")
    print(f"Total historical alerts used: {len(historical_alerts)}")
    print(f"Total computed links: {len(precomputed_links)}")

    print("Head of the computed links.")
    for i, ((src, dst), (alpha, beta)) in enumerate(precomputed_links.items()):
        print(f"Link {i + 1}: {src} → {dst} | α={alpha}, β={beta}")
        if i == 4:
            break

    return precomputed_links


def csv_preprocess_example():
    """
    New CSV preprocessing: reads the single CSV file, splits and normalizes features.
    """
    csv_path = Path(__file__).parent.parent / "test_data/data/all_alerts.csv"
    if not csv_path.exists():
        print(f"CSV file {csv_path} not found. Skipping CSV preprocessing.")
        return
    X_train, X_test, y_train, y_test = load_and_preprocess(str(csv_path))
    print("CSV Preprocessing completed.")
    print(f"X_train shape: {X_train.shape}")
    print(f"X_test shape: {X_test.shape}")
    return X_train, X_test, y_train, y_test


async def main(config):
    notifier = WsNotifier()
    graph = ServiceGraph("test_data/test_service_map.yaml")
    mq = AsyncQueue()
    store = DictStore("test/alerts")
    csv_preprocess_example()
    precomputed_links = await preprocess(graph, store)
    detector = ProbabilityDetector(graph, mq, store, notifier, precomputed_links)
    httpserver = HTTPListener(mq, notifier)
    httpserver.set_feedback_listner(detector.feedback_handler)
    try:
        await asyncio.gather(detector.start(), httpserver.listen())
    except asyncio.CancelledError:
        print()
        await httpserver.close()
        await notifier.free_wsockets()
        raise


def parse_config():
    pass


if __name__ == "__main__":
    try:
        cfg = parse_config()
        asyncio.run(main(cfg))
    except KeyboardInterrupt:
        print("Exiting the application.")
