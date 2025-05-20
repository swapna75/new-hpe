import asyncio
from collections import defaultdict
from datetime import datetime, timedelta


from src.models import AlertGroup, FeedBack
from src.storage import BaseAlertStore
from . import BaseDetector, log
from src.message_queue import BaseMessageQueue
from src.graph import BaseGraph
from src.notifier import BaseNotifier
from src.models import Alert

DELTA_TIME = timedelta(seconds=30)
CONFIDENCE_THRESHOLD = 0.2

INITIAL_ALPHA = 1
INITIAL_BETA = 1

DELAY = 20


class AlertBatch:
    """Maintains a sliding window batch of alerts and their causal links."""

    def __init__(self, graph: BaseGraph, store: BaseAlertStore, notifier: BaseNotifier):
        self.service_graph = graph
        self.store = store
        self.notifier = notifier

        self.lower_bound: datetime = None
        self.upper_bound: datetime = None

        self.curr_alerts = set()  # set[Alert]
        self.links = {}  # (A.id, B.id) -> (alpha, beta)
        self.service_to_alert: dict[int, set[Alert]] = defaultdict(set)
        self.notify_tasks: dict[int, asyncio.Task] = {}
        self.groups: list[AlertGroup] = []

    def check_temporal(self, alert: Alert):
        if self.lower_bound:
            if not (
                self.lower_bound - DELTA_TIME
                <= alert.startsAt
                <= self.upper_bound + DELTA_TIME
            ):
                return False
        return True

    async def check_and_add_alert(self, alert: Alert):
        temporality = self.check_temporal(alert)
        log.debug(
            f"temporal check for alert {alert.id} {'passed' if temporality else 'falied'}"
        )
        if not temporality:
            return False

        parents = self.service_graph.get_parents(alert.service)
        children = self.service_graph.get_dependents(alert.service)

        linked = False

        for p in parents:
            for p_alert in self.service_to_alert[p.id]:
                linked = True
                if (p_alert.id, alert.id) not in self.links:
                    self.links[(p_alert.id, alert.id)] = [INITIAL_ALPHA, INITIAL_BETA]

        for c in children:
            for c_alert in self.service_to_alert[c.id]:
                linked = True
                if (alert.id, c_alert.id) not in self.links:
                    self.links[(alert.id, c_alert.id)] = [INITIAL_ALPHA, INITIAL_BETA]

        if not linked:
            log.debug("No links found")
            return False

        log.debug("links found")

        self.curr_alerts.add(alert)
        self.service_to_alert[alert.service].add(alert)

        if not self.lower_bound:
            self.lower_bound = self.upper_bound = alert.startsAt
        else:
            self.lower_bound = min(self.lower_bound, alert.startsAt)
            self.upper_bound = max(self.upper_bound, alert.startsAt)

        await self.handle_this_alert(alert)
        return True

    async def handle_this_alert(self, alert: Alert):
        children = []
        parents = []
        for link, vals in self.links.items():
            if alert.id not in link:
                continue

            a, b = link
            if a == alert.id:
                children.append(b)

            if b == alert.id:
                parents.append(a)

        # if this has no parent then this may be a root
        # even if its not then the current alert can be a link to 2 seperate groups

        have_poked_a_child = False
        best_strenght = -float("inf")
        best_child = None
        for child in children:
            decision, strength = self.check_link_strength(alert.id, child)
            log.debug(f"Child: {decision=}, {strength=} for ({alert.id}, {child})")

            if decision:
                if best_strenght < strength:
                    best_strenght = strength
                    best_child = child
                if not len(parents) > 0:
                    have_poked_a_child = True

        have_poked_a_parent = False
        best_strenght = -float("inf")
        best_parent = None
        for parent in parents:
            decision, strength = self.check_link_strength(parent, alert.id)
            log.debug(f"Parent: {decision=}, {strength=} for ({parent}, {alert.id})")
            if decision:
                have_poked_a_parent = True
                if best_strenght < strength:
                    best_strenght = strength
                    best_parent = parent

        # in the further iterations add a case where the strength delta
        # is betweeen them in the less then add multiple childs for the current root.

        if (
            not have_poked_a_child and not have_poked_a_parent
        ):  # assuming no child and no parent
            # create a new group
            log.debug("found no child and parent with strong enough link.")
            alert.group = AlertGroup(alert)
            self.register_as_a_root(alert)
            return
        elif not have_poked_a_parent:  # assuming no parent but a possible child
            log.debug("found only children.")
            # add to childs grp replacing the child as root
            c_alert, _ = await self.store.get(best_child)

            if best_child in self.notify_tasks:
                log.debug(f"the best alert child for the {alert.id} is {best_child}")
                tsk = self.notify_tasks.get(best_child)
                tsk.cancel()

            alert.group = c_alert.group
            self.register_as_a_root(alert)
        elif not have_poked_a_child:  # assuming no child but a parent
            log.debug("found only parent.")
            # add to parents grp without replacing any thing
            p_alert, _ = await self.store.get(best_parent)
            alert.group = p_alert.group
        else:  # assuming both parents and children
            # for now only considering best child and best parent.
            # bridge this alert between them
            log.debug("found both parent and child.")

            p_alert, _ = await self.store.get(best_parent)
            c_alert, _ = await self.store.get(best_child)

            alert.group = p_alert.group
            parent_grp = p_alert.group
            other_grp: AlertGroup = c_alert.group
            for c_al in other_grp.group:  # convert the childs group to this group
                c_al.group = parent_grp
            other_grp.group.clear()  # remove all alerts pointing to it

    def register_as_a_root(self, alert: Alert):
        log.debug(f"registering {alert.id} as root")
        tsk = self.notify_tasks.get(alert.id, None)
        if tsk:
            tsk.cancel()
        grp: AlertGroup = alert.group
        new_tsk = asyncio.create_task(
            self._notify_after_delay(grp.add_root(alert))
        )  # change this to new task that registered as wait time and send the request.
        self.notify_tasks[alert.id] = new_tsk

    def check_link_strength(self, parent_id: int, child_id: int) -> tuple[bool, float]:
        alpha, beta_ = self.links.get(
            (parent_id, child_id), (INITIAL_ALPHA, INITIAL_BETA)
        )
        total = alpha + beta_

        strength = alpha / total

        should = strength >= 0.3
        return should, strength

    async def _notify_after_delay(self, group: AlertGroup):
        root = group.root
        try:
            await asyncio.sleep(DELAY)
            log.info(f"Notifying root={root.id} for {len(group.group)} alerts")
            await self.notifier.notify(group)
        except asyncio.CancelledError:
            log.debug(
                f"Notify task cancelled for group with root {str(group.root.id)[:10]} (new alert arrived)."
            )


class ProbabilityDetector(BaseDetector):
    """
    Learns causal link strengths with on-the-fly feedback.
    """

    def __init__(
        self,
        graph: BaseGraph,
        work_queue: BaseMessageQueue,
        store: BaseAlertStore,
        notifier: BaseNotifier,
    ):
        super().__init__(graph, work_queue, store, notifier)

        self.counts = defaultdict(lambda: [INITIAL_ALPHA, INITIAL_BETA])
        self.batches: list[AlertBatch] = []

    async def process_alert(self, alert: Alert):
        log.debug(f"Processing alert {alert.id} {alert.service_name} {alert.summary}")
        for batch in self.batches:
            if await batch.check_and_add_alert(alert):
                log.debug("added alert to an already present batch.")
                alert.batch = batch
                return

        log.debug(
            "Creating new batch because the alert is not linkable to other batches."
        )

        new_batch = AlertBatch(self.service_graph, self.store, self.notifier)
        new_batch.curr_alerts.add(alert)
        new_batch.service_to_alert[alert.service].add(alert)
        alert.batch = new_batch
        alert.group = AlertGroup(alert)
        new_batch.register_as_a_root(alert)
        self.batches.append(new_batch)

    async def feedback_handler(self, fb: FeedBack):
        for (cause, effect), confirmed in fb.relations.items():
            key = (cause.id, effect.id)
            alpha, beta_ = self.counts[key]
            beta_ += 1  # one more trial
            if confirmed:
                alpha += 1  # one more success
            self.counts[key] = [alpha, beta_]

            # Propagate to any open batches so their link strengths are up-to-date:
            for batch in self.batches:
                if key in batch.links:
                    batch.links[key] = [alpha, beta_]
        log.info("Causal link counts updated from feedback.")
