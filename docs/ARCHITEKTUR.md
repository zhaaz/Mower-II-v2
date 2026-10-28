# Architektur

V2 verwendet eine Ports-und-Adapter-Struktur:

1. `domain` enthält reine Fachmodelle ohne UI- oder Hardwareabhängigkeit.
2. `application` orchestriert vollständige Arbeitsabläufe.
3. `hardware/interfaces.py` definiert die Geräteverträge.
4. Reale und simulierte Adapter erfüllen exakt dieselben Verträge.
5. Die spätere UI ruft ausschließlich Anwendungsfälle auf.

Damit kann ein Ablauf zuerst vollständig simuliert und danach ohne zweite
Geschäftslogik an echter Hardware geprüft werden.

## Sicherheitsgrenze

Der Modus wird beim Programmstart festgelegt. Eine laufende Sitzung darf nicht
unbemerkt zwischen Simulation und Realbetrieb wechseln. Reale Bewegung benötigt
zusätzlich Initialisierung, Homing, gültige Transformation und aktuelle
Sensordaten. Nach Wiederherstellung eines Autosaves gelten Homing und
Transformation grundsätzlich als ungültig.

