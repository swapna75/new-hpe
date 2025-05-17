from enum import Enum


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
