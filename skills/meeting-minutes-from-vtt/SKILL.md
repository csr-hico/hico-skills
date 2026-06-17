---
name: Meeting Minutes from VTT
triggers:
  - .vtt file uploaded
  - meeting minutes
  - meeting protocol
  - Teams transcript
  - minutes from transcript
  - turn this transcript into minutes
description: >
  Turns a Microsoft Teams transcript file (.vtt) into a polished, IBCS-compliant set of meeting
  minutes. Use this skill whenever a .vtt file is uploaded or the user mentions "meeting minutes",
  "meeting protocol", "minutes from transcript" or a "Teams transcript" - even if the word "VTT"
  is never used. It auto-detects German or English, parses speakers and utterances from the WEBVTT
  format, and produces cleanly structured minutes following the IBCS pyramid principle (message
  first, then evidence) in the HICO consultant email style. On request it additionally
  produces an Outlook-ready email variant with UPPERCASE headings.
---

# Meeting Minutes from a VTT Transcript

## Purpose

Produce complete, polished meeting minutes from a Microsoft Teams transcript
file (`.vtt`). The output is in the same language as the transcript (German or
English), follows IBCS principles (pyramid from broad to detail, MECE
structures, message first, precise language) and is immediately usable as an
email or OneNote entry.

The logic of this skill is a standalone port of the n8n workflow "Teams Meeting
Minutes Automation" (workflow ID `10v6Nbtf9Jq44GQ4` on the n8n_hico server).
That workflow runs automatically every 15 minutes against completed Teams
meetings; this skill performs the same processing manually for a single
uploaded VTT file.

## When to trigger

Trigger the skill as soon as one of these applies:

- A `.vtt` file is uploaded
- The user asks for "meeting minutes", "meeting protocol", "minutes from
  transcript", or a "Teams transcript" write-up
- The user hands over Teams transcript content (also as pasted text) and wants
  it cleaned up

## Procedure

The skill works in four steps. Each step builds on the previous one.

### Step 1 - Read and parse the VTT file

Use the script `scripts/parse_vtt.py` to convert the WEBVTT format into a clean
speaker/utterance structure. The script:

- strips the WEBVTT header, cue timestamps, and `-->` markers
- detects `<v SpeakerName>...</v>` tags and assigns following untagged lines to
  the current speaker
- removes inner HTML tags
- auto-detects the language (German/English) via stopword analysis + umlauts
  (umlauts count double)

Invocation:

```bash
python3 scripts/parse_vtt.py /path/to/file.vtt
```

The output is a JSON object with `clean_transcript`, `language`,
`language_name`, `speakers` and `utterance_count`. Read this JSON before moving
on.

If the script is not available, you can apply the same logic directly in a
one-off Python cell - the logic is documented in the script.

### Step 2 - Ask for or derive meta information

Politely ask the user for the meta info that does NOT come from the VTT file but
is needed for the header:

- **Subject** (meeting title) - if not derivable from the file name
- **Date** (date + time range, e.g. `25.04.2026, 10:00 - 11:00 Uhr`)
- **Organizer** (name and, if available, email)
- **Attendees** (list; often derivable from the `speakers` from step 1, but
  attendees who never spoke are missing there)

If the user already provided the info in the original request, do NOT ask
again - use it directly.

**Date format - strictly per the house style:**

- German: `25.04.2026, 10:00 - 11:00 Uhr`
- English: `2026-04-25, 10:00 - 11:00 CEST` (always include the time zone for
  English)

### Step 3 - Generate the meeting minutes

Produce the minutes in exactly this structure. Translate the section headings
into the detected language.

#### Output structure (Markdown)

```markdown
## **Meeting Minutes: <Subject>**
**Date**: <date>
**Organizer**: <Name <email>>
**Attendees**: <list>

## **Summary**
<2-4 sentences that convey the core message of the meeting - NOT just a
description that the meeting took place. Anyone who reads only the summary must
understand what came out of it and what happens next.>

## **Topics Discussed**
- <Topic 1 as a noun phrase>
- <Topic 2 as a noun phrase>
- ...

## **Decisions**
- <Decision 1, made by <person/group>>
- <Decision 2, made by <person/group>>
- (If none: "No decisions made." / "Keine Entscheidungen getroffen.")

## **Action Items**
- **<Owner>** - <task as imperative + noun> - Due: **<date>**
- **<Owner>** - <task> - Due: **<date>**
- (If owner missing: **Unassigned** / **Unzugeordnet**)
- (If date missing: **No deadline** / **Kein Termin**)

## **Next Meeting**
<Only include if mentioned in the transcript - otherwise omit the section
entirely.>
```

#### Language rule - non-negotiable

Write the ENTIRE answer in the detected language: headings, section labels,
bullet points, placeholder texts, and every other word. If the transcript is in
English, everything is in English. If German, everything is in German. Never
mix. Even the header labels (`Date`, `Organizer`, `Attendees`) are translated -
only the values stay verbatim.

German translation of the header labels:
- `Date` -> `Datum`
- `Organizer` -> `Organisator`
- `Attendees` -> `Teilnehmer`
- `Meeting Minutes` -> `Meeting-Protokoll`

German translation of the section headings:
- `Summary` -> `Zusammenfassung`
- `Topics Discussed` -> `Diskutierte Themen`
- `Decisions` -> `Entscheidungen`
- `Action Items` -> `Offene Aufgaben`
- `Next Meeting` -> `Nächstes Meeting`

#### Content rules (IBCS, see `references/ibcs_principles.md`)

1. **Message first (SA 3.2)** - The summary must deliver the core message of the
   meeting, not describe its course. Wrong reflex: "The meeting discussed X."
   Right: "X will be implemented by date Y, because Z."

2. **Precise words (SA 4.2)** - No vague terms like "soon", "relevant",
   "shortly", "in the near future". Use dates, names, numbers.

3. **Consistent statement types per section (ST 1.2)** -
   - "Topics Discussed": topics only (noun phrases)
   - "Decisions": decisions made only (past tense)
   - "Action Items": open tasks only (imperative + owner + date)
   - Never mix.

4. **Consistent wording (ST 1.3)** - Action items always take the form
   `**Owner** - Task - Due: **Date**`. Not alternating between styles.

5. **MECE (ST 2 + ST 3)** - A piece of information belongs in exactly one
   section. A decision goes into "Decisions"; if a task arises from it, only the
   task goes into "Action Items" - not the decision twice.

6. **Pyramid (ST 4)** - Header -> Summary -> detail sections. Whoever descends
   gets more detail.

#### Faithfulness to the facts

- Invent nothing. If the transcript contains no decisions, state that explicitly
  (placeholder) instead of fabricating something.
- Assign an owner to an action item ONLY if the name is clearly attributable in
  the transcript. Otherwise `**Unassigned**` / `**Unzugeordnet**`.
- Take over dates/deadlines ONLY if they are mentioned in the transcript.
  Otherwise `**No deadline**` / `**Kein Termin**`.

#### What you do NOT do

- No separator lines (`---`, `***`, `___`) - the section headings are enough.
- No preamble ("Here are your minutes:" etc.) - start directly with the header.
- No comments after the output ("Hope this helps!") - the Markdown block is the
  answer.
- No interpretation or evaluation of the meeting - only what is in the
  transcript, phrased cleanly.

### Step 4 - Optional email variant (house style)

If the user explicitly asks for an "email version", "Outlook version",
"sendable version" or similar, additionally build a second variant. It follows
the full style instruction in `references/email_style.md` - the most important
adjustments:

- **Salutation**: `Hi all,` (EN) or `Hallo zusammen,` (DE)
- **Intro** (1-2 sentences): `please find attached the minutes for our meeting
  of <date>.`
- **Headings**: in UPPERCASE, without Markdown asterisks, with a line break
  after them. Example: `SUMMARY` instead of `## **Summary**`.
- **Dates/times** always explicit (not "tomorrow", but "Tuesday, 2026-04-28";
  not just "10:00", but "10:00 CEST" for English / "10:00 Uhr" for German).
- **Action items** as a numbered list with a responsibility prefix
  (`1.  HICO: ...`, `2.  CUSTOMER: ...`) when clearly attributable - otherwise
  the owner name.
- **Closing**: a short offer-of-help sentence, then a blank line, then
  `Best regards,\n<First name> <Last name>` (EN) or
  `Viele Grüße,\n<First name> <Last name>` (DE).
- **No Markdown formatting** in the email body - the body is plain text for
  Outlook, so no `#`, no `**`.

## Example - English output

Input: VTT file from a meeting between Alex Morgan and Sam Rivera about server
sizing on 2026-04-25.

```markdown
## **Meeting Minutes: TRUECHART Server Sizing**
**Date**: 2026-04-25, 10:00 - 11:00 CEST
**Organizer**: Alex Morgan <alex.morgan@example.com>
**Attendees**: Alex Morgan, Sam Rivera

## **Summary**
The new TRUECHART environment will be sized at 32 GB RAM and 8 vCPUs to cover
the expected load of 50 concurrent users. Sam will deliver the final sizing
document by Friday, 2026-05-02; HICO will then place the order with the hosting
partner.

## **Topics Discussed**
- Minimum requirements for RAM and CPU
- Expected number of concurrent users
- Backup strategy for the VM
- Rollout timeline through Q3 2026

## **Decisions**
- Sizing fixed at 32 GB RAM / 8 vCPUs (Alex + Sam)
- Daily snapshots will be configured via the hosting partner (Sam)

## **Action Items**
- **Sam** - Finalize the sizing document and send it to HICO - Due: **2026-05-02**
- **HICO** - Place the order with the hosting partner - Due: **2026-05-09**
- **Alex** - Present the rollout plan in the next Jour Fixe - Due: **No deadline**
```

## Example - German output

```markdown
## **Meeting-Protokoll: Serverauslegung TRUECHART-Umgebung**
**Datum**: 25.04.2026, 10:00 - 11:00 Uhr
**Organisator**: Alex Morgan <alex.morgan@example.com>
**Teilnehmer**: Alex Morgan, Sam Rivera

## **Zusammenfassung**
Die neue TRUECHART-Umgebung wird mit 32 GB RAM und 8 vCPUs ausgelegt, um die
erwartete Last von 50 gleichzeitigen Usern abzudecken. Sam liefert bis
Freitag, 02.05.2026, das finale Sizing-Dokument; HICO setzt anschließend die
Bestellung beim Hosting-Partner auf.

## **Diskutierte Themen**
- Mindestanforderungen für RAM und CPU
- Erwartete Anzahl gleichzeitiger User
- Backup-Strategie für die VM
- Rollout-Zeitplan bis Q3 2026

## **Entscheidungen**
- Sizing wird auf 32 GB RAM / 8 vCPUs festgelegt (Alex + Sam)
- Tägliche Snapshots werden über den Hosting-Partner eingerichtet (Sam)

## **Offene Aufgaben**
- **Sam** - Sizing-Dokument finalisieren und an HICO senden - Fällig: **02.05.2026**
- **HICO** - Bestellung beim Hosting-Partner aufsetzen - Fällig: **09.05.2026**
- **Alex** - Rollout-Plan im nächsten Jour Fixe vorstellen - Fällig: **Kein Termin**
```

## References

- `references/ibcs_principles.md` - IBCS excerpt with the SAY and STRUCTURE
  rules relevant to meeting minutes. Read this when it is unclear how a section
  should be structured.
- `references/email_style.md` - the full house email style instruction. Read
  this as soon as the user wants an email variant.
- `scripts/parse_vtt.py` - Python port of the VTT parser logic from the n8n
  workflow. First choice for reading the file in.

## Background - Why this skill?

The n8n workflow `10v6Nbtf9Jq44GQ4` ("Teams Meeting Minutes Automation") handles
this task automatically for all online meetings in the calendar, but does not
cover three cases:

1. **External VTT files** - e.g. forwarded transcripts from meetings in which
   the user was not the organizer.
2. **Manual adjustment** - when the auto-generated output needs another pass
   before it goes out.
3. **Iterative work** - when the user needs several rounds of adjustment (tone,
   granularity, additional sections).

This skill closes that gap while using the same parsing and structuring logic as
the workflow, extended with IBCS compliance and the house email style.
