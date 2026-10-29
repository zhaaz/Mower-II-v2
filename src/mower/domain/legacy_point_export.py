from __future__ import annotations

from pathlib import Path

from .models import StakeoutPoint


HEADER_LINES = (
    "// Mower II Punktimport",
    "// Format: punktnummer x y z kennziffer \"bemerkung\" // Kommentar",
    "// XYZ in mm",
    "// Point. X. Y. Z. Markierung Bemerkung",
    "",
)


def legacy_point_text(points: list[StakeoutPoint]) -> str:
    if not points:
        raise ValueError("Mindestens ein Punkt ist für den Export erforderlich")
    lines = list(HEADER_LINES)
    for point in points:
        remark = _safe_remark(point.remark)
        lines.append(
            f"{point.name}  "
            f"{point.target.x:.6f}  "
            f"{point.target.y:.6f}  "
            f"{point.target.z:.6f}  "
            f"{point.marker_code}  "
            f'"{remark}"'
        )
    return "\n".join(lines) + "\n"


def save_legacy_point_file(
    path: str | Path,
    points: list[StakeoutPoint],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(target.suffix + ".tmp")
    temporary.write_text(legacy_point_text(points), encoding="utf-8")
    temporary.replace(target)


def _safe_remark(text: str) -> str:
    return " ".join(str(text).replace('"', "'").split())
