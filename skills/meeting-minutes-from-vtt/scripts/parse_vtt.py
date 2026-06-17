#!/usr/bin/env python3
"""
VTT-Parser fuer Microsoft-Teams-Transkripte.

Portiert 1:1 die Logik aus dem n8n-Workflow "Teams Meeting Minutes Automation"
(ID 10v6Nbtf9Jq44GQ4), Node "Prepare Transcript".

Verwendung:
    python parse_vtt.py <pfad/zur/datei.vtt>

Ausgabe (auf stdout):
    Eine JSON-Struktur mit:
      - clean_transcript: bereinigter Text als "Speaker: Aussage"-Zeilen
      - language: "de" oder "en"
      - language_name: "Deutsch" oder "English"
      - speakers: Liste der erkannten Sprecher
      - utterance_count: Anzahl der Aeusserungen
"""

import json
import re
import sys
from pathlib import Path


def parse_vtt(vtt_text: str) -> dict:
    """Wandelt rohen VTT-Inhalt in eine "Speaker: Aussage"-Struktur um.

    Die Logik folgt dem n8n-Workflow:
    - WEBVTT-Header, Timestamps und Cue-Marker werden uebersprungen
    - <v Sprecher>...</v>-Tags markieren neue Sprecher
    - Folgezeilen ohne Tag werden dem aktuellen Sprecher zugeordnet
    - Innere HTML-Tags werden entfernt
    """
    utterances = []
    speaker = ""
    buffer = ""

    speaker_re = re.compile(r"^<v ([^>]+)>(.*?)(?:</v>)?$")
    timestamp_re = re.compile(r"^\d{2}:\d{2}")
    inner_tag_re = re.compile(r"<[^>]*>")

    for raw in vtt_text.split("\n"):
        line = raw.strip()
        if not line or line == "WEBVTT":
            continue
        if timestamp_re.match(line) or "-->" in line:
            continue

        m = speaker_re.match(line)
        if m:
            if speaker and buffer:
                utterances.append(f"{speaker}: {buffer.strip()}")
            speaker = m.group(1)
            buffer = inner_tag_re.sub("", m.group(2))
        elif speaker:
            buffer += " " + inner_tag_re.sub("", line)

    if speaker and buffer:
        utterances.append(f"{speaker}: {buffer.strip()}")

    clean_transcript = "\n".join(utterances) or "(Kein lesbarer Transkriptinhalt verfuegbar)"

    speakers = sorted({u.split(":", 1)[0] for u in utterances})

    language, language_name = detect_language(clean_transcript)

    return {
        "clean_transcript": clean_transcript,
        "language": language,
        "language_name": language_name,
        "speakers": speakers,
        "utterance_count": len(utterances),
    }


def detect_language(text: str) -> tuple[str, str]:
    """Erkennt Deutsch oder Englisch via Stopword-Zaehlung + Umlaute.

    Identische Logik wie im n8n-Workflow: Umlaute zaehlen doppelt,
    weil sie ein starkes Indiz fuer Deutsch sind.
    """
    sample = text.lower()[:10000]

    german_stopwords = re.compile(
        r"\b(und|oder|aber|nicht|auch|noch|schon|dann|wenn|weil|dass|sich|sind|"
        r"wird|werden|haben|hatte|muss|kann|wie|was|wer|wo|warum|ich|du|er|sie|"
        r"wir|ihr|das|der|die|den|dem|des|ein|eine|einen|einem|einer|ist|bin|"
        r"bist|hat|mit|von|zu|auf|fuer|für|bei|nach|aus|ueber|über|hier|dort|"
        r"heute|morgen|gestern|jetzt|also|doch)\b"
    )
    english_stopwords = re.compile(
        r"\b(the|and|or|but|not|also|still|already|then|when|because|that|"
        r"itself|are|will|would|have|had|must|can|how|what|who|where|why|"
        r"this|is|am|has|with|from|on|for|at|after|out|about|of|in|by|as|"
        r"so|here|there|today|tomorrow|yesterday|now|just|really)\b"
    )
    umlauts = re.compile(r"[äöüß]")

    de_count = len(german_stopwords.findall(sample)) + len(umlauts.findall(sample)) * 2
    en_count = len(english_stopwords.findall(sample))

    if de_count > en_count:
        return "de", "Deutsch"
    return "en", "English"


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python parse_vtt.py <path/to/file.vtt>", file=sys.stderr)
        return 1

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        return 1

    vtt_text = path.read_text(encoding="utf-8")
    result = parse_vtt(vtt_text)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
