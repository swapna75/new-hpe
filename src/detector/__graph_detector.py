import asyncio
from log_config import log
from collections import defaultdict

from src.models import AlertGroup
from src.storage import BaseAlertStore
from . import BaseDetector
from src.message_queue import BaseMessageQueue
from src.graph import BaseGraph
from src.notifier import BaseNotifier
from models import ALERT_STATE, Alert, GraphNode


class GraphDetector(BaseDetector):
    """
    Tracks causal relationships between alerts based on a dependency graph.

    Behavior:
    1. On new/firing alert: link to any parent-alerts, or mark as root and schedule notify.
    2. On resolved alert: cancel any pending notify, clean up links and store.
    3. If a parent-alert arrives during a root-alert's waiting period, cancel the root notify.
    """

    def __init__(
        self,
        graph: BaseGraph,
        work_queue: BaseMessageQueue,
        store: BaseAlertStore,
        notifier: BaseNotifier,
    ) -> None:
        self.dep_graph = graph
        self.queue = work_queue
        self.store = store
        self.notifier = notifier

        # Active alerts by service
        self.active_by_service: dict[str, list[str]] = defaultdict(list)
        # Causal links: parent alert -> [child alerts]
        self.children: dict[str, list[str]] = defaultdict(list)
        # Pending root notifications: alert_id -> Task
        self.notify_tasks: dict[str, asyncio.Task] = {}
        # Alerts flagged as root cause
        self.roots: set[str] = set()

        # Delay before actual notification
        self.delay = 40

    async def start(self):
        while True:
            batch = await self.queue.get()
            for raw in sorted(batch, key=lambda x: x.get("startsAt")):
                alert = Alert(raw)
                if alert.severity == "critical":
                    await self.process_alert(alert)

    async def process_alert(self, alert: Alert):
        log.debug(f"Processing alert {alert.id} ({alert.service})")

        # Handle resolved first
        stored = await self.store.get(alert.id)
        if stored:
            if (
                stored.status == ALERT_STATE.FIRING
                and alert.status == ALERT_STATE.RESOLVED
            ):
                await self._handle_resolved(alert)
            else:
                log.debug("Duplicate alert detected skipping.")
                pass
            return

        # Store or update
        await self.store.put(alert.id, alert)
        self.active_by_service[alert.service].append(alert.id)

        # Link to any waiting root children: if this alert is parent to any roots
        await self._cancel_roots_for_parent(alert)

        # Find any parent alerts for this service
        try:
            node = self.dep_graph.get_node(GraphNode.get_id(alert.service))
        except Exception as e:
            log.warning(f"Graph node missing for {alert.service}: {e}")
            return

        parent_ids = []
        for p in node.parents:
            parent_ids.extend(self.active_by_service.get(p.service, []))

        if parent_ids:
            # Link this alert under each parent
            for pid in parent_ids:
                self.children[pid].append(alert.id)
                log.info(f"Linked {alert.id} as child of {pid}")
            # If we had scheduled this as root, cancel it
            if alert.id in self.notify_tasks:
                self._cancel_notify(alert.id)
            return

        # No parent alerts: candidate root
        if alert.id in self.notify_tasks:
            # Already pending; skip
            return

        log.info(
            f"Alert {alert.id} is potential root; scheduling notify in {self.delay}s."
        )
        alert.is_root_cause = True
        self.roots.add(alert.id)
        task = asyncio.create_task(self._notify_after_delay(alert))
        self.notify_tasks[alert.id] = task

    async def _handle_resolved(self, alert: Alert):
        log.debug(f"Resolving alert {alert.id}; cleaning up.")
        # Cancel notify if pending
        if alert.id in self.notify_tasks:
            self._cancel_notify(alert.id)

        # Cleanup data
        self.roots.discard(alert.id)
        self.children.pop(alert.id, None)
        await self.store.remove(alert.id)
        self.active_by_service.get(alert.service, []).remove(alert.id)

    async def _cancel_roots_for_parent(self, parent: Alert):
        """
        If a root candidate exists for which this alert.service is a parent, cancel it.
        """
        try:
            pnode = self.dep_graph.get_node(GraphNode.get_id(parent.service))
        except Exception:
            return

        # For every waiting root alert, check if parent.service is upstream
        for rid in list(self.roots):
            ralert = await self.store.get(rid)
            if not ralert:
                continue
            try:
                rnode = self.dep_graph.get_node(GraphNode.get_id(ralert.service))
            except Exception:
                continue

            # If this new alert is a parent of the root's service, cancel root
            if any(p.id == pnode.id for p in rnode.parents):
                log.info(f"Cancelling root {rid}; parent {parent.id} arrived.")
                self._cancel_notify(rid)
                self.roots.discard(rid)
                self.children[parent.id].append(rid)
                log.info(f"Linked {rid} as child of {parent.id}")

    def _cancel_notify(self, alert_id: str):
        """Cancel a pending notify task"""
        task = self.notify_tasks.pop(alert_id, None)
        if task and not task.done():
            task.cancel()
        # Mark not a root
        # Assume Alert object updates in store

    async def _notify_after_delay(self, alert: Alert):
        try:
            await asyncio.sleep(self.delay)
            log.info(f"Notifying about root alert {alert.id}")
            # await self.notifier.notify(alert)  # change
            await self.notifier.notify(AlertGroup())  # change
        except asyncio.CancelledError:
            log.info(f"Notification for {alert.id} cancelled.")
        finally:
            # Cleanup task record
            self.notify_tasks.pop(alert.id, None)
