# Flexibler Punktimport

Der Importdialog wird nach der Dateiauswahl geöffnet und zeigt die gelesenen
Spalten vor dem eigentlichen Import.

## Pflichtfelder

- ID
- X
- Y
- Z

Optional können Markierungscode und Bemerkung zugeordnet werden. Ohne
Markierungscode wird Kennziffer 1 (Plus) verwendet.

## Einstellbarer Dateiaufbau

- Trennzeichen: beliebiger Leerraum, Semikolon, Komma, Tabulator oder ein
  eigenes einzelnes Zeichen
- Anzahl physischer Anfangszeilen, die übersprungen werden
- Dezimalzeichen Punkt oder Komma
- freie Zuordnung jeder fachlichen Information zu einer Dateispalte

Kommentarzeilen mit `#` oder `//` sowie leere Zeilen werden ignoriert.
Inline-Kommentare nach `//` werden außerhalb von Anführungszeichen entfernt.
Bemerkungen mit Leerzeichen können in doppelte Anführungszeichen gesetzt
werden.

## Beispiel

```text
Rechtswert;Punktnummer;Hoehe;Hochwert;Code;Bemerkung
41007.5;P1;9.25;-10619.5;2;Achse A
```

Einstellungen:

- eine Anfangszeile überspringen
- Semikolon als Trennzeichen
- ID = Spalte 2
- X = Spalte 1
- Y = Spalte 4
- Z = Spalte 3
- Markierung = Spalte 5
- Bemerkung = Spalte 6

Trennzeichen und Dezimalzeichen dürfen nicht identisch sein. Für CSV-Dateien
mit Komma als Trennzeichen müssen Dezimalzahlen daher einen Punkt verwenden.
