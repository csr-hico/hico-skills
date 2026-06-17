---
name: IBCS-Mail
description: >
  Writes business emails in IBCS style: pyramidal from overview to detail, UPPERCASE headings,
  solution-oriented without drama, with explicit dates/times and clear responsibilities - as
  Outlook-ready plain text without Markdown. The email is written in the language of the user's
  prompt.
triggers:
  - write an email
  - draft an email
  - improve this email
  - email to the customer
  - schreib eine Mail
  - E-Mail aufsetzen
---

# IBCS-Mail

Write a business email in IBCS style. Ask briefly for any missing context (recipient, request,
facts, desired next steps) instead of inventing details. Output **only the finished email as plain
text** (see FORMATTING) - no commentary around it, unless the user asks for it.

**Language:** write the email in the **language of the user's prompt**. If the user writes the
request in German, write a German email; if in English, English; and so on. Translate the headings
and labels below into that language - but keep them UPPERCASE. The examples here are in English.

## Mindset
- Professional and solution-oriented: focus on solutions, even for problems.
- Proactive: state initiative and the next steps clearly.
- Phrased positively: avoid negative or dramatizing wording; offer constructive alternatives.
- Customer-friendly: tend the relationship, no blame.
- Transparent: name causes and measures clearly - no glossing over, no dramatizing.

## IBCS structure (general to specific)
1. Overview/summary first.
2. Detailed exposition in thematic blocks.
3. Concrete next steps at the end.
4. Avoid redundancy.
5. Dates ALWAYS explicit: not "Friday", but "Friday, 21 Oct 2025" (the recipient may read it later).
6. Times as "hh:mm" (point in time) or "hh:mm-hh:mm" (range). Include the time zone when relevant
   (e.g. CEST).

## Structure
**Salutation** - individual: `Hello Mr/Ms [last name],` · group: `Hello everyone,`. Always a comma.

**Opening** - 1-3 sentences giving context or a short summary.

**Body in thematic blocks**
- Headings ALWAYS in UPPERCASE, concise, followed ALWAYS by a line break (never continue on the
  same line).
- Move from general to specific; short to medium sentences.
- Lists with `-`, sub-points indented with a tab.
- Dates in parentheses, e.g. "(17 Oct 2025)", "(end of July 2025)".
- Technical details precise: thousands separators ("10,384 MB"), full versions
  ("31.34.8.0 (November 2024)"), full server names ("DEGRV-APP-PV017"), file names in quotes
  ("Server Sizing_BL.pdf").

**Next steps** - heading NEXT STEPS, a numbered list with the responsible party as a prefix:
```
1.  CUSTOMER: Take a VM snapshot by tomorrow (14 Oct 2025) 09:30.
2.  HICO: Back up, reinstall, restore the backup.
```
Assign responsibilities explicitly ("HICO:", "CUSTOMER:", "CUSTOMER & HICO:").

**Closing** - optional offer to help on complex topics + a short check-back
("Does this help?" / "Just let me know when you'd like to schedule this!").
Blank line before the sign-off.

**Sign-off** - `Best regards,` or `Kind regards,` on its own line, then `[Your name]`.

## Language (examples)
- instead of "The problem is..." → "We found the cause:"
- instead of "Unfortunately the database is full" → "Your database has reached its size limit"
- instead of "That's not possible" → "To solve this permanently, the following steps are needed:"
- For problems: describe the situation first, then the solution; immediate measure + long-term fix.
- Polite without overdoing it ("apologies for the late reply", "thank you for the constructive
  meeting").

## Avoid
Excessive bold/highlighting · negative or dramatizing language · blame · long nested sentences ·
informal/emotional phrasing · over-apologizing.

## Formatting (MS Outlook)
- NO Markdown (no `#`, `**`, etc.). Plain text only.
- Headings: simply UPPERCASE, no styling.
- Blank lines between all sections.
- Lists: a simple hyphen `-` or numbering `1.`, `2.`; sub-points with a tab.

## Mail types (skeletons)

USE the fitting skeleton, not all of them. Adapt the headings as needed and translate them into the
email's language.

### 1. Problem/incident report
```
<Salutation>

<Short summary: what is the problem?>

ISSUE AND CAUSE
<Technical details, precise but understandable>

IMMEDIATE MEASURE
<What has already been done?>

NEXT STEPS
<Numbered list with responsibilities>

<Offer to help>

Best regards,
[Your name]
```

### 2. Meeting summary
```
<Salutation>

<Thanks for the meeting + announce the summary>

POSITIVE FEEDBACK
<What went well?>

DISCUSSION POINTS [TOPIC]
- Point 1
- Point 2

[FURTHER TOPICS]
<More discussion points>

NEXT STEPS
1.  [RESPONSIBILITY]: [action]
2.  [RESPONSIBILITY]: [action]

Best regards,
[Your name]
```

### 3. Status update
```
<Salutation>

<Short status description>

Problem:
<Precise description>

Server: <name>
Version: <version>

Cause: <technical cause>

NEXT STEPS:
1.  [RESPONSIBILITY]: [action] [timeframe]
2.  [RESPONSIBILITY]: [action]

Best regards,
[Your name]
```

### 4. Request/information
```
<Salutation>

<Optional opening>

HEADING 1
<Information/explanation>

HEADING 2
<More information>

<Check-back whether it helps>

Best regards,
[Your name]
```
