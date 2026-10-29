from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from mower.application import MowerSystem
from mower.domain import Point3D, StakeoutPoint, WagonGeometry, WagonPose
from mower.domain.point_file import load_points
from mower.hardware.simulation import SimGyro, SimRotationMotor, SimTracker, SimXYZRobot
from mower.ui.project_view import ProjectView
from mower.ui.xyz_top_view import Viewport, robot_to_screen, workspace_screen_bounds


class MowerApp(tk.Tk):
    BG = "#f2f2f2"
    PANEL = "#ffffff"
    BORDER = "#b9b9b9"
    GREEN = "#238636"
    RED = "#b42318"
    BLUE = "#1976d2"

    def __init__(self) -> None:
        super().__init__()
        self.title("Mower II v2 – SIMULATION")
        self.minsize(1120, 700)
        self._set_initial_geometry()
        self.configure(background=self.BG)

        self.system = MowerSystem(
            SimXYZRobot(), SimTracker(), SimGyro(), SimRotationMotor()
        )
        self.points: list[StakeoutPoint] = []
        self.target_position: Point3D | None = None
        self.tracker_station = Point3D(0.0, 0.0, 0.0)
        self.robot_project_position: Point3D | None = None
        self.wagon_geometry = WagonGeometry()
        self.wagon_pose: WagonPose | None = None
        self.project_view = ProjectView()
        self.project_view_fitted = False
        self.project_view_user_adjusted = False
        self.status_var = tk.StringVar(value="Simulation bereit – System noch nicht initialisiert")
        self.mode_var = tk.StringVar(value="SIMULATION")
        self.workflow_var = tk.StringVar(value="offline")
        self.xyz_var = tk.StringVar(value="X 0.0   Y 0.0   Z 0.0 mm")
        self.tracker_var = tk.StringVar(value="X 0.0   Y 0.0 mm")
        self.robot_var = tk.StringVar(value="noch unbekannt")

        self._configure_style()
        self._build_menu()
        self._build_layout()
        self._bind_hotkeys()
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.after(100, self._refresh)

    def _set_initial_geometry(self) -> None:
        """Öffnet das Fenster reproduzierbar und vollständig auf dem Bildschirm."""
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        width = min(1500, max(1120, screen_width - 80))
        height = min(880, max(700, screen_height - 120))
        x = max(0, (screen_width - width) // 2)
        y = max(0, (screen_height - height) // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _configure_style(self) -> None:
        style = ttk.Style(self)
        if "vista" in style.theme_names():
            style.theme_use("vista")
        style.configure("Title.TLabel", font=("Segoe UI", 11, "bold"))
        style.configure("Status.TLabel", font=("Segoe UI", 9))
        style.configure("Treeview", rowheight=23, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))

    def _build_menu(self) -> None:
        menu = tk.Menu(self)
        file_menu = tk.Menu(menu, tearoff=False)
        file_menu.add_command(label="Punktdatei öffnen…", command=self.open_points)
        file_menu.add_separator()
        file_menu.add_command(label="Beenden", command=self.destroy)
        menu.add_cascade(label="Datei", menu=file_menu)

        system_menu = tk.Menu(menu, tearoff=False)
        system_menu.add_command(label="Initialisieren\tStrg+I", command=self.initialize)
        menu.add_cascade(label="System", menu=system_menu)

        workflow_menu = tk.Menu(menu, tearoff=False)
        workflow_menu.add_command(label="Transformation\tStrg+T", command=self.transform)
        workflow_menu.add_command(label="Offset kalibrieren\tStrg+K", command=self.calibrate_offset)
        workflow_menu.add_command(label="Markierhöhe kalibrieren\tStrg+H", command=self.calibrate_height)
        workflow_menu.add_separator()
        workflow_menu.add_command(label="Absteckung\tStrg+A", command=self.stakeout_selected)
        menu.add_cascade(label="Arbeitsablauf", menu=workflow_menu)

        simulation_menu = tk.Menu(menu, tearoff=False)
        simulation_menu.add_command(
            label="Wagen auf gewählten Punkt setzen",
            command=self.place_wagon_at_selected,
        )
        simulation_menu.add_separator()
        simulation_menu.add_command(label="XYZ zur Mitte", command=self.move_center)
        simulation_menu.add_command(label="XYZ-Not-Halt testen", command=self.emergency_stop)
        menu.add_cascade(label="Simulation", menu=simulation_menu)
        self.config(menu=menu)

    def _build_layout(self) -> None:
        header = tk.Frame(self, bg="#e5e5e5", bd=1, relief="solid")
        header.pack(fill="x", padx=8, pady=(8, 4))
        tk.Label(
            header, text="Mower II v2", bg="#e5e5e5",
            font=("Segoe UI", 13, "bold"), padx=10, pady=8
        ).pack(side="left")
        tk.Label(
            header, textvariable=self.mode_var, bg="#f5a623", fg="#111111",
            font=("Segoe UI", 10, "bold"), padx=12, pady=4
        ).pack(side="right", padx=8)

        toolbar = tk.Frame(self, bg=self.BG)
        toolbar.pack(fill="x", padx=8, pady=4)
        buttons = [
            ("Initialisieren", self.initialize),
            ("Transformation", self.transform),
            ("Offset", self.calibrate_offset),
            ("Markierhöhe", self.calibrate_height),
            ("Abstecken", self.stakeout_selected),
        ]
        for text, command in buttons:
            ttk.Button(toolbar, text=text, command=command).pack(side="left", padx=(0, 6))

        self.body = tk.PanedWindow(self, orient="horizontal", sashwidth=5, bg=self.BG)
        self.body.pack(fill="both", expand=True, padx=8, pady=4)

        left = tk.LabelFrame(self.body, text="Absteckpunkte", bg=self.PANEL, padx=5, pady=5)
        center = tk.LabelFrame(self.body, text="Projektansicht", bg=self.PANEL, padx=5, pady=5)
        right = tk.Frame(self.body, bg=self.BG)
        self.body.add(left, minsize=220)
        self.body.add(center, minsize=450)
        self.body.add(right, minsize=220)
        self.after_idle(self._set_initial_pane_widths)

        columns = ("x", "y", "z", "status")
        self.point_tree = ttk.Treeview(left, columns=columns, show="tree headings")
        self.point_tree.heading("#0", text="Punkt")
        self.point_tree.heading("x", text="X")
        self.point_tree.heading("y", text="Y")
        self.point_tree.heading("z", text="Z")
        self.point_tree.heading("status", text="Status")
        self.point_tree.column("#0", width=70)
        for column in ("x", "y", "z"):
            self.point_tree.column(column, width=75, anchor="e")
        self.point_tree.column("status", width=85)
        self.point_tree.pack(fill="both", expand=True)
        self.point_tree.bind("<<TreeviewSelect>>", self._select_point)

        project_toolbar = tk.Frame(center, bg=self.PANEL)
        project_toolbar.pack(fill="x", pady=(0, 4))
        tk.Label(
            project_toolbar,
            text="Projektkoordinaten",
            bg=self.PANEL,
            fg="#555555",
        ).pack(side="left", padx=4)
        ttk.Button(
            project_toolbar, text="Alles", width=7, command=self.fit_project_view
        ).pack(side="right", padx=(3, 0))
        ttk.Button(
            project_toolbar, text="−", width=3, command=lambda: self.zoom_project(1.0 / 1.25)
        ).pack(side="right", padx=(3, 0))
        ttk.Button(
            project_toolbar, text="+", width=3, command=lambda: self.zoom_project(1.25)
        ).pack(side="right")

        self.project_canvas = tk.Canvas(center, bg="#eeeeee", highlightthickness=0)
        self.project_canvas.pack(fill="both", expand=True)
        self.project_canvas.bind("<Configure>", self._on_project_configure)
        self.project_canvas.bind("<MouseWheel>", self._on_project_mousewheel)
        self.project_canvas.bind("<Button-4>", self._on_project_mousewheel)
        self.project_canvas.bind("<Button-5>", self._on_project_mousewheel)

        status_box = tk.LabelFrame(right, text="Systemstatus", bg=self.PANEL, padx=10, pady=8)
        status_box.pack(fill="x", pady=(0, 8))
        self._status_row(status_box, "Modus", self.mode_var)
        self._status_row(status_box, "Ablauf", self.workflow_var)
        self._status_row(status_box, "XYZ", self.xyz_var)
        self._status_row(status_box, "Tracker", self.tracker_var)
        self._status_row(status_box, "Wagen", self.robot_var)

        robot_box = tk.LabelFrame(
            right, text="XYZ-Roboter – Draufsicht", bg=self.PANEL, padx=5, pady=5
        )
        robot_box.pack(fill="both", expand=True)
        self.xyz_canvas = tk.Canvas(
            robot_box, bg="#fafafa", highlightthickness=1, highlightbackground=self.BORDER
        )
        self.xyz_canvas.pack(fill="both", expand=True)
        self.xyz_canvas.bind("<Configure>", lambda _event: self._draw_xyz())

        footer = tk.Label(
            self, textvariable=self.status_var, anchor="w", bg="#e5e5e5",
            relief="sunken", bd=1, padx=8, pady=5, font=("Segoe UI", 9)
        )
        footer.pack(fill="x", padx=8, pady=(4, 8))

    def _set_initial_pane_widths(self) -> None:
        """Setzt die Hauptbereiche nach dem ersten Tk-Layout auf etwa 1:3:1."""
        self.update_idletasks()
        width = self.body.winfo_width()
        if width <= 1:
            self.after(50, self._set_initial_pane_widths)
            return
        self.body.sash_place(0, round(width * 0.20), 1)
        self.body.sash_place(1, round(width * 0.80), 1)

    def _status_row(self, parent: tk.Widget, label: str, variable: tk.StringVar) -> None:
        row = tk.Frame(parent, bg=self.PANEL)
        row.pack(fill="x", pady=2)
        tk.Label(row, text=f"{label}:", width=10, anchor="w", bg=self.PANEL).pack(side="left")
        tk.Label(row, textvariable=variable, anchor="w", bg=self.PANEL).pack(
            side="left", fill="x", expand=True
        )

    def _bind_hotkeys(self) -> None:
        bindings = {
            "i": self.initialize,
            "t": self.transform,
            "k": self.calibrate_offset,
            "h": self.calibrate_height,
            "a": self.stakeout_selected,
        }
        for key, command in bindings.items():
            self.bind_all(f"<Control-{key}>", lambda _event, cmd=command: self._hotkey(cmd))
            self.bind_all(f"<Control-{key.upper()}>", lambda _event, cmd=command: self._hotkey(cmd))

    def _hotkey(self, command: object) -> str:
        command()  # type: ignore[operator]
        return "break"

    def open_points(self) -> None:
        path = filedialog.askopenfilename(
            parent=self, title="Punktdatei öffnen",
            filetypes=[("Punktdateien", "*.txt"), ("Alle Dateien", "*.*")],
        )
        if not path:
            return
        try:
            self.points = load_points(Path(path))
        except Exception as exc:
            messagebox.showerror("Punktimport", str(exc), parent=self)
            return
        self._populate_points()
        if self.points:
            self._place_wagon_center(self.points[0].target)
            self._update_reachability()
        self.project_view_fitted = False
        self.project_view_user_adjusted = False
        self.fit_project_view()
        self.status_var.set(f"{len(self.points)} Punkte geladen: {Path(path).name}")

    def initialize(self) -> None:
        self._run("System initialisiert und XYZ referenziert", self.system.initialize)

    def transform(self) -> None:
        self._run("Simulationstransformation gültig", self.system.perform_transformation)

    def calibrate_offset(self) -> None:
        self._run("Simulierter Marker-/Reflektoroffset kalibriert", self.system.calibrate_offset)

    def calibrate_height(self) -> None:
        self._run("Simulierte Markierhöhe kalibriert", self.system.calibrate_marker_height)

    def stakeout_selected(self) -> None:
        selected = self.point_tree.selection()
        if not selected:
            messagebox.showinfo("Absteckung", "Bitte zuerst einen Punkt auswählen.", parent=self)
            return
        if self.system.workflow_state.value != "ready":
            messagebox.showwarning(
                "Absteckung", "Initialisierung und alle Kalibrierungen müssen abgeschlossen sein.",
                parent=self,
            )
            return
        index = int(selected[0])
        point = self.points[index]
        robot_target = self._project_to_robot(point)
        if not point.reachable:
            messagebox.showwarning(
                "Absteckung",
                f"Punkt {point.name} liegt außerhalb des XYZ-Arbeitsraums.",
                parent=self,
            )
            return

        def action() -> None:
            self.target_position = robot_target
            self.system.move_robot(robot_target)
            point.marking_state = point.marking_state.COMPLETE

        self._run(f"Punkt {point.name} simuliert abgesteckt", action)
        self._populate_points(select=index)
        self._draw_project()

    def move_center(self) -> None:
        self.target_position = Point3D(250.0, 200.0, 170.0)
        self._run("XYZ zur Arbeitsraummitte bewegt", lambda: self.system.move_robot(self.target_position))

    def place_wagon_at_selected(self) -> None:
        selected = self.point_tree.selection()
        if not selected:
            messagebox.showinfo(
                "Simulation",
                "Bitte zuerst einen Punkt auswählen.",
                parent=self,
            )
            return
        point = self.points[int(selected[0])]
        self._place_wagon_center(point.target)
        self._update_reachability()
        self._populate_points(select=int(selected[0]))
        self._draw_project()
        self.status_var.set(f"Simulierter Wagen auf Punkt {point.name} positioniert")

    def emergency_stop(self) -> None:
        self.system.xyz.emergency_stop()
        self.status_var.set("SIMULATION: XYZ-Not-Halt ausgelöst")
        self._draw_xyz()

    def _run(self, success: str, action: object) -> None:
        try:
            action()  # type: ignore[operator]
        except Exception as exc:
            self.status_var.set(f"Fehler: {exc}")
            messagebox.showerror("Mower II v2", str(exc), parent=self)
        else:
            self.status_var.set(success)
        self._refresh()

    def _project_to_robot(self, point: StakeoutPoint) -> Point3D:
        if self.wagon_pose is None:
            raise RuntimeError("Wagenpose ist noch nicht bekannt")
        return self.wagon_pose.project_to_local(
            point.target,
            local_z=self.wagon_geometry.marking_z_mm,
        )

    def _place_wagon_center(self, center_project: Point3D) -> None:
        yaw_deg = self.system.gyro.angle_deg
        center = self.wagon_geometry.center_local
        center_offset = WagonPose(Point3D(0.0, 0.0, 0.0), yaw_deg).local_to_project(center)
        origin = Point3D(
            center_project.x - center_offset.x,
            center_project.y - center_offset.y,
            0.0,
        )
        self.wagon_pose = WagonPose(origin, yaw_deg)
        self.robot_project_position = Point3D(center_project.x, center_project.y, center_project.z)

    def _update_reachability(self) -> None:
        for point in self.points:
            if self.wagon_pose is None:
                point.reachable = False
                continue
            local = self.wagon_pose.project_to_local(
                point.target,
                local_z=self.wagon_geometry.marking_z_mm,
            )
            point.reachable = self.wagon_geometry.workspace.contains(local)

    def _populate_points(self, select: int | None = None) -> None:
        self.point_tree.delete(*self.point_tree.get_children())
        for index, point in enumerate(self.points):
            self.point_tree.insert(
                "", "end", iid=str(index), text=point.name,
                values=(
                    f"{point.target.x:.3f}", f"{point.target.y:.3f}",
                    f"{point.target.z:.3f}", self._point_status(point),
                ),
            )
        if select is not None and str(select) in self.point_tree.get_children():
            self.point_tree.selection_set(str(select))

    def _select_point(self, _event: tk.Event[tk.Misc]) -> None:
        selected = self.point_tree.selection()
        if selected:
            self.target_position = self._project_to_robot(self.points[int(selected[0])])
        self._draw_xyz()
        self._draw_project()

    @staticmethod
    def _point_status(point: StakeoutPoint) -> str:
        if point.marking_state.value == "complete":
            return "markiert"
        return "erreichbar" if point.reachable else "außer Reichw."

    def _refresh(self) -> None:
        position = self.system.xyz.position
        self.workflow_var.set(self.system.workflow_state.value)
        self.xyz_var.set(f"X {position.x:.1f}   Y {position.y:.1f}   Z {position.z:.1f} mm")
        self.tracker_var.set(
            f"X {self.tracker_station.x:.1f}   Y {self.tracker_station.y:.1f} mm"
        )
        if self.robot_project_position is None:
            self.robot_var.set("noch unbekannt")
        else:
            self.robot_var.set(
                f"X {self.robot_project_position.x:.1f}   "
                f"Y {self.robot_project_position.y:.1f} mm"
            )
        self._draw_xyz()

    def _draw_xyz(self) -> None:
        canvas = self.xyz_canvas
        canvas.delete("all")
        width = max(canvas.winfo_width(), 100)
        height = max(canvas.winfo_height(), 100)
        viewport = Viewport(width, height, 34.0)
        xyz = self.system.xyz
        minimum, maximum = xyz.workspace_min, xyz.workspace_max

        left, top, right, bottom = workspace_screen_bounds(minimum, maximum, viewport)
        canvas.create_rectangle(left, top, right, bottom, fill="#eef7fa", outline="#44879a", width=2)

        origin = robot_to_screen(Point3D(0.0, 0.0, 0.0), minimum, maximum, viewport)
        canvas.create_line(origin[0], top, origin[0], bottom, fill="#c0c0c0", dash=(3, 3))
        canvas.create_line(left, origin[1], right, origin[1], fill="#c0c0c0", dash=(3, 3))

        canvas.create_line(right - 18, bottom - 12, right - 18, top + 16, arrow="last", width=2)
        canvas.create_text(right - 14, top + 10, text="X+", anchor="sw", font=("Segoe UI", 9, "bold"))
        canvas.create_line(right - 12, bottom - 18, left + 16, bottom - 18, arrow="last", width=2)
        canvas.create_text(left + 8, bottom - 23, text="Y+", anchor="sw", font=("Segoe UI", 9, "bold"))

        if self.target_position is not None:
            tx, ty = robot_to_screen(self.target_position, minimum, maximum, viewport)
            canvas.create_oval(tx - 8, ty - 8, tx + 8, ty + 8, outline="#e28b00", width=2)
            canvas.create_line(tx - 11, ty, tx + 11, ty, fill="#e28b00")
            canvas.create_line(tx, ty - 11, tx, ty + 11, fill="#e28b00")
            canvas.create_text(tx + 10, ty - 9, text="Ziel", anchor="sw", fill="#8a5300")

        px, py = robot_to_screen(xyz.position, minimum, maximum, viewport)
        fill = self.RED if xyz.stopped else self.GREEN
        canvas.create_oval(px - 9, py - 9, px + 9, py + 9, fill=fill, outline="white", width=2)
        canvas.create_text(px + 11, py + 9, text="XYZ", anchor="nw", fill=fill, font=("Segoe UI", 9, "bold"))
        canvas.create_text(
            width / 2, height - 8,
            text="Draufsicht · X+ oben · Y+ links", anchor="s", fill="#555555"
        )

    def _draw_project(self) -> None:
        canvas = self.project_canvas
        canvas.delete("all")
        width = max(canvas.winfo_width(), 100)
        height = max(canvas.winfo_height(), 100)
        if not self.points:
            canvas.create_text(
                width / 2, height / 2,
                text="Noch keine Punktdatei geladen\nDatei → Punktdatei öffnen…",
                justify="center", fill="#666666", font=("Segoe UI", 11)
            )
            return
        if not self.project_view_fitted:
            self._fit_project_view(width, height)

        self._draw_project_grid(canvas, width, height)
        self._draw_wagon_and_workspace(canvas, width, height)
        selected = self.point_tree.selection()
        selected_index = int(selected[0]) if selected else None
        for index, point in enumerate(self.points):
            x, y = self.project_view.world_to_screen(point.target, width, height)
            if point.marking_state.value == "complete":
                color = "#8a8a8a"
            elif point.reachable:
                color = self.GREEN
            else:
                color = self.BLUE
            radius = 7 if index == selected_index else 5
            canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=color, outline="white")
            canvas.create_text(x + 8, y - 7, text=point.name, anchor="sw", fill="#222222")

        tracker_x, tracker_y = self.project_view.world_to_screen(
            self.tracker_station, width, height
        )
        canvas.create_oval(
            tracker_x - 9,
            tracker_y - 9,
            tracker_x + 9,
            tracker_y + 9,
            outline="#f57c00",
            width=2,
        )
        canvas.create_line(
            tracker_x - 13, tracker_y, tracker_x + 13, tracker_y, fill="#f57c00", width=2
        )
        canvas.create_line(
            tracker_x, tracker_y - 13, tracker_x, tracker_y + 13, fill="#f57c00", width=2
        )
        canvas.create_text(
            tracker_x + 11,
            tracker_y - 11,
            text="Lasertracker",
            anchor="sw",
            fill="#c45d00",
            font=("Segoe UI", 9, "bold"),
        )

        if self.robot_project_position is not None:
            robot_x, robot_y = self.project_view.world_to_screen(
                self.robot_project_position, width, height
            )
            canvas.create_polygon(
                robot_x,
                robot_y - 11,
                robot_x + 10,
                robot_y + 9,
                robot_x - 10,
                robot_y + 9,
                fill=self.GREEN,
                outline="white",
                width=2,
            )
            canvas.create_text(
                robot_x + 12,
                robot_y + 7,
                text="Wagen (sim.)",
                anchor="nw",
                fill="#176b2a",
                font=("Segoe UI", 9, "bold"),
            )

    def _draw_wagon_and_workspace(
        self,
        canvas: tk.Canvas,
        width: float,
        height: float,
    ) -> None:
        if self.wagon_pose is None:
            return
        geometry = self.wagon_geometry
        footprint_local = [
            Point3D(geometry.footprint_min_x, geometry.footprint_min_y, 0.0),
            Point3D(geometry.footprint_max_x, geometry.footprint_min_y, 0.0),
            Point3D(geometry.footprint_max_x, geometry.footprint_max_y, 0.0),
            Point3D(geometry.footprint_min_x, geometry.footprint_max_y, 0.0),
        ]
        workspace = geometry.workspace
        workspace_local = [
            Point3D(workspace.minimum.x, workspace.minimum.y, 0.0),
            Point3D(workspace.maximum.x, workspace.minimum.y, 0.0),
            Point3D(workspace.maximum.x, workspace.maximum.y, 0.0),
            Point3D(workspace.minimum.x, workspace.maximum.y, 0.0),
        ]
        footprint_screen: list[float] = []
        for point in self.wagon_pose.polygon_to_project(footprint_local):
            footprint_screen.extend(self.project_view.world_to_screen(point, width, height))
        workspace_screen: list[float] = []
        for point in self.wagon_pose.polygon_to_project(workspace_local):
            workspace_screen.extend(self.project_view.world_to_screen(point, width, height))
        canvas.create_polygon(
            *footprint_screen,
            fill="#e8e8e8",
            outline="#555555",
            width=2,
            stipple="gray25",
        )
        canvas.create_polygon(
            *workspace_screen,
            fill="",
            outline="#0086a8",
            width=2,
            dash=(5, 3),
        )

    def _project_positions(self) -> list[Point3D]:
        positions = [point.target for point in self.points]
        positions.append(self.tracker_station)
        if self.robot_project_position is not None:
            positions.append(self.robot_project_position)
        return positions

    def _fit_project_view(self, width: float, height: float) -> None:
        self.project_view.fit(self._project_positions(), width, height)
        self.project_view_fitted = True

    def fit_project_view(self) -> None:
        width = max(self.project_canvas.winfo_width(), 100)
        height = max(self.project_canvas.winfo_height(), 100)
        self._fit_project_view(width, height)
        self.project_view_user_adjusted = False
        self._draw_project()

    def zoom_project(
        self,
        factor: float,
        screen_x: float | None = None,
        screen_y: float | None = None,
    ) -> None:
        if not self.points:
            return
        width = max(self.project_canvas.winfo_width(), 100)
        height = max(self.project_canvas.winfo_height(), 100)
        self.project_view.zoom_at(
            factor,
            width / 2.0 if screen_x is None else screen_x,
            height / 2.0 if screen_y is None else screen_y,
            width,
            height,
        )
        self.project_view_fitted = True
        self.project_view_user_adjusted = True
        self._draw_project()

    def _on_project_configure(self, _event: tk.Event[tk.Misc]) -> None:
        if self.points and not self.project_view_user_adjusted:
            width = max(self.project_canvas.winfo_width(), 100)
            height = max(self.project_canvas.winfo_height(), 100)
            self._fit_project_view(width, height)
        self._draw_project()

    def _on_project_mousewheel(self, event: tk.Event[tk.Misc]) -> str:
        if getattr(event, "num", None) == 4:
            factor = 1.25
        elif getattr(event, "num", None) == 5:
            factor = 1.0 / 1.25
        else:
            factor = 1.25 if getattr(event, "delta", 0) > 0 else 1.0 / 1.25
        self.zoom_project(factor, float(event.x), float(event.y))
        return "break"

    def _draw_project_grid(self, canvas: tk.Canvas, width: float, height: float) -> None:
        origin_x, origin_y = self.project_view.world_to_screen(
            Point3D(0.0, 0.0, 0.0), width, height
        )
        if 0.0 <= origin_x <= width:
            canvas.create_line(origin_x, 0, origin_x, height, fill="#d0d0d0", dash=(3, 3))
        if 0.0 <= origin_y <= height:
            canvas.create_line(0, origin_y, width, origin_y, fill="#d0d0d0", dash=(3, 3))
        canvas.create_text(
            10,
            height - 10,
            text=f"Maßstab: {self.project_view.scale:.4f} px/mm",
            anchor="sw",
            fill="#666666",
        )


def main() -> None:
    app = MowerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
