from __future__ import annotations

import csv
import shlex
from dataclasses import dataclass
from pathlib import Path

from .models import Point3D, StakeoutPoint
from .point_file import VALID_MARKER_CODES


@dataclass(frozen=True, slots=True)
class PointImportSettings:
    delimiter: str = "whitespace"
    skip_rows: int = 0
    decimal_separator: str = "."
    id_column: int = 0
    x_column: int = 1
    y_column: int = 2
    z_column: int = 3
    marker_column: int | None = 4
    remark_column: int | None = 5

    def validate(self) -> None:
        if self.skip_rows < 0:
            raise ValueError("Die Anzahl übersprungener Zeilen darf nicht negativ sein")
        if self.decimal_separator not in {".", ","}:
            raise ValueError("Dezimalzeichen muss Punkt oder Komma sein")
        required = {
            "ID": self.id_column,
            "X": self.x_column,
            "Y": self.y_column,
            "Z": self.z_column,
        }
        if any(value < 0 for value in required.values()):
            raise ValueError("ID, X, Y und Z müssen einer Spalte zugeordnet sein")
        if len(set(required.values())) != len(required):
            raise ValueError("ID, X, Y und Z müssen unterschiedliche Spalten verwenden")
        optional = [
            value
            for value in (self.marker_column, self.remark_column)
            if value is not None
        ]
        if len(optional) != len(set(optional)):
            raise ValueError("Optionale Felder dürfen nicht dieselbe Spalte verwenden")
        if set(required.values()).intersection(optional):
            raise ValueError("Eine Spalte darf nur einem Feld zugeordnet sein")
        if self.delimiter != "whitespace" and len(self.delimiter) != 1:
            raise ValueError("Das benutzerdefinierte Trennzeichen muss genau ein Zeichen lang sein")
        if self.delimiter == self.decimal_separator:
            raise ValueError("Trennzeichen und Dezimalzeichen dürfen nicht identisch sein")


@dataclass(frozen=True, slots=True)
class PreviewRow:
    physical_line: int
    columns: tuple[str, ...]


def preview_rows(
    path: str | Path,
    delimiter: str,
    skip_rows: int,
    limit: int = 25,
) -> list[PreviewRow]:
    source = Path(path)
    rows: list[PreviewRow] = []
    for physical_line, raw_line in enumerate(
        source.read_text(encoding="utf-8-sig").splitlines(),
        1,
    ):
        if physical_line <= skip_rows:
            continue
        columns = split_line(raw_line, delimiter)
        if columns is None:
            continue
        rows.append(PreviewRow(physical_line, tuple(columns)))
        if len(rows) >= limit:
            break
    return rows


def load_points_with_settings(
    path: str | Path,
    settings: PointImportSettings,
) -> list[StakeoutPoint]:
    settings.validate()
    source = Path(path)
    points: list[StakeoutPoint] = []
    required_max = max(
        settings.id_column,
        settings.x_column,
        settings.y_column,
        settings.z_column,
        settings.marker_column if settings.marker_column is not None else 0,
        settings.remark_column if settings.remark_column is not None else 0,
    )
    for physical_line, raw_line in enumerate(
        source.read_text(encoding="utf-8-sig").splitlines(),
        1,
    ):
        if physical_line <= settings.skip_rows:
            continue
        columns = split_line(raw_line, settings.delimiter)
        if columns is None:
            continue
        if len(columns) <= required_max:
            raise ValueError(
                f"Zeile {physical_line}: nur {len(columns)} Spalten vorhanden, "
                f"benötigt wird mindestens Spalte {required_max + 1}"
            )
        try:
            name = columns[settings.id_column].strip()
            x = _parse_number(columns[settings.x_column], settings.decimal_separator)
            y = _parse_number(columns[settings.y_column], settings.decimal_separator)
            z = _parse_number(columns[settings.z_column], settings.decimal_separator)
        except ValueError as exc:
            raise ValueError(f"Zeile {physical_line}: {exc}") from exc
        if not name:
            raise ValueError(f"Zeile {physical_line}: ID ist leer")

        marker_code = 1
        if settings.marker_column is not None:
            marker_text = columns[settings.marker_column].strip()
            if marker_text:
                try:
                    marker_code = int(marker_text)
                except ValueError as exc:
                    raise ValueError(
                        f"Zeile {physical_line}: Markierungscode ist keine Ganzzahl"
                    ) from exc
        if marker_code not in VALID_MARKER_CODES:
            raise ValueError(
                f"Zeile {physical_line}: unbekannter Markierungscode {marker_code}"
            )
        remark = (
            columns[settings.remark_column].strip()
            if settings.remark_column is not None
            else ""
        )
        points.append(
            StakeoutPoint(
                name=name,
                target=Point3D(x, y, z),
                marker_code=marker_code,
                remark=remark,
            )
        )
    if not points:
        raise ValueError(f"Keine Punkte in Datei gefunden: {source}")
    return points


def split_line(raw_line: str, delimiter: str) -> list[str] | None:
    text = _strip_inline_comment(raw_line).strip()
    if not text or text.startswith("#"):
        return None
    if delimiter == "whitespace":
        try:
            return shlex.split(text, comments=False, posix=True)
        except ValueError as exc:
            raise ValueError(f"Ungültige Anführungszeichen: {exc}") from exc
    return next(
        csv.reader(
            [text],
            delimiter=delimiter,
            quotechar='"',
            skipinitialspace=True,
        )
    )


def _parse_number(text: str, decimal_separator: str) -> float:
    normalized = text.strip()
    if decimal_separator == ",":
        normalized = normalized.replace(".", "").replace(",", ".")
    try:
        return float(normalized)
    except ValueError as exc:
        raise ValueError(f"'{text}' ist keine gültige Zahl") from exc


def _strip_inline_comment(text: str) -> str:
    in_quotes = False
    index = 0
    while index < len(text) - 1:
        if text[index] == '"':
            in_quotes = not in_quotes
        if not in_quotes and text[index:index + 2] == "//":
            return text[:index]
        index += 1
    return text
