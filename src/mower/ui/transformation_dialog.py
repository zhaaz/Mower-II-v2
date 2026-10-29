from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

from mower.application.transformation import (
    TransformationMeasurement,
    TransformationResult,
)


class TransformationDialog(tk.Toplevel):
    def __init__(
        self,
        parent: tk.Misc,
        measurements: list[TransformationMeasurement],
        result: TransformationResult,
        accepted: bool,
        quality_text: str,
        on_accept: Callable[[], None],
    ) -> None:
        super().__init__(parent)
        self.title("Transformation – Simulation")
        self.geometry("900x480")
        self.transient(parent)
        self.grab_set()

        header = tk.Frame(self, bg="#f2f2f2", padx=12, pady=10)
        header.pack(fill="x")
        tk.Label(
            header,
            text=f"Qualität: {quality_text}",
            bg="#f2f2f2",
            fg="#1f7a38" if accepted else "#b42318",
            font=("Segoe UI", 12, "bold"),
        ).pack(side="left")
        tk.Label(
            header,
            text=(
                f"RMS {result.rms_mm:.3f} mm · "
                f"Max {result.max_residual_mm:.3f} mm · "
                f"Drehung {result.pose.yaw_deg:.4f}°"
            ),
            bg="#f2f2f2",
            font=("Segoe UI", 10),
        ).pack(side="right")

        columns = ("lx", "ly", "lz", "px", "py", "pz", "residual")
        tree = ttk.Treeview(self, columns=columns, show="headings")
        headings = {
            "lx": "Lokal X",
            "ly": "Lokal Y",
            "lz": "Lokal Z",
            "px": "Projekt X",
            "py": "Projekt Y",
            "pz": "Projekt Z",
            "residual": "Restabw.",
        }
        for column, label in headings.items():
            tree.heading(column, text=label)
            tree.column(column, width=110, anchor="e")
        tree.pack(fill="both", expand=True, padx=12, pady=8)
        for index, (measurement, residual) in enumerate(
            zip(measurements, result.residuals_mm),
            1,
        ):
            tree.insert(
                "",
                "end",
                values=(
                    f"{measurement.local.x:.3f}",
                    f"{measurement.local.y:.3f}",
                    f"{measurement.local.z:.3f}",
                    f"{measurement.measured_project.x:.3f}",
                    f"{measurement.measured_project.y:.3f}",
                    f"{measurement.measured_project.z:.3f}",
                    f"{residual:.3f} mm",
                ),
            )

        buttons = tk.Frame(self, padx=12, pady=10)
        buttons.pack(fill="x")
        ttk.Button(buttons, text="Abbrechen", command=self.destroy).pack(side="right")

        def accept_and_close() -> None:
            on_accept()
            self.destroy()

        accept_button = ttk.Button(
            buttons,
            text="Transformation übernehmen",
            command=accept_and_close,
        )
        accept_button.pack(side="right", padx=(0, 8))
        if not accepted:
            accept_button.state(["disabled"])
