from enum import Enum


class GraphNode:
    srevice_to_id = {}

    def __init__(
        self,
        id: int,
        service: str,
        parents: set | None = None,
        children: set | None = None,
    ) -> None:
        self.id = id
        self.service = service

        # edges with dependency information.
        self.parents: set[GraphNode] = parents or set()
        self.children: set[GraphNode] = children or set()

        self.srevice_to_id[service] = id

    def __hash__(self) -> int:
        return hash(self.id)

    @classmethod
    def get_id(cls, service):
        return hash(cls.srevice_to_id.get(service, None))


class ALERT_STATE(Enum):
    FIRING = 1
    RESOLVED = 2


status = {"resolved": ALERT_STATE.RESOLVED, "firing": ALERT_STATE.FIRING}


class Alert:
    def __init__(self, alert_json: dict) -> None:
        self.alert = alert_json
        self.service = alert_json["labels"]["job"]
        self.severity = alert_json["labels"]["severity"]
        self.startsAt = alert_json["startsAt"]
        self.endsAt = alert_json["endsAt"]
        self.status = status[alert_json["status"]]
        self.is_root_cause = False

        self.parent_count = 0

        self.decription = alert_json["annotations"]["description"]
        self.summary = alert_json["annotations"]["summary"]

        # self.id = self.__get_id()
        self.id = self.service + "-" + self.summary

    def __str__(self) -> str:
        return f"Alert from service {self.service} started at {self.startsAt} with severity {self.severity}"

    def __get_id(self):
        return frozenset(self.alert["labels"].items())
