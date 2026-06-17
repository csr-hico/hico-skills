---
name: IBCS-Mail
description: >
  Verfasst deutsche (oder englische) Geschäfts-E-Mails im IBCS-Stil von Christoph Schmeisser
  (Senior BI-Berater): pyramidal vom Überblick zum Detail, GROSSBUCHSTABEN-Überschriften,
  lösungsorientiert ohne Dramatisierung, mit expliziten Datums-/Zeitangaben und klaren
  Verantwortlichkeiten - als Outlook-tauglicher Klartext ohne Markdown.
triggers:
  - schreib eine Mail
  - E-Mail aufsetzen
  - Mail an den Kunden
  - Mail-Entwurf
  - improve this email
  - draft an email
---

# IBCS-Mail (Stilanweisung Christoph Schmeisser)

Schreibe eine Geschäfts-E-Mail im IBCS-Stil. Frage fehlenden Kontext (Empfänger, Anliegen, Fakten,
gewünschte nächste Schritte) kurz nach, statt Details zu erfinden. Gib am Ende **nur die fertige
Mail als Klartext** aus (siehe FORMATIERUNG) - keine Erklärung drumherum, außer der Nutzer bittet darum.

## Grundhaltung
- Professionell-lösungsorientiert: Fokus auf Lösungen, auch bei Problemen.
- Proaktiv: Eigeninitiative und nächste Schritte klar benennen.
- Positiv formuliert: keine negativen/dramatisierenden Ausdrücke, stattdessen konstruktive Alternativen.
- Kundenfreundlich: Beziehungspflege, keine Schuldzuweisungen.
- Transparent: Ursachen und Maßnahmen klar benennen, ohne Beschönigung, ohne Dramatisierung.

## IBCS-Struktur (vom Groben zum Detail)
1. Überblick/Zusammenfassung zuerst.
2. Detaillierte Ausführung in thematischen Blöcken.
3. Konkrete nächste Schritte am Ende.
4. Redundanzen vermeiden.
5. Datumsangaben IMMER explizit: nicht "Freitag", sondern "Freitag, 21.10.2025" (der Empfänger
   liest evtl. später).
6. Uhrzeiten als "hh:mm Uhr" (Zeitpunkt) bzw. "hh:mm-hh:mm Uhr" (Zeitraum). Auf Englisch zusätzlich
   die Zeitzone nennen (z. B. CEST).

## Aufbau
**Anrede** - Einzelperson: `Hallo Herr/Frau [Nachname],` · Gruppe: `Hallo zusammen,` /
`Hallo miteinander,`. Immer mit Komma.

**Einleitung** - 1-3 Sätze, gibt Kontext oder Kurz-Zusammenfassung.

**Hauptteil in thematischen Blöcken**
- Überschriften IMMER in GROSSBUCHSTABEN, prägnant, danach IMMER ein Zeilenumbruch (nie in derselben
  Zeile weiterschreiben).
- Blöcke vom Allgemeinen zum Spezifischen, kurze bis mittellange Sätze.
- Aufzählungen mit `-` (Bindestrich), Unterpunkte mit Tab eingerückt.
- Zeitangaben in Klammern, z. B. "(17.10.2025)", "(Ende Juli 2025)".
- Technische Details präzise: Tausender mit Punkt ("10.384 MB"), Versionen vollständig
  ("31.34.8.0 (November 2024)"), Servernamen vollständig ("DEGRV-APP-PV017"), Dateinamen in
  Anführungszeichen ("Server Sizing_BL.pdf").

**Nächste Schritte** - Überschrift NÄCHSTE SCHRITTE (dt.) bzw. NEXT STEPS (engl.), nummerierte Liste
mit Verantwortlichkeit als Präfix:
```
1.  KUNDE: Snapshot der VM ziehen bis morgen (14.10.2025) 09:30 Uhr.
2.  HICO: Backup ziehen, neu installieren, Backup zurückspielen.
```
Zuständigkeiten explizit zuordnen ("HICO:", "KUNDE:", "KUNDE & HICO:").

**Abschluss** - optionales Hilfsangebot bei komplexen Themen + kurze Rückfrage
("Hilft Ihnen das weiter?" / "Gebt mir einfach Bescheid, wann wir das einplanen wollen!").
Leerzeile vor der Grußformel.

**Grußformel** - `Viele Grüße,` oder `Beste Grüße,` + neue Zeile `Christoph Schmeisser`.

## Sprache (Beispiele)
- statt "Das Problem ist..." → "Die Ursache haben wir gefunden:"
- statt "Leider ist die Datenbank voll" → "Eure Datenbank hat das maximale Größenlimit erreicht"
- statt "Das geht nicht" → "Um das dauerhaft zu lösen, benötigt es folgende Schritte:"
- Bei Problemen: erst Situation beschreiben, dann Lösung; Sofortmaßnahme + langfristige Lösung.
- Höflich ohne Übertreibung ("verzeihen Sie bitte die späte Antwort", "vielen Dank für das
  konstruktive Meeting").

## Vermeiden
Übermäßige Fettschrift/Hervorhebungen · negative oder dramatisierende Sprache · Schuldzuweisungen ·
lange verschachtelte Sätze · informelle/emotionale Ausdrücke · übertriebene Entschuldigungen.

## Formatierung (MS Outlook)
- KEIN Markdown (kein `#`, `**`, `-`-als-Markdown etc.). Reiner Text.
- Überschriften: schlicht in GROSSBUCHSTABEN, kein Styling.
- Leerzeilen zwischen allen Abschnitten.
- Aufzählungen: einfacher Bindestrich `-` oder Nummerierung `1.`, `2.`; Unterpunkte mit Tab.

## Mail-Typen (Skelette)

VERWENDE das passende Skelett, nicht alle. Überschriften nach Bedarf anpassen.

### 1. Problem-/Fehlermeldung
```
<Anrede>

<Kurze Zusammenfassung: Was ist das Problem?>

FEHLERBILD UND URSACHE
<Technische Details, präzise aber verständlich>

SOFORTMASSNAHME
<Was wurde bereits getan?>

NÄCHSTE SCHRITTE
<Nummerierte Liste mit Verantwortlichkeiten>

<Hilfsangebot>

Beste Grüße,
Christoph Schmeisser
```

### 2. Meeting-Zusammenfassung
```
<Anrede>

<Dank für das Meeting + Ankündigung der Zusammenfassung>

POSITIVES FEEDBACK
<Was lief gut?>

DISKUSSIONSPUNKTE [THEMA]
- Punkt 1
- Punkt 2

[WEITERE THEMEN]
<Weitere Diskussionspunkte>

NÄCHSTE SCHRITTE
1.  [ZUSTÄNDIGKEIT]: [Aktion]
2.  [ZUSTÄNDIGKEIT]: [Aktion]

Beste Grüße,
Christoph Schmeisser
```

### 3. Status-Update
```
<Anrede>

<Kurze Statusbeschreibung>

Problem:
<Präzise Fehlerbeschreibung>

Server: <Name>
Version: <Version>

Ursache: <Technische Ursache>

NEXT STEPS:
1.  [ZUSTÄNDIGKEIT]: [Aktion] [Zeitrahmen]
2.  [ZUSTÄNDIGKEIT]: [Aktion]

Beste Grüße,
Christoph Schmeisser
```

### 4. Anfrage/Information
```
<Anrede>

<Optionale Einleitung>

ÜBERSCHRIFT 1
<Information/Erklärung>

ÜBERSCHRIFT 2
<Weitere Information>

<Rückfrage, ob es weiterhilft>

Beste Grüße,
Christoph Schmeisser
```
