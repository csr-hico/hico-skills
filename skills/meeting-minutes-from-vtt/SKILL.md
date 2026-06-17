---
name: Meeting Minutes from VTT
triggers:
  - .vtt file uploaded
  - meeting minutes
  - Meeting-Protokoll
  - Besprechungsprotokoll
  - Teams-Transkript
  - Protokoll aus Transkript
  - turn this transcript into minutes
description: Wandelt eine Microsoft-Teams-Transkriptdatei (.vtt) in ein geschliffenes, IBCS-konformes Meeting-Protokoll um. Verwende diesen Skill immer, wenn eine .vtt-Datei hochgeladen wird oder der User von "Meeting Minutes", "Meeting-Protokoll", "Besprechungsprotokoll", "Teams-Transkript" oder "Protokoll aus Transkript" spricht — auch wenn das Wort "VTT" gar nicht fällt. Erkennt automatisch Deutsch oder Englisch, parst Sprecher und Aussagen aus dem WEBVTT-Format und liefert sauber strukturierte Minutes nach IBCS-Pyramidenprinzip (Aussage zuerst, dann Evidenz) im Christoph-Schmeisser-E-Mail-Stil. Auf Wunsch produziert er zusätzlich eine Outlook-fertige E-Mail-Variante mit GROSSBUCHSTABEN-Überschriften.
---

# Meeting Minutes aus VTT-Transkript

## Zweck

Aus einer Microsoft-Teams-Transkriptdatei (`.vtt`) ein vollständiges,
geschliffenes Meeting-Protokoll erzeugen. Output ist in derselben Sprache wie
das Transkript (Deutsch oder Englisch), folgt den IBCS-Prinzipien (Pyramide
vom Groben zum Detail, MECE-Strukturen, Aussage zuerst, präzise Sprache) und
ist sofort als E-Mail oder OneNote-Eintrag verwendbar.

Die Logik dieses Skills ist eine eigenständige Portierung des n8n-Workflows
"Teams Meeting Minutes Automation" (Workflow-ID `10v6Nbtf9Jq44GQ4` im
n8n_hico-Server). Der Workflow läuft automatisiert alle 15 Minuten auf
abgeschlossenen Teams-Meetings; dieser Skill macht dieselbe Aufbereitung
manuell für eine einzelne hochgeladene VTT-Datei.

## Wann auslösen

Trigger den Skill, sobald eines davon zutrifft:

- Eine `.vtt`-Datei wird hochgeladen
- Der User fragt nach "Meeting Minutes", "Meeting-Protokoll",
  "Besprechungsprotokoll", "Teams-Protokoll", "Protokoll aus Transkript"
- Der User übergibt einen Teams-Transkript-Inhalt (auch als Text-Paste) und
  möchte ihn aufbereitet bekommen

## Ablauf

Der Skill arbeitet in vier Schritten. Jeder Schritt baut auf dem vorherigen auf.

### Schritt 1 — VTT-Datei einlesen und parsen

Verwende das Skript `scripts/parse_vtt.py`, um das WEBVTT-Format in eine saubere
Sprecher/Aussage-Struktur umzuwandeln. Das Skript:

- entfernt WEBVTT-Header, Cue-Timestamps und `-->`-Marker
- erkennt `<v Sprechername>...</v>`-Tags und ordnet Folgezeilen ohne Tag dem
  aktuellen Sprecher zu
- entfernt innere HTML-Tags
- erkennt automatisch die Sprache (Deutsch/Englisch) per Stopword-Analyse +
  Umlaute (Umlaute zählen doppelt)

Aufruf:

```bash
python3 scripts/parse_vtt.py /pfad/zur/datei.vtt
```

Output ist ein JSON-Objekt mit `clean_transcript`, `language`, `language_name`,
`speakers` und `utterance_count`. Lies dieses JSON ein, bevor du weitermachst.

Falls das Skript nicht verfügbar ist, kannst du dieselbe Logik auch direkt in
einer einmaligen Python-Zelle anwenden — die Logik ist im Skript dokumentiert.

### Schritt 2 — Meta-Informationen erfragen oder ableiten

Frage den User höflich nach den Meta-Infos, die NICHT aus der VTT-Datei kommen,
aber für den Header gebraucht werden:

- **Subject** (Meeting-Titel) — falls nicht aus dem Dateinamen ableitbar
- **Date** (Datum + Zeitraum, z. B. `25.04.2026, 10:00 – 11:00 Uhr`)
- **Organizer** (Name + ggf. E-Mail)
- **Attendees** (Liste, kann oft aus den `speakers` aus Schritt 1 abgeleitet
  werden, aber Teilnehmer ohne Wortmeldung fehlen dort)

Wenn der User die Infos schon in der ursprünglichen Anfrage geliefert hat, NICHT
nochmal nachfragen — dann direkt verwenden.

**Datumsformat — strikt nach Schmeisser-Stil:**

- Deutsch: `25.04.2026, 10:00 – 11:00 Uhr`
- Englisch: `2026-04-25, 10:00 – 11:00 CEST` (Zeitzone bei Englisch immer dazu)

### Schritt 3 — Meeting Minutes generieren

Erzeuge die Minutes nach exakt dieser Struktur. Die Sektions-Überschriften
übersetzt du in die erkannte Sprache.

#### Output-Struktur (Markdown)

```markdown
## **Meeting Minutes: <Subject>**
**Date**: <Datumsangabe>
**Organizer**: <Name <email>>
**Attendees**: <Liste>

## **Summary**
<2-4 Sätze, die die Kernaussage des Meetings transportieren — NICHT nur
beschreiben, dass das Meeting stattfand. Wer nur die Summary liest, muss
verstehen, was rauskam und was als nächstes passiert.>

## **Topics Discussed**
- <Thema 1 als Nominalphrase>
- <Thema 2 als Nominalphrase>
- ...

## **Decisions**
- <Entscheidung 1, getroffen von <Person/Gruppe>>
- <Entscheidung 2, getroffen von <Person/Gruppe>>
- (Falls keine: "Keine Entscheidungen getroffen." / "No decisions made.")

## **Action Items**
- **<Owner>** – <Aufgabe als Imperativ + Substantiv> – Fällig: **<Datum>**
- **<Owner>** – <Aufgabe> – Fällig: **<Datum>**
- (Bei fehlendem Owner: **Unzugeordnet** / **Unassigned**)
- (Bei fehlendem Datum: **Kein Termin** / **No deadline**)

## **Next Meeting**
<Nur einbinden, wenn im Transkript erwähnt — sonst Sektion komplett weglassen.>
```

#### Sprachregel — kompromisslos

Schreibe die KOMPLETTE Antwort in der erkannten Sprache: Überschriften,
Sektions-Labels, Bullet-Punkte, Platzhalter-Texte und jedes weitere Wort. Wenn
das Transkript Englisch ist, ist alles auf Englisch. Wenn Deutsch, alles auf
Deutsch. Niemals mischen. Selbst die Header-Labels (`Date`, `Organizer`,
`Attendees`) werden übersetzt — nur die Werte bleiben verbatim.

Deutsche Übersetzung der Header-Labels:
- `Date` → `Datum`
- `Organizer` → `Organisator`
- `Attendees` → `Teilnehmer`
- `Meeting Minutes` → `Meeting-Protokoll`

Deutsche Übersetzung der Sektions-Überschriften:
- `Summary` → `Zusammenfassung`
- `Topics Discussed` → `Diskutierte Themen`
- `Decisions` → `Entscheidungen`
- `Action Items` → `Offene Aufgaben`
- `Next Meeting` → `Nächstes Meeting`

#### Inhaltliche Regeln (IBCS, siehe `references/ibcs_principles.md`)

1. **Aussage zuerst (SA 3.2)** — Die Summary muss die Kernaussage des Meetings
   liefern, nicht den Verlauf beschreiben. Falscher Reflex: "Im Meeting wurde
   über X gesprochen." Richtig: "X wird bis Datum Y umgesetzt, weil Z."

2. **Präzise Worte (SA 4.2)** — Keine schwammigen Begriffe wie "zeitnah",
   "relevant", "in Kürze", "demnächst". Nutze Datumsangaben, Namen, Zahlen.

3. **Konsistente Aussage-Typen pro Sektion (ST 1.2)** —
   - "Topics Discussed": nur Themen (Nominalphrasen)
   - "Decisions": nur getroffene Entscheidungen (Vergangenheit/Perfekt)
   - "Action Items": nur offene Aufgaben (Imperativ + Owner + Datum)
   - Niemals mischen.

4. **Konsistentes Wording (ST 1.3)** — Action Items haben IMMER die Form
   `**Owner** – Task – Fällig: **Datum**`. Nicht abwechselnd mal so, mal anders.

5. **MECE (ST 2 + ST 3)** — Eine Information gehört in genau eine Sektion. Eine
   Entscheidung kommt in "Decisions"; falls daraus eine Aufgabe entsteht, kommt
   nur die Aufgabe in "Action Items" — nicht die Entscheidung doppelt.

6. **Pyramide (ST 4)** — Header → Summary → Detail-Sektionen. Wer absteigt,
   bekommt mehr Details.

#### Faktentreue

- Erfinde nichts. Wenn das Transkript keine Decisions enthält, schreib das
  explizit hin (Platzhalter), statt etwas zu fingieren.
- Owner für Action Items NUR vergeben, wenn der Name im Transkript klar
  zugeordnet wird. Sonst `**Unzugeordnet**` / `**Unassigned**`.
- Daten/Termine NUR übernehmen, wenn sie im Transkript genannt werden. Sonst
  `**Kein Termin**` / `**No deadline**`.

#### Was du NICHT tust

- Keine Trennlinien (`---`, `***`, `___`) — die Sektions-Überschriften reichen.
- Keine Präambel ("Hier ist Ihr Protokoll:" etc.) — direkt mit dem Header
  beginnen.
- Keine Kommentare nach dem Output ("Hoffe, das hilft!") — der Markdown-Block
  ist die Antwort.
- Keine eigene Interpretation oder Bewertung des Meetings — nur das, was im
  Transkript steht, geschliffen formuliert.

### Schritt 4 — Optionale E-Mail-Variante (Schmeisser-Stil)

Wenn der User explizit nach einer "E-Mail-Version", "Outlook-Version",
"versendbaren Version" oder ähnlichem fragt, baue zusätzlich eine zweite
Variante. Diese folgt der vollständigen Stilanweisung in
`references/email_style.md` — die wichtigsten Anpassungen:

- **Anrede**: `Hallo zusammen,` (DE) bzw. `Hi all,` (EN)
- **Einleitung** (1-2 Sätze): `anbei das Protokoll für unser Meeting vom <Datum>.`
- **Überschriften**: in GROSSBUCHSTABEN, ohne Markdown-Sterne, mit
  Zeilenumbruch danach. Beispiel: `ZUSAMMENFASSUNG` statt `## **Summary**`.
- **Datums-/Zeitangaben** immer explizit (nicht "morgen", sondern
  "Dienstag, 28.04.2026"; nicht nur "10:00", sondern "10:00 Uhr" / bei EN
  "10:00 CEST").
- **Action Items** als nummerierte Liste mit Verantwortlichkeits-Präfix
  (`1.  HICO: ...`, `2.  KUNDE: ...`), wenn klar zuordenbar — sonst Owner-Name.
- **Abschluss**: kurzer Hilfsangebot-Satz, dann Leerzeile, dann
  `Viele Grüße,\nChristoph Schmeisser` (DE) bzw.
  `Best regards,\nChristoph Schmeisser` (EN).
- **Keine Markdown-Formatierung** im E-Mail-Body — der Body ist Klartext für
  Outlook, also keine `#`, keine `**`.

## Beispiel — Deutscher Output

Eingang: VTT-Datei aus einem Meeting zwischen Christoph Schmeisser und Daniele
Müller über die Serverauslegung am 25.04.2026.

```markdown
## **Meeting-Protokoll: Serverauslegung TRUECHART-Umgebung**
**Datum**: 25.04.2026, 10:00 – 11:00 Uhr
**Organisator**: Christoph Schmeisser <christoph.schmeisser@hico-group.com>
**Teilnehmer**: Christoph Schmeisser, Daniele Müller

## **Zusammenfassung**
Die neue TRUECHART-Umgebung wird mit 32 GB RAM und 8 vCPUs ausgelegt, um die
erwartete Last von 50 gleichzeitigen Usern abzudecken. Daniele liefert bis
Freitag, 02.05.2026, das finale Sizing-Dokument; HICO setzt anschließend die
Bestellung beim Hosting-Partner auf.

## **Diskutierte Themen**
- Mindestanforderungen für RAM und CPU
- Erwartete Anzahl gleichzeitiger User
- Backup-Strategie für die VM
- Rollout-Zeitplan bis Q3 2026

## **Entscheidungen**
- Sizing wird auf 32 GB RAM / 8 vCPUs festgelegt (Christoph + Daniele)
- Tägliche Snapshots werden über den Hosting-Partner eingerichtet (Daniele)

## **Offene Aufgaben**
- **Daniele** – Sizing-Dokument finalisieren und an HICO senden – Fällig: **02.05.2026**
- **HICO** – Bestellung beim Hosting-Partner aufsetzen – Fällig: **09.05.2026**
- **Christoph** – Rollout-Plan im nächsten Jour Fixe vorstellen – Fällig: **Kein Termin**
```

## Beispiel — Englischer Output

```markdown
## **Meeting Minutes: TRUECHART Server Sizing**
**Date**: 2026-04-25, 10:00 – 11:00 CEST
**Organizer**: Christoph Schmeisser <christoph.schmeisser@hico-group.com>
**Attendees**: Christoph Schmeisser, Daniele Müller

## **Summary**
The new TRUECHART environment will be sized at 32 GB RAM and 8 vCPUs to cover
the expected load of 50 concurrent users. Daniele will deliver the final sizing
document by Friday, 2026-05-02; HICO will then place the order with the hosting
partner.

## **Topics Discussed**
- Minimum requirements for RAM and CPU
- Expected number of concurrent users
- Backup strategy for the VM
- Rollout timeline through Q3 2026

## **Decisions**
- Sizing fixed at 32 GB RAM / 8 vCPUs (Christoph + Daniele)
- Daily snapshots will be configured via the hosting partner (Daniele)

## **Action Items**
- **Daniele** – Finalize the sizing document and send it to HICO – Due: **2026-05-02**
- **HICO** – Place the order with the hosting partner – Due: **2026-05-09**
- **Christoph** – Present the rollout plan in the next Jour Fixe – Due: **No deadline**
```

## Referenzen

- `references/ibcs_principles.md` — IBCS-Auszug mit den für Meeting Minutes
  relevanten SAY- und STRUCTURE-Regeln. Lies dies, wenn unklar ist, wie eine
  Sektion strukturiert werden soll.
- `references/email_style.md` — vollständige E-Mail-Stilanweisung
  von Christoph Schmeisser. Lies dies, sobald der User eine E-Mail-Variante
  möchte.
- `scripts/parse_vtt.py` — Python-Portierung der VTT-Parser-Logik aus dem
  n8n-Workflow. Erste Wahl für das Einlesen.

## Hintergrund — Warum dieser Skill?

Der n8n-Workflow `10v6Nbtf9Jq44GQ4` ("Teams Meeting Minutes Automation")
erledigt diese Aufgabe automatisiert für alle Online-Meetings im Kalender,
deckt aber drei Fälle nicht ab:

1. **Externe VTT-Dateien** — z. B. weitergeleitete Transkripte aus Meetings, in
   denen der User nicht selbst Organizer war.
2. **Manuelle Anpassung** — wenn der automatisch erzeugte Output nochmal
   überarbeitet werden muss, bevor er rausgeht.
3. **Iteratives Arbeiten** — wenn der User mehrere Anpassungs-Runden braucht
   (Tonalität, Granularität, zusätzliche Sektionen).

Dieser Skill schließt diese Lücke und nutzt dabei dieselbe Parsing- und
Strukturierungs-Logik wie der Workflow, ergänzt um IBCS-Konformität und den
Schmeisser-E-Mail-Stil.
