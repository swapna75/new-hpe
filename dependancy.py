import asyncio
from log_config import log
from collections import defaultdict
from interfaces import (
    AbstractAlertStore,
    AbstractDetector,
    AbstractMessageQueue,
    AbstractGraph,
    AbstractNotifier,
)
from models import ALERT_STATE, Alert, GraphNode


class node:
    def __init__(self, alert_id) -> None:
        self.alert_id = alert_id
        self.possible_cause: list[node] = []


class GraphDetector(AbstractDetector):
    """This class purely does the operations based on graph traversals
    but the parameter graph is used for dependency usage.
    """

    def __init__(
        self,
        graph: AbstractGraph,
        work_queue: AbstractMessageQueue,
        store: AbstractAlertStore,
        notifier: AbstractNotifier,
    ) -> None:
        self.dep_graph = graph
        self.message_quque = work_queue
        self.root_alerts = set()
        self.alert_paths = defaultdict(list)
        self.service_based_alerts = defaultdict(list)
        self.store = store
        self.notifier = notifier
        self.notifier_tasks = []

    async def start(self):
        while True:
            alerts = await self.message_quque.get()

            for alert in sorted(map(Alert, alerts), key=lambda x: x.startsAt):
                await self.process_alert(alert)

    async def process_alert(self, alert: Alert):
        log.info(f"Processing alert {alert.id}")

        prev_alert = await self.store.get(alert.id)
        if prev_alert:
            if prev_alert.status == ALERT_STATE.FIRING and alert.status == ALERT_STATE.RESOLVED:
                await self.store.remove(alert.id)
                self.root_alerts.discard(alert.id)
                self.alert_paths.pop(alert.id, None)
                return

        # New or firing alert
        await self.store.put(alert.id, alert)
        self.service_based_alerts[alert.service].append(alert.id)

        # If other alerts already present for same service, copy their alert path
        if len(self.service_based_alerts[alert.service]) > 1:
            first_alert_id = self.service_based_alerts[alert.service][0]
            self.alert_paths[alert.id] = self.alert_paths[first_alert_id]
            return

        # Check upstream parents in dependency graph
        alert.parent_count = 0
        try:
            node = self.dep_graph.get_node(GraphNode.get_id(alert.service))
        except Exception as e:
            log.warning(f"Could not fetch node for {alert.service}: {e}")
            return

        for parent in node.parents:
            parent_alerts = self.service_based_alerts.get(parent.id, [])
            for parent_alert_id in parent_alerts:
                self.alert_paths[parent_alert_id].append(alert.id)
                alert.parent_count += 1

        # Flag as root if no parent alerts
        if alert.parent_count == 0:
            log.info(f"Alert {alert.id} flagged as ROOT cause.")
            alert.is_root_cause = True 
            self.root_alerts.add(alert.id)
            self.notifier_tasks.append(self.trigger_notify(alert))

    time_before_trigger = 3

    async def trigger_notify(self, alert: Alert):
        await asyncio.sleep(self.time_before_trigger)
        log.info(f"Notifying about alert {alert.id} {alert.summary}")
        await self.notifier.notify(alert)
