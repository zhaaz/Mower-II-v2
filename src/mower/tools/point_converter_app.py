from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from mower.domain import StakeoutPoint
from mower.domain.legacy_point_export import save_legacy_point_file
from mower.ui.point_import_dialog import show_point_import_dialog


class PointConverterApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Mower Point Converter")
        self.geometry("1050x680")
        self.minsize(820, 520)
        self.points: list[StakeoutPoint] = []
        self.source_path: Path | None = None
        self.status_var = tk.StringVar(
            value="Quelldatei auswählen und Dateiaufbau festlegen"
        )
        self.source_var = tk.StringVar(value="–")
        self.count_var = tk.StringVar(value="0 Punkte")
        self._configure_style()
        self._build()

    def _configure_style(self) -> None:
        style = ttk.Style(self)
        if "vista" in style.theme_names():
            style.theme_use("vista")
        style.configure("Treeview", rowheight=23, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))

    def _build(self) -> None:
        header = tk.Frame(self, bg="#e7e7e7", padx=14, pady=12)
        header.pack(fill="x")
        tk.Label(
            header,
            text="Mower Point Converter",
            bg="#e7e7e7",
            font=("Segoe UI", 15, "bold"),
        ).pack(side="left")
        tk.Label(
            header,
            text="Eigenständiges Hilfsprogramm",
            bg="#e7e7e7",
            fg="#555555",
            font=("Segoe UI", 9),
        ).pack(side="right")

        intro = ttk.Frame(self, padding=(14, 12))
        intro.pack(fill="x")
        ttk.Label(
            intro,
            text=(
                "Konvertiert frei aufgebaute TXT-/CSV-Dateien in das feste "
                "Punktformat des bisherigen Mower II."
            ),
        ).pack(anchor="w")

        actions = ttk.Frame(self, padding=(14, 0, 14, 10))
        actions.pack(fill="x")
        ttk.Button(
            actions,
            text="1. Quelldatei auswählen…",
            command=self.select_source,
        ).pack(side="left")
        self.save_button = ttk.Button(
            actions,
            text="2. Mower-Datei speichern…",
            command=self.save_result,
        )
        self.save_button.pack(side="left", padx=(8, 0))
        self.save_button.state(["disabled"])
        ttk.Label(actions, textvariable=self.count_var).pack(side="right")

        information = ttk.LabelFrame(self, text="Quelldatei", padding=8)
        information.pack(fill="x", padx=14, pady=(0, 8))
        ttk.Label(information, textvariable=self.source_var).pack(
            anchor="w", fill="x"
        )

        table_frame = ttk.LabelFrame(self, text="Konvertierungsvorschau", padding=8)
        table_frame.pack(fill="both", expand=True, padx=14, pady=(0, 8))
        columns = ("id", "x", "y", "z", "marker", "remark")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        headings = {
            "id": "ID",
            "x": "X [mm]",
            "y": "Y [mm]",
            "z": "Z [mm]",
            "marker": "Markierung",
            "remark": "Bemerkung",
        }
        for column, label in headings.items():
            self.tree.heading(column, text=label)
        self.tree.column("id", width=90, stretch=False)
        for column in ("x", "y", "z"):
            self.tree.column(column, width=125, anchor="e", stretch=False)
        self.tree.column("marker", width=120, anchor="center", stretch=False)
        self.tree.column("remark", width=260)
        vertical = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.tree.yview
        )
        horizontal = ttk.Scrollbar(
            table_frame, orient="horizontal", command=self.tree.xview
        )
        self.tree.configure(
            yscrollcommand=vertical.set,
            xscrollcommand=horizontal.set,
        )
        self.tree.grid(row=0, column=0, sticky="nsew")
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        tk.Label(
            self,
            textvariable=self.status_var,
            anchor="w",
            bg="#e7e7e7",
            relief="sunken",
            bd=1,
            padx=8,
            pady=5,
        ).pack(fill="x", padx=14, pady=(0, 14))

    def select_source(self) -> None:
        path = filedialog.askopenfilename(
            parent=self,
            title="Quelldatei auswählen",
            filetypes=[
                ("Text- und Tabellendateien", "*.txt *.csv *.xyz *.dat"),
                ("Alle Dateien", "*.*"),
            ],
        )
        if not path:
            return
        try:
            points = show_point_import_dialog(self, path)
        except Exception as exc:
            messagebox.showerror("Punktkonverter", str(exc), parent=self)
            return
        if points is None:
            return
        self.points = points
        self.source_path = Path(path)
        self.source_var.set(str(self.source_path))
        self.count_var.set(f"{len(self.points)} Punkte")
        self._populate_preview()
        self.save_button.state(["!disabled"])
        self.status_var.set(
            f"{len(self.points)} Punkte gelesen – bereit zum Speichern"
        )

    def _populate_preview(self) -> None:
        self.tree.delete(*self.tree.get_children())
        for point in self.points:
            self.tree.insert(
                "",
                "end",
                values=(
                    point.name,
                    f"{point.target.x:.6f}",
                    f"{point.target.y:.6f}",
                    f"{point.target.z:.6f}",
                    f"{point.marker_code} / {point.marker_shape}",
                    point.remark,
                ),
            )

    def save_result(self) -> None:
        if not self.points:
            return
        initial_name = (
            f"{self.source_path.stem}_mower.txt"
            if self.source_path is not None
            else "mower_punkte.txt"
        )
        path = filedialog.asksaveasfilename(
            parent=self,
            title="Mower-Punktdatei speichern",
            defaultextension=".txt",
            initialfile=initial_name,
            filetypes=[("Mower-Punktdatei", "*.txt"), ("Alle Dateien", "*.*")],
        )
        if not path:
            return
        try:
            save_legacy_point_file(path, self.points)
        except Exception as exc:
            messagebox.showerror("Punktkonverter", str(exc), parent=self)
            return
        self.status_var.set(f"Mower-Punktdatei gespeichert: {path}")
        messagebox.showinfo(
            "Punktkonverter",
            f"{len(self.points)} Punkte wurden erfolgreich konvertiert.",
            parent=self,
        )


def main() -> None:
    app = PointConverterApp()
    app.mainloop()


if __name__ == "__main__":
    main()
