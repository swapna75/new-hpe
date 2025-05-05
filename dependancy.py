import asyncio
from interfaces import (
    AbstractDetector,
    AbstractMessageQueue,
    AbstractGraph,
    AbstractNotifier,
)
from models import Alert, GraphNode


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
        notifier: AbstractNotifier,
    ) -> None:
        self.dep_graph = graph
        self.message_quque = work_queue
        self.root_alerts = set()
        self.alert_paths = {}
        self.notifier = notifier
        self.notifier_tasks = []

    async def start(self):
        while True:
            alerts = await self.message_quque.get()

            for alert in alerts:
                await self.process_alert(Alert(alert))

    async def process_alert(self, alert: Alert):
        service = alert.service
        node_id = GraphNode.get_id(service)

        # if this case passed then -> already this alert is being porcessed or similar alert is raised and processed so skip
        if node_id not in self.alert_paths:
            if await self.walkthrough_graph(node_id):
                self.notifier_tasks.append(self.notifier.notify(alert))

    async def walkthrough_graph(self, node_id):
        self.alert_paths[node_id] = self.alert_paths.get(node_id, set())
        for parent in self.dep_graph.get_node(node_id).parents:
            if parent in self.alert_paths:
                self.alert_paths[node_id].add(parent)
        if len(self.alert_paths[node_id]):
            self.root_alerts.add(node_id)
            return True
        return False

    time_before_trigger = 3

    async def trigger_notify(self, alert: Alert):
        await asyncio.sleep(self.time_before_trigger)
        await self.notifier.notify(alert)
