import asyncio
import json

from src.notifier import ConsoleNotifier
from src.graph import ServiceGraph
from src.listners import HTTPListener
from src.message_queue import AsyncQueue
from src.detector import ProbabilityDetector
from src.storage import DictStore
from src.preprocessing.causal_inference import preprocess_alert_links
from src.models.alert import Alert


async def main():
    notifier = ConsoleNotifier()
    graph = ServiceGraph()
    mq = AsyncQueue()
    store = DictStore("test/alerts")
    
    # Load historical data
    with open("historical_alerts.json", "r") as f:
        alert_jsons = json.load(f)["alerts"]
    historical_alerts = [Alert(a) for a in alert_jsons]

    # Compute α/β strengths
    precomputed_links = preprocess_alert_links(historical_alerts, graph)

    # Initialize detector with historical knowledge
    detector = ProbabilityDetector(graph, mq, store, notifier, precomputed_links)

    httpserver = HTTPListener(mq)
    httpserver.set_feedback_listner(detector.feedback_handler)

    await asyncio.gather(detector.start(), httpserver.listen())


if __name__ == "__main__":
    asyncio.run(main())
