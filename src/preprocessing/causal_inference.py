from collections import defaultdict
from datetime import timedelta

DELTA_TIME = timedelta(seconds=2)
INITIAL_ALPHA = 1
INITIAL_BETA = 1


def is_temporally_valid(a, b, delta=DELTA_TIME):
    """Checks if a could have caused b based on time."""
    return a.startsAt <= b.startsAt <= a.startsAt + delta


def preprocess_alert_links(alerts, graph, time_threshold=DELTA_TIME):
    """
    Computes alpha-beta link strengths from historical alerts.
    Returns: dict[(parent_id, child_id)] = [alpha, beta]
    """
    alerts = sorted(alerts, key=lambda a: a.startsAt)
    service_to_alerts = defaultdict(list)
    links = defaultdict(lambda: [INITIAL_ALPHA, INITIAL_BETA])

    for alert in alerts:
        service_to_alerts[alert.service].append(alert)

    for alert in alerts:
        parent_services = graph.get_parents(alert.service)
        for p_service in parent_services:
            for parent_alert in service_to_alerts.get(p_service.id, []):
                if is_temporally_valid(parent_alert, alert, delta=time_threshold):
                    links[(parent_alert.id, alert.id)][0] += 1
                else:
                    links[(parent_alert.id, alert.id)][1] += 1

        for same_alert in service_to_alerts.get(alert.service, []):
            if same_alert.id == alert.id:
                continue
            if is_temporally_valid(same_alert, alert):
                links[(same_alert.id, alert.id)][0] += 1
            else:
                links[(same_alert.id, alert.id)][1] += 1

    return links
