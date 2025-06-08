import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import json

from src.notifier import ConsoleNotifier
from src.graph import ServiceGraph
from src.listners import HTTPListener
from src.message_queue import AsyncQueue
from src.detector import ProbabilityDetector
from src.storage import DictStore
from src.preprocessing.causal_inference import compute_alpha_beta_links
from src.models.alert import Alert


async def main():
    notifier = ConsoleNotifier()
    graph = ServiceGraph()
    mq = AsyncQueue()
    store = DictStore("test/alerts")

    with open("historical_alerts.json", "r") as f:
        alert_jsons = json.load(f)["alerts"]

    historical_alerts = []
    for alert_data in alert_jsons:
        try:
            alert = Alert(alert_data)
            if graph.has_node(alert.service):
                historical_alerts.append(alert)
        except Exception as e:
            print(f"[WARNING] Skipping invalid alert: {e}")

    # Compute α/β link strengths using valid historical alerts
    precomputed_links = compute_alpha_beta_links(historical_alerts, graph)
    print("Preprocessing summary:")
    print(f"Total historical alerts used: {len(historical_alerts)}")
    print(f"Total computed links: {len(precomputed_links)}")

    for i, ((src, dst), (alpha, beta)) in enumerate(precomputed_links.items()):
        print(f"Link {i + 1}: {src} → {dst} | α={alpha}, β={beta}")
        if i == 4:
            break

    # Initialize detector
    detector = ProbabilityDetector(graph, mq, store, notifier, precomputed_links)

    # Set up listener and start services
    httpserver = HTTPListener(mq)
    httpserver.set_feedback_listner(detector.feedback_handler)
    await asyncio.gather(detector.start(), httpserver.listen())


if __name__ == "__main__":
    asyncio.run(main())
