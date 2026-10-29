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
python -m mower.ui.app
```

Die GUI kennzeichnet den Simulationsmodus dauerhaft. In der XYZ-Draufsicht
rechts unten zeigt X+ nach oben und Y+ nach links. Der grüne Punkt ist die
aktuelle XYZ-Position, das orange Fadenkreuz die ausgewählte Zielposition.
X und Y werden mit demselben Maßstab dargestellt; die Arbeitsraumgrenzen
stammen aus der Gerätekonfiguration.

Die große Projektansicht zeigt Absteckpunkte, Lasertracker und die simulierte
Wagenposition. Sie kann über Mausrad sowie die Schaltflächen `+`, `−` und
`Alles` gezoomt werden. Beim Mausradzoom bleibt die Position unter dem
Mauszeiger erhalten.

Der Wagen wird mit 600 × 500 mm dargestellt. Der darin liegende XYZ-Arbeitsraum
beträgt X=0…500 mm und Y=0…400 mm; die Z-Grenzen liegen bei 150…200 mm.
Nur Punkte, deren transformierte lokale Koordinate innerhalb dieser Grenzen
liegt, werden als erreichbar freigegeben. Im Simulationsmenü kann der Wagen
auf den ausgewählten Punkt versetzt werden.

