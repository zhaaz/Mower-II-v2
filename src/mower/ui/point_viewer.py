from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from mower.domain import Point3D, StakeoutPoint


def show_point_viewer(
    parent: tk.Misc,
    point: StakeoutPoint,
    local: Point3D | None,
    transformation_valid: bool,
) -> None:
    window = tk.Toplevel(parent)
    window.title(f"Absteckpunkt {point.name}")
    window.geometry("520x420")
    window.transient(parent)

    frame = ttk.Frame(window, padding=14)
    frame.pack(fill="both", expand=True)
    point_status = (
        "Transformation fehlt"
        if not transformation_valid
        else ("erreichbar" if point.reachable else "außer Reichweite")
    )
    rows = [
        ("ID", point.name),
        ("Status", point_status),
        ("Markierungszustand", point.marking_state.value),
        ("Markierung", f"{point.marker_code} / {point.marker_shape}"),
        ("Bemerkung", point.remark or "–"),
        ("Projekt X", f"{point.target.x:.3f} mm"),
        ("Projekt Y", f"{point.target.y:.3f} mm"),
        ("Projekt Z", f"{point.target.z:.3f} mm"),
    ]
    if local is not None:
        rows.extend(
            [
                ("Roboter X", f"{local.x:.3f} mm"),
                ("Roboter Y", f"{local.y:.3f} mm"),
                ("Markierhöhe Z", f"{local.z:.3f} mm"),
            ]
        )
    for row_index, (label, value) in enumerate(rows):
        ttk.Label(frame, text=label, font=("Segoe UI", 9, "bold")).grid(
            row=row_index, column=0, sticky="nw", padx=(0, 18), pady=4
        )
        ttk.Label(frame, text=value, wraplength=300).grid(
            row=row_index, column=1, sticky="nw", pady=4
        )
    frame.columnconfigure(1, weight=1)
    ttk.Button(frame, text="Schließen", command=window.destroy).grid(
        row=len(rows), column=1, sticky="e", pady=(16, 0)
    )
