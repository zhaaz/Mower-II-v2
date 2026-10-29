from __future__ import annotations

from mower.application import MowerSystem
from mower.domain import Point3D
from mower.hardware.simulation import SimGyro, SimRotationMotor, SimTracker, SimXYZRobot


def main() -> None:
    system = MowerSystem(SimXYZRobot(), SimTracker(), SimGyro(), SimRotationMotor())
    system.initialize()
    result = system.simulation_probe(Point3D(100.0, 50.0, 165.9))
    print("Mower II v2 – Simulation betriebsbereit")
    for name, value in result.items():
        print(f"{name}: {value}")


if __name__ == "__main__":
    main()

