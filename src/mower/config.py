from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from mower.domain import Point3D, RobotWorkspace, WagonGeometry


@dataclass(frozen=True, slots=True)
class SimulationConfig:
    random_seed: int
    tracker_noise_mm: float
    movement_time_scale: float
    true_yaw_deg: float


@dataclass(frozen=True, slots=True)
class TransformationConfig:
    calibration_points: tuple[Point3D, ...]
    good_rms_mm: float
    good_max_residual_mm: float
    accepted_rms_mm: float
    accepted_max_residual_mm: float


@dataclass(frozen=True, slots=True)
class AppConfig:
    mode: str
    workspace: RobotWorkspace
    wagon: WagonGeometry
    front_direction: str
    simulation: SimulationConfig
    transformation: TransformationConfig


def default_config_path() -> Path:
    candidates = [
        Path.cwd() / "config" / "mower_config.json",
        Path(__file__).resolve().parents[2] / "config" / "mower_config.json",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("config/mower_config.json wurde nicht gefunden")


def load_config(path: str | Path | None = None) -> AppConfig:
    source = Path(path) if path is not None else default_config_path()
    raw = json.loads(source.read_text(encoding="utf-8"))
    xyz = raw["xyz"]
    wagon_raw = raw["wagon"]
    simulation_raw = raw["simulation"]
    transformation_raw = raw["transformation"]

    workspace = RobotWorkspace(
        minimum=Point3D(*map(float, xyz["workspace_min_mm"])),
        maximum=Point3D(*map(float, xyz["workspace_max_mm"])),
    )
    footprint_min = wagon_raw["footprint_min_xy_mm"]
    footprint_max = wagon_raw["footprint_max_xy_mm"]
    wagon = WagonGeometry(
        footprint_min_x=float(footprint_min[0]),
        footprint_max_x=float(footprint_max[0]),
        footprint_min_y=float(footprint_min[1]),
        footprint_max_y=float(footprint_max[1]),
        workspace=workspace,
        marking_z_mm=float(raw["marker"]["z_mark_mm"]),
    )
    simulation = SimulationConfig(
        random_seed=int(simulation_raw["random_seed"]),
        tracker_noise_mm=float(simulation_raw["tracker_noise_mm"]),
        movement_time_scale=float(simulation_raw["movement_time_scale"]),
        true_yaw_deg=float(simulation_raw["true_yaw_deg"]),
    )
    transformation = TransformationConfig(
        calibration_points=tuple(
            Point3D(*map(float, values))
            for values in transformation_raw["calibration_points_mm"]
        ),
        good_rms_mm=float(transformation_raw["good_rms_mm"]),
        good_max_residual_mm=float(transformation_raw["good_max_residual_mm"]),
        accepted_rms_mm=float(transformation_raw["accepted_rms_mm"]),
        accepted_max_residual_mm=float(
            transformation_raw["accepted_max_residual_mm"]
        ),
    )
    front_direction = str(wagon_raw["front_direction"])
    _validate(workspace, wagon, front_direction, transformation)
    return AppConfig(
        raw["mode"],
        workspace,
        wagon,
        front_direction,
        simulation,
        transformation,
    )


def _validate(
    workspace: RobotWorkspace,
    wagon: WagonGeometry,
    front_direction: str,
    transformation: TransformationConfig,
) -> None:
    if not (
        workspace.maximum.x > workspace.minimum.x
        and workspace.maximum.y > workspace.minimum.y
        and workspace.maximum.z > workspace.minimum.z
    ):
        raise ValueError("Ungültige XYZ-Arbeitsraumgrenzen")
    if not (
        wagon.footprint_max_x > wagon.footprint_min_x
        and wagon.footprint_max_y > wagon.footprint_min_y
    ):
        raise ValueError("Ungültige Wagenabmessungen")
    if front_direction != "+X":
        raise ValueError("Aktuell wird als Wagenvorderseite nur +X unterstützt")
    if len(transformation.calibration_points) < 3:
        raise ValueError("Mindestens drei Transformationspunkte erforderlich")
    for point in transformation.calibration_points:
        if not workspace.contains(point):
            raise ValueError(f"Transformationspunkt außerhalb des Arbeitsraums: {point}")
