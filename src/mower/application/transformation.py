from __future__ import annotations

import math
import random
from dataclasses import dataclass

from mower.domain import Point3D, WagonPose


@dataclass(frozen=True, slots=True)
class TransformationMeasurement:
    local: Point3D
    measured_project: Point3D


@dataclass(frozen=True, slots=True)
class TransformationResult:
    pose: WagonPose
    residuals_mm: tuple[float, ...]
    rms_mm: float
    max_residual_mm: float


def solve_rigid_transformation(
    measurements: list[TransformationMeasurement],
) -> TransformationResult:
    if len(measurements) < 2:
        raise ValueError("Mindestens zwei Messungen erforderlich")
    local_mean_x = sum(item.local.x for item in measurements) / len(measurements)
    local_mean_y = sum(item.local.y for item in measurements) / len(measurements)
    project_mean_x = (
        sum(item.measured_project.x for item in measurements) / len(measurements)
    )
    project_mean_y = (
        sum(item.measured_project.y for item in measurements) / len(measurements)
    )
    numerator = 0.0
    denominator = 0.0
    for item in measurements:
        lx = item.local.x - local_mean_x
        ly = item.local.y - local_mean_y
        px = item.measured_project.x - project_mean_x
        py = item.measured_project.y - project_mean_y
        numerator += lx * py - ly * px
        denominator += lx * px + ly * py
    if abs(numerator) + abs(denominator) < 1.0e-12:
        raise ValueError("Unzureichende Geometrie der Transformationspunkte")
    yaw_rad = math.atan2(numerator, denominator)
    cosine = math.cos(yaw_rad)
    sine = math.sin(yaw_rad)
    origin_x = project_mean_x - (cosine * local_mean_x - sine * local_mean_y)
    origin_y = project_mean_y - (sine * local_mean_x + cosine * local_mean_y)
    origin_z = sum(
        item.measured_project.z - item.local.z for item in measurements
    ) / len(measurements)
    pose = WagonPose(
        Point3D(origin_x, origin_y, origin_z),
        math.degrees(yaw_rad),
    )
    residuals: list[float] = []
    for item in measurements:
        predicted = pose.local_to_project(item.local)
        residuals.append(
            math.sqrt(
                (predicted.x - item.measured_project.x) ** 2
                + (predicted.y - item.measured_project.y) ** 2
                + (predicted.z - item.measured_project.z) ** 2
            )
        )
    rms = math.sqrt(sum(value * value for value in residuals) / len(residuals))
    return TransformationResult(pose, tuple(residuals), rms, max(residuals))


def simulate_measurements(
    local_points: tuple[Point3D, ...],
    true_pose: WagonPose,
    noise_mm: float,
    seed: int,
) -> list[TransformationMeasurement]:
    generator = random.Random(seed)
    result: list[TransformationMeasurement] = []
    for point in local_points:
        exact = true_pose.local_to_project(point)
        measured = Point3D(
            exact.x + generator.gauss(0.0, noise_mm),
            exact.y + generator.gauss(0.0, noise_mm),
            exact.z + generator.gauss(0.0, noise_mm),
        )
        result.append(TransformationMeasurement(point, measured))
    return result
