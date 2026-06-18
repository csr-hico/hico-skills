"""Hand-curated DE/EN synonym groups for query expansion. Tiny on purpose.

Each inner list is a set of interchangeable terms. `search.py` folds every term with the same
normalization it applies to queries (casefold + diacritic strip), so write them naturally here -
umlauts and case are handled. Keep terms single words (the tokenizer splits on non-alphanumerics).

Grow this from the zero-hit queries the search telemetry logs - not from imagination.
"""

from __future__ import annotations

RAW_GROUPS: list[list[str]] = [
    [
        "login",
        "authenticate",
        "authentication",
        "auth",
        "session",
        "anmelden",
        "anmeldung",
        "einloggen",
    ],
    ["logout", "signout", "abmelden"],
    ["mail", "email", "nachricht", "message"],
    ["run", "launch", "start", "starten", "ausführen", "execute"],
    ["status", "progress", "fortschritt", "state", "zustand"],
    ["summary", "summarize", "minutes", "protokoll", "zusammenfassung", "zusammenfassen"],
    ["workflow", "ablauf", "pipeline"],
    ["create", "add", "new", "erstellen", "anlegen", "hinzufügen"],
    ["delete", "remove", "löschen", "entfernen"],
    ["update", "edit", "change", "ändern", "bearbeiten"],
    ["secret", "credential", "credentials", "password", "passwort", "geheimnis", "token"],
    ["rotate", "rotation", "rotieren", "renew", "erneuern"],
    ["search", "find", "lookup", "suchen", "finden"],
    ["transcript", "vtt", "transkript"],
    ["meeting", "besprechung", "termin"],
    ["commit", "checkin"],
    ["review", "audit", "check", "prüfen"],
]
