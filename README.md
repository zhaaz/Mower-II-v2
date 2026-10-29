# Mower II v2

Neuaufbau der Bedien- und Steuerungssoftware des Mower-II-Abstecksystems.

Der produktive V1-Stand bleibt im separaten Repository `Mower-II`. V2 trennt
Bedienoberfläche, Anwendungslogik, Hardware und Speicherung konsequent und kann
denselben Ablauf wahlweise mit realer oder simulierter Hardware ausführen.

## Aktueller Stand

- flexibler Punktimport mit Vorschau, Trennzeichen und Spaltenzuordnung
- typisierte Domänenmodelle und Geräteschnittstellen
- deterministische Simulation für XYZ, Lasertracker, Murata und GYEMS
- Simulations-Szenario inklusive Homing und Bewegung
- Konfigurationsdatei für Real-/Simulationsbetrieb
- Tests und Projektdokumentation
- reservierte V1-Hotkeys: `Strg+I/T/K/H/A`
- erste klassische GUI mit fester XYZ-Draufsicht
- berechnete Simulationstransformation mit Qualitätsprüfung
- kompakte Punktliste und Punktdetailviewer

Die echte Hardware wird erst in einer folgenden, separat prüfbaren Ausbaustufe
angeschlossen. Der aktuelle Stand sendet keine Befehle an reale Geräte.

## Start

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .[dev]
python -m pytest
python -m mower.simulation_demo
python -m mower.ui.app
```

Weitere Informationen:

- [Projektbeschreibung](docs/PROJEKTBESCHREIBUNG.md)
- [Architektur](docs/ARCHITEKTUR.md)
- [Simulation](docs/SIMULATION.md)
- [Punktimport](docs/PUNKTIMPORT.md)
- [Mower Point Converter](docs/POINT_CONVERTER.md)
- [Beispieldaten](examples/data/README.md)

