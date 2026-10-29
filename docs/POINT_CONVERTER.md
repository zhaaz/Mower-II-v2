# Mower Point Converter

Der Mower Point Converter ist ein eigenständiges Windows-Hilfsprogramm. Er
verändert weder die Installation noch den Quellcode von Mower II V1.

## Funktion

1. beliebige TXT-, CSV-, XYZ- oder DAT-Datei auswählen
2. Trennzeichen, Kopfzeilen, Dezimalzeichen und Spalten zuordnen
3. konvertierte Punkte in einer Tabelle kontrollieren
4. feste Mower-II-Punktdatei speichern

Das Zielformat lautet:

```text
punktnummer x y z kennziffer "bemerkung"
```

Koordinaten werden mit sechs Nachkommastellen und Punkt als Dezimalzeichen
geschrieben. Fehlt ein Markierungscode, wird Code 1 verwendet.

## Direkt aus Python starten

```powershell
python -m mower.tools.point_converter_app
```

## Windows-EXE erstellen

Im Projektverzeichnis:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\build_point_converter.ps1
```

Ergebnis:

```text
dist\MowerPointConverter\MowerPointConverter.exe
```

Der gesamte Ordner `dist\MowerPointConverter` kann auf einen anderen
Windows-Rechner kopiert werden. Python ist dort zum Ausführen nicht nötig.
