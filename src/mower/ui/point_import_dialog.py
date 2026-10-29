from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from mower.domain import StakeoutPoint
from mower.domain.flexible_point_file import (
    PointImportSettings,
    load_points_with_settings,
    preview_rows,
)


SEPARATOR_LABELS = {
    "Leerraum": "whitespace",
    "Semikolon (;)": ";",
    "Komma (, )": ",",
    "Tabulator": "\t",
    "Eigenes Zeichen": "custom",
}
NONE_COLUMN = "Nicht verwenden"


class PointImportDialog(tk.Toplevel):
    def __init__(self, parent: tk.Misc, path: str | Path) -> None:
        super().__init__(parent)
        self.path = Path(path)
        self.result: list[StakeoutPoint] | None = None
        self.title(f"Punktimport – {self.path.name}")
        self.geometry("1100x700")
        self.minsize(900, 580)
        self.transient(parent)
        self.grab_set()

        self.separator_var = tk.StringVar(value="Leerraum")
        self.custom_separator_var = tk.StringVar(value="|")
        self.skip_rows_var = tk.IntVar(value=0)
        self.decimal_var = tk.StringVar(value=".")
        self.mapping_vars = {
            "ID": tk.StringVar(value="Spalte 1"),
            "X": tk.StringVar(value="Spalte 2"),
            "Y": tk.StringVar(value="Spalte 3"),
            "Z": tk.StringVar(value="Spalte 4"),
            "Markierung": tk.StringVar(value="Spalte 5"),
            "Bemerkung": tk.StringVar(value="Spalte 6"),
        }
        self.mapping_boxes: dict[str, ttk.Combobox] = {}

        self._build()
        self._refresh_preview()
        self.wait_window(self)

    def _build(self) -> None:
        settings = ttk.LabelFrame(self, text="Dateiaufbau", padding=10)
        settings.pack(fill="x", padx=12, pady=(12, 6))
        ttk.Label(settings, text="Trennzeichen").grid(row=0, column=0, sticky="w")
        separator = ttk.Combobox(
            settings,
            textvariable=self.separator_var,
            values=list(SEPARATOR_LABELS),
            state="readonly",
            width=18,
        )
        separator.grid(row=1, column=0, sticky="ew", padx=(0, 10))
        separator.bind("<<ComboboxSelected>>", lambda _event: self._refresh_preview())

        ttk.Label(settings, text="Eigenes Zeichen").grid(row=0, column=1, sticky="w")
        custom_entry = ttk.Entry(
            settings,
            textvariable=self.custom_separator_var,
            width=8,
        )
        custom_entry.grid(row=1, column=1, sticky="w", padx=(0, 10))
        custom_entry.bind("<KeyRelease>", lambda _event: self._refresh_preview())

        ttk.Label(settings, text="Anfangszeilen überspringen").grid(
            row=0, column=2, sticky="w"
        )
        skip = ttk.Spinbox(
            settings,
            from_=0,
            to=10000,
            textvariable=self.skip_rows_var,
            width=9,
            command=self._refresh_preview,
        )
        skip.grid(row=1, column=2, sticky="w", padx=(0, 10))
        skip.bind("<KeyRelease>", lambda _event: self._refresh_preview())

        ttk.Label(settings, text="Dezimalzeichen").grid(row=0, column=3, sticky="w")
        decimal = ttk.Combobox(
            settings,
            textvariable=self.decimal_var,
            values=[".", ","],
            state="readonly",
            width=6,
        )
        decimal.grid(row=1, column=3, sticky="w")

        mapping = ttk.LabelFrame(self, text="Spaltenzuordnung", padding=10)
        mapping.pack(fill="x", padx=12, pady=6)
        for column_index, (field, variable) in enumerate(self.mapping_vars.items()):
            ttk.Label(
                mapping,
                text=field + (" *" if field in {"ID", "X", "Y", "Z"} else ""),
            ).grid(row=0, column=column_index, sticky="w", padx=(0, 8))
            box = ttk.Combobox(mapping, textvariable=variable, state="readonly", width=16)
            box.grid(row=1, column=column_index, sticky="ew", padx=(0, 8))
            self.mapping_boxes[field] = box
            mapping.columnconfigure(column_index, weight=1)

        preview_frame = ttk.LabelFrame(self, text="Vorschau", padding=8)
        preview_frame.pack(fill="both", expand=True, padx=12, pady=6)
        self.preview_tree = ttk.Treeview(preview_frame, show="headings")
        vertical = ttk.Scrollbar(
            preview_frame, orient="vertical", command=self.preview_tree.yview
        )
        horizontal = ttk.Scrollbar(
            preview_frame, orient="horizontal", command=self.preview_tree.xview
        )
        self.preview_tree.configure(
            yscrollcommand=vertical.set,
            xscrollcommand=horizontal.set,
        )
        self.preview_tree.grid(row=0, column=0, sticky="nsew")
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")
        preview_frame.rowconfigure(0, weight=1)
        preview_frame.columnconfigure(0, weight=1)

        footer = ttk.Frame(self, padding=(12, 6, 12, 12))
        footer.pack(fill="x")
        ttk.Label(footer, text="* Pflichtfeld").pack(side="left")
        ttk.Button(footer, text="Abbrechen", command=self.destroy).pack(side="right")
        ttk.Button(footer, text="Importieren", command=self._import).pack(
            side="right", padx=(0, 8)
        )

    def _delimiter(self) -> str:
        selected = SEPARATOR_LABELS[self.separator_var.get()]
        if selected == "custom":
            return self.custom_separator_var.get()
        return selected

    def _refresh_preview(self) -> None:
        try:
            skip_rows = max(0, int(self.skip_rows_var.get()))
            delimiter = self._delimiter()
            if delimiter != "whitespace" and len(delimiter) != 1:
                return
            rows = preview_rows(self.path, delimiter, skip_rows)
        except (ValueError, tk.TclError):
            return
        column_count = max((len(row.columns) for row in rows), default=4)
        column_ids = tuple(f"c{index}" for index in range(column_count))
        self.preview_tree.delete(*self.preview_tree.get_children())
        self.preview_tree.configure(columns=column_ids)
        for index, column_id in enumerate(column_ids, 1):
            self.preview_tree.heading(column_id, text=f"Spalte {index}")
            self.preview_tree.column(column_id, width=140, minwidth=70, stretch=True)
        for row in rows:
            values = list(row.columns) + [""] * (column_count - len(row.columns))
            self.preview_tree.insert("", "end", values=values)

        options = [NONE_COLUMN] + [
            f"Spalte {index}" for index in range(1, column_count + 1)
        ]
        for field, box in self.mapping_boxes.items():
            box.configure(values=options)
            current = self.mapping_vars[field].get()
            if current not in options:
                self.mapping_vars[field].set(
                    NONE_COLUMN if field in {"Markierung", "Bemerkung"} else options[1]
                )

    def _column_index(self, field: str, required: bool) -> int | None:
        value = self.mapping_vars[field].get()
        if value == NONE_COLUMN:
            if required:
                raise ValueError(f"{field} ist ein Pflichtfeld")
            return None
        if not value.startswith("Spalte "):
            raise ValueError(f"Für {field} wurde keine Spalte gewählt")
        return int(value.removeprefix("Spalte ")) - 1

    def _settings(self) -> PointImportSettings:
        return PointImportSettings(
            delimiter=self._delimiter(),
            skip_rows=int(self.skip_rows_var.get()),
            decimal_separator=self.decimal_var.get(),
            id_column=self._column_index("ID", True),  # type: ignore[arg-type]
            x_column=self._column_index("X", True),  # type: ignore[arg-type]
            y_column=self._column_index("Y", True),  # type: ignore[arg-type]
            z_column=self._column_index("Z", True),  # type: ignore[arg-type]
            marker_column=self._column_index("Markierung", False),
            remark_column=self._column_index("Bemerkung", False),
        )

    def _import(self) -> None:
        try:
            settings = self._settings()
            self.result = load_points_with_settings(self.path, settings)
        except Exception as exc:
            messagebox.showerror("Punktimport", str(exc), parent=self)
            return
        self.destroy()


def show_point_import_dialog(
    parent: tk.Misc,
    path: str | Path,
) -> list[StakeoutPoint] | None:
    return PointImportDialog(parent, path).result
