from collections import defaultdict
from datetime import timedelta
import sys
from typing import List, Dict, Tuple

from src.models.alert import Alert


DELTA_TIME = timedelta(minutes=2)
BATCH_GAP_THRESHOLD = timedelta(minutes=15)
INITIAL_ALPHA = 1
INITIAL_BETA = 1


def is_temporally_valid(parent_alert, child_alert, delta=DELTA_TIME) -> bool:
    """Checks if parent_alert could have caused child_alert based on timestamp."""
    return (
        parent_alert.startsAt <= child_alert.startsAt <= parent_alert.startsAt + delta
    )


def batch_alerts(
    alerts: List[Alert], gap_threshold=BATCH_GAP_THRESHOLD
) -> List[List[Alert]]:
    """Splits a sorted list of alerts into time-separated batches."""
    alerts = sorted(alerts, key=lambda a: a.startsAt)
    batches = []
    current_batch = []

    for alert in alerts:
        if not current_batch:
            current_batch.append(alert)
            continue

        if alert.startsAt - current_batch[-1].startsAt > gap_threshold:
            batches.append(current_batch)
            current_batch = [alert]
        else:
            current_batch.append(alert)

    if current_batch:
        batches.append(current_batch)

    return batches


def process_batch(
    batch: List, graph, delta=DELTA_TIME
) -> Dict[Tuple[str, str], List[int]]:
    """Processes a single batch of alerts and returns alpha-beta updates."""
    links = defaultdict(lambda: [INITIAL_ALPHA, INITIAL_BETA])
    service_to_alerts = defaultdict(list)

    for alert in batch:
        service_to_alerts[alert.service].append(alert)

    for alert in batch:
        parent_services = graph.get_parents(alert.service)

        # Topological links (parent → child)
        for p_service in parent_services:
            for parent_alert in service_to_alerts.get(p_service.id, []):
                if parent_alert.id == alert.id:
                    continue

                key = (parent_alert.id, alert.id)
                if is_temporally_valid(parent_alert, alert, delta):
                    links[key][0] += 1  # alpha
                else:
                    links[key][1] += 1  # beta

        # Same-service links
        for same_alert in service_to_alerts[alert.service]:
            if same_alert.id == alert.id:
                continue

            key = (same_alert.id, alert.id)
            if is_temporally_valid(same_alert, alert, delta):
                links[key][0] += 1
            else:
                links[key][1] += 1

    return links


def compute_alpha_beta_links(
    alerts: List, graph, delta=DELTA_TIME, gap_threshold=BATCH_GAP_THRESHOLD
):
    """Runs full pipeline: batching + per-batch processing."""
    total_links = defaultdict(lambda: [INITIAL_ALPHA, INITIAL_BETA])
    batches = batch_alerts(alerts, gap_threshold)

    for batch in batches:
        batch_links = process_batch(batch, graph, delta)

        for key, (a, b) in batch_links.items():
            total_links[key][0] += a - INITIAL_ALPHA  # skip initial count in each batch
            total_links[key][1] += b - INITIAL_BETA
    return total_links


if __name__ == "__main__":
    map_dir = sys.argv[1]
    data_dir = sys.argv[2]
