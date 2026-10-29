# Projektbeschreibung Mower II v2

## 1. Ziel

Mower II ist ein mobiles Abstecksystem, das Sollpunkte aus einer Punktdatei mit
Lasertracker, Murata SCH16T, GYEMS-Drehmotor und einem Marlin-gesteuerten
XYZ-Roboter anfährt, markiert und kontrolliert. V2 ist ein technischer Neuaufbau
unter Beibehaltung des bewährten hellen, klassischen Bedienkonzepts.

## 2. Abgrenzung zu V1

V1 bleibt unverändert als produktiver und nachvollziehbarer Referenzstand
erhalten. V2 entsteht im separaten Repository und übernimmt Verhalten nur nach
Prüfung. Alte V1-Projektdateien müssen nicht kompatibel sein; das bestehende
Punktimportformat bleibt kompatibel.

## 3. Referenzmaterial vom 28.10.2026

- aktueller V1-Stand im Repository `zhaaz/Mower-II`
- Marlin 2.1.2.5 für den XYZ-Roboter
- Arduino-Sketch `Murata_SCH16T_Only_Yaw.ino`
- Trackerstandpunkt `0.000000,0.000000,0.000000`
- V1-Projektexport vom 28.10.2026
- Labor-Punktdatei vom 22.10.2026

Das vollständige Marlin-Quellarchiv wird nicht ungeprüft übernommen.
Build-Ausgaben aus `.pio` gehören nicht ins Repository.

## 4. Bedienung

Der generelle V1-Look bleibt bestehen. Menüs dürfen nach Arbeitsablauf neu
geordnet und seltene Diagnosefunktionen nachgeordnet werden.

| Hotkey | Hauptbefehl |
| --- | --- |
| Strg+I | System initialisieren |
| Strg+T | Transformation |
| Strg+K | Marker-/Reflektoroffset kalibrieren |
| Strg+H | Markierhöhe kalibrieren |
| Strg+A | Absteckung |

## 5. Datenformat

Standardzeile:

```text
punktnummer x y z kennziffer "bemerkung" // optionaler Kommentar
```

Koordinaten sind in Millimeter. Markerkennziffern: 1 Plus, 2 Kreuz, 3
Kreis/Punkt, 4 Plus/Kreis.

## 6. Hardware

| Komponente | V2-Strategie |
| --- | --- |
| XYZ/Marlin | serieller Realadapter plus Simulationsadapter |
| Lasertracker/SpatialAnalyzer | UDP-Realadapter plus simulierte Messquelle |
| Murata SCH16T-K01 | Arduino seriell, 115200 Baud, 100 Hz |
| GYEMS | RS485-Realadapter plus simulierter Winkelantrieb |

Das aktuelle Murata-Protokoll lautet
`time_us;gyro_z_dps;yaw_raw_deg`. Vor echter Inbetriebnahme müssen die
Vorzeichen von Murata, GYEMS und allen XYZ-Achsen am Wagen bestätigt werden.

## 7. Persistenz und Wiederanlauf

Projektzustände werden atomar mit Backup gespeichert. Während einer Markierung
gilt ein expliziter Zwischenzustand. Nach Absturz wird er als unbekannt
behandelt. Wiederherstellung reaktiviert weder Homing noch Transformation.

## 8. Qualitätsziele

- keine direkte Hardwaresteuerung aus UI-Code
- deterministische Tests ohne Hardware
- explizite Zustände und nachvollziehbare Fehler
- einheitliche Einheiten: Millimeter, Grad und Sekunden
- reale Bewegung erst nach Sicherheitsvorbedingungen
- reproduzierbarer EXE-Build

## 9. Ausbaustufen

1. Kernarchitektur, Punktimport und Simulation
2. Transformation und vollständiger virtueller Absteckablauf
3. klassische Bedienoberfläche
4. reale Adapter einzeln migrieren und mit Protokolltests absichern
5. Autosave, Export, Replay und Fehlerdiagnose
6. EXE-Build und Laborabnahme

## 10. Offene Bestätigungen

- physische Richtungen X+, Y+ und Z+
- positive Drehrichtung von Murata und GYEMS
- freigegebene COM-Ports und Baudraten
- verbindliche Arbeitsraumgrenzen
- endgültiges SpatialAnalyzer-UDP-Format

## 11. Änderungshistorie

| Datum | Version | Änderung |
| --- | --- | --- |
| 28.10.2026 | 0.1 | Grundstruktur, Punktimport, Schnittstellen und Simulation |
| 28.10.2026 | 0.2 | Klassische Simulations-GUI, Ablaufzustände und XYZ-Draufsicht |
| 29.10.2026 | 0.3 | Zoombare Projektansicht mit Tracker/Wagen und Referenzdaten |
| 29.10.2026 | 0.4 | Wagengeometrie und verbindliche XYZ-Reichweitenprüfung |
| 29.10.2026 | 0.5 | Wagenrichtung, Kartenverschiebung, Wagenzoom und Maßstabsbalken |
| 29.10.2026 | 0.6 | Validierte Config, berechnete Simulationstransformation und Punktviewer |
| 29.10.2026 | 0.7 | Flexibler Punktimport mit Vorschau und frei zuweisbaren Spalten |

