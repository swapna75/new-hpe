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
    but the parameter graph is used for dependency uasage.
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
        if prev_alert := await self.store.get(alert.id):
            if (
                prev_alert.status == ALERT_STATE.FIRING
                and alert.status == ALERT_STATE.RESOLVED
            ):
                await self.store.remove(alert.id)
                if alert.id in self.root_alerts:
                    self.root_alerts.remove(alert.id)
                if alert.id in self.alert_paths:
                    for child_alert in self.alert_paths[alert.id]:
                        child_alert.parent_count -= 1
                        if child_alert.parent_count == 0:
                            self.alert_paths.pop(child_alert.id, None)
                return
        # if not_found then raised first time probably.
        await self.store.put(alert.id, alert)
        self.service_based_alerts[alert.service].append(alert.id)
        if len(self.service_based_alerts[alert.service]) != 1:
            other_alert_id = self.service_based_alerts[alert.service][0]

            self.alert_paths[alert.id] = self.alert_paths[other_alert_id]
            return

        # find parent alerts

        for parent in self.dep_graph.get_node(GraphNode.get_id(alert.service)).parents:
            parent_alerts = self.service_based_alerts[parent.id]
            if len(parent_alerts) == 0:
                continue

            for possible_parent in parent_alerts:
                self.alert_paths[possible_parent.id].append(alert.id)
                alert.parent_count += 0
        if alert.parent_count == 0:
            log.info(f"Added alert {alert.id} to root alert to be notifed")
            self.root_alerts.add(alert.id)
            self.notifier_tasks.append(self.trigger_notify(alert))
        return

    # async def walkthrough_graph(self, node_id):
    #     self.alert_paths[node_id] = self.alert_paths.get(node_id, set())
    #     for parent in self.dep_graph.get_node(node_id).parents:
    #         if parent in self.alert_paths:
    #             self.alert_paths[node_id].add(parent)
    #     if len(self.alert_paths[node_id]):
    #         self.root_alerts.add(node_id)
    #         return True
    #     return False
    #

    time_before_trigger = 3

    async def trigger_notify(self, alert: Alert):
        await asyncio.sleep(self.time_before_trigger)
        log.info(f"Notifying about alert {alert.id} {alert.summary}")
        await self.notifier.notify(alert)
