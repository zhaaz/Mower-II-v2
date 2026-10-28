# Simulation

Die Simulation ist kein zweiter Demo-Ablauf. Sie implementiert dieselben
Geräteschnittstellen, die später von den realen Adaptern verwendet werden.

Aktuell simuliert:

- XYZ-Verbindung, Homing, Bewegung und Arbeitsraumverletzungen
- Lasertrackermessungen mit reproduzierbarem Gauß-Rauschen
- Murata-Yaw
- GYEMS-Winkel

Geplant:

- einstellbare Bewegungsdauer
- Drift und Sensorausfälle
- Verbindungsabbrüche und Timeouts
- virtueller Transformations- und Markierablauf
- Aufzeichnung und Wiedergabe realer Sensordaten

```powershell
python -m mower.simulation_demo
```

