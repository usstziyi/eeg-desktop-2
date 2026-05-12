from __future__ import annotations

from dataclasses import dataclass
from time import time


@dataclass(frozen=True)
class Marker:
    value: float
    label: str
    created_at: float


def make_marker(label: str, value: float | None = None) -> Marker:
    now = time()
    return Marker(value=value if value is not None else now, label=label, created_at=now)

