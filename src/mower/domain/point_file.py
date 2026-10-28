from __future__ import annotations

import re
from pathlib import Path

from .models import Point3D, StakeoutPoint

VALID_MARKER_CODES = {1, 2, 3, 4}


def parse_point_line(line: str, line_number: int) -> StakeoutPoint | None:
    raw = line.strip()
    if not raw or raw.startswith(("#", "//")):
        return None
    text = _strip_comment(raw)
    quoted = re.findall(r'"([^"]*)"', text)
    remark = quoted[0].strip() if quoted else ""
    text = re.sub(r'"[^"]*"', " ", text)
    text = re.sub(r"(?<=\d),(?=\d)", ".", text)
    parts = text.replace(";", " ").replace(",", " ").split()
    if not parts:
        return None
    if parts[0].lower().strip(".:") in {
        "id", "name", "punkt", "punktname", "point", "pointnumber", "punktnummer"
    }:
        return None
    if len(parts) < 4:
        raise ValueError(f"Zeile {line_number}: mindestens Punktnummer X Y Z erwartet")
    try:
        target = Point3D(*(float(value.replace(",", ".")) for value in parts[1:4]))
    except ValueError as exc:
        if line_number <= 10:
            return None
        raise ValueError(f"Zeile {line_number}: ungültige Koordinaten") from exc
    rest = parts[4:]
    marker_code = 1
    if rest and re.fullmatch(r"[+-]?\d+", rest[0]):
        marker_code = int(rest.pop(0))
    if marker_code not in VALID_MARKER_CODES:
        raise ValueError(f"Zeile {line_number}: unbekannte Marker-Kennziffer {marker_code}")
    if not remark:
        remark = " ".join(rest)
    return StakeoutPoint(parts[0], target, marker_code, remark)


def load_points(path: str | Path) -> list[StakeoutPoint]:
    source = Path(path)
    points = [
        point
        for number, line in enumerate(source.read_text(encoding="utf-8-sig").splitlines(), 1)
        if (point := parse_point_line(line, number)) is not None
    ]
    if not points:
        raise ValueError(f"Keine Punkte in Datei gefunden: {source}")
    return points


def _strip_comment(text: str) -> str:
    quoted = False
    for index in range(len(text) - 1):
        if text[index] == '"':
            quoted = not quoted
        if not quoted and text[index:index + 2] == "//":
            return text[:index].rstrip()
    return text

