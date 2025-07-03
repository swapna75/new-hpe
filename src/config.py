from datetime import timedelta
import sys
from attr import dataclass
import yaml


@dataclass
class AppConfig:
    batch_gap_threshold: timedelta = timedelta(minutes=15)
    time_delta: timedelta = timedelta(minutes=3)
    confidence_threshold: float = 0.2

    initial_alpha: int = 1
    initial_beta: int = 1

    delay: int = 5


def load_config(path: str) -> AppConfig:
    with open(path, "r") as f:
        raw = yaml.safe_load(f)
    raw["time_delta"] = timedelta(minutes=raw["time_delta"])
    raw["batch_gap_threshold"] = timedelta(minutes=raw["batch_gap_threshold"])

    return AppConfig(**raw)


cfg_path = "config.yaml" if len(sys.argv) <= 1 else sys.argv[1]
cfg_path = "config.yaml" if not cfg_path else cfg_path  # check full null value.
cfg = load_config(cfg_path)
