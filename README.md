# Mower II v2

Neuaufbau der Bedien- und Steuerungssoftware des Mower-II-Abstecksystems.

Der produktive V1-Stand bleibt im separaten Repository `Mower-II`. V2 trennt
Bedienoberfläche, Anwendungslogik, Hardware und Speicherung konsequent und kann
denselben Ablauf wahlweise mit realer oder simulierter Hardware ausführen.

## Aktueller Stand

- kompatibler Import des bestehenden Punktformats
- typisierte Domänenmodelle und Geräteschnittstellen
- deterministische Simulation für XYZ, Lasertracker, Murata und GYEMS
- Simulations-Szenario inklusive Homing und Bewegung
- Konfigurationsdatei für Real-/Simulationsbetrieb
- Tests und Projektdokumentation
- reservierte V1-Hotkeys: `Strg+I/T/K/H/A`

Die echte Hardware wird erst in einer folgenden, separat prüfbaren Ausbaustufe
angeschlossen. Der aktuelle Stand sendet keine Befehle an reale Geräte.

## Start

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .[dev]
python -m pytest
python -m mower.simulation_demo
```

Weitere Informationen:

- [Projektbeschreibung](docs/PROJEKTBESCHREIBUNG.md)
- [Architektur](docs/ARCHITEKTUR.md)
- [Simulation](docs/SIMULATION.md)

