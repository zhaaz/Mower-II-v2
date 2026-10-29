from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class MarkingState(StrEnum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    FAILED = "failed"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class Point3D:
    x: float
    y: float
    z: float


@dataclass(slots=True)
class StakeoutPoint:
    name: str
    target: Point3D
    marker_code: int = 1
    remark: str = ""
    marking_state: MarkingState = MarkingState.OPEN
    reachable: bool = False

    @property
    def marker_shape(self) -> str:
        return {1: "plus", 2: "cross", 3: "circle_point", 4: "plus_circle"}[self.marker_code]

