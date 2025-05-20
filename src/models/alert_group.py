from src.models import Alert


class AlertGroup:
    def __init__(self, root: Alert = None) -> None:
        self.root = root
        self.group = set()
        self.h = hash(self.root)

    def add_root(self, root: Alert):
        self.h -= hash(self.root)
        self.root = root
        self.h += hash(root)
        return self

    def add_other(self, other: Alert):
        if other not in self.group:
            self._update_hash(other)
        self.group.add(other)
        return self

    def remove_other(self, other: Alert):
        if other in self.group:
            self._update_hash(other, rev=True)
            self.group.remove(other)
        return self

    def _update_hash(self, other: Alert, rev=False):
        self.h = (-1 if rev else 1) * hash(other) + self.h

    def __hash__(self) -> int:
        return self.h

    def __str__(self) -> str:
        return f"<AlertGroup with root: {self.root} ({self.root.summary}, {self.root.service})>"
