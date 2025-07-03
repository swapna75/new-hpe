from datetime import datetime, timezone
from enum import Enum
import hashlib

from .node import GraphNode


class ALERT_STATE(Enum):
    FIRING = 1
    RESOLVED = 2


status = {"resolved": ALERT_STATE.RESOLVED, "firing": ALERT_STATE.FIRING}


# def change_to_date(t_str):
#     dt = datetime.strptime(t_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
#     return dt


def change_to_date(t_str):
    # Accepts both with and without milliseconds
    try:
        return datetime.strptime(t_str, "%Y-%m-%dT%H:%M:%S.%f").replace(
            tzinfo=timezone.utc
        )
    except ValueError:
        return datetime.strptime(t_str, "%Y-%m-%dT%H:%M:%S").replace(
            tzinfo=timezone.utc
        )


class Alert:
    def __init__(self, alert_json: dict) -> None:
        self.alert = alert_json
        self.service_name = alert_json["labels"]["job"]
        # self.service = alert_json["labels"]["job"]
        self.service = GraphNode.get_id(self.service_name)
        self.severity = alert_json["labels"]["severity"]
        self.startsAt = change_to_date(alert_json["startsAt"])
        self.endsAt = change_to_date(alert_json["endsAt"])
        self.status = status[alert_json["status"]]
        self.is_root_cause = False

        self.parent_count = 0
        self.parent_id = ""  # gets updated somewhere.

        self.description = alert_json["annotations"]["description"]
        self.summary = alert_json["annotations"]["summary"]

        # self.id = self.__get_id()
        self.id = f"{self.service}.{self.alert['labels']['instance']}"

    def __str__(self) -> str:
        return f"Alert from service {self.service_name} with name `{self.description}` started at {self.startsAt} with severity {self.severity}"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "parent_id": self.parent_id,
            "service": self.service_name,
            "summary": self.description,
        }

    def __repr__(self) -> str:
        return self.id

    def __get_id(self) -> str:
        s = str(frozenset(self.alert["labels"].items()))
        h = hashlib.sha256(s.encode()).digest()
        return str(int.from_bytes(h, "big"))[:15]
