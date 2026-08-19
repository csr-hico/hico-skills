from __future__ import annotations

from hico_skills.auth import identity_from_headers


def test_headers_parsed_case_insensitive():
    ident = identity_from_headers(
        {"X-Forwarded-Preferred-Username": "jdoe@hico.test", "X-Forwarded-Groups": "HICO, dev "}
    )
    assert ident.username == "jdoe@hico.test"
    assert ident.groups == ("HICO", "dev")


def test_email_fallback_when_no_preferred_username():
    ident = identity_from_headers({"X-Forwarded-Email": "jdoe@hico.test"})
    assert ident.username == "jdoe@hico.test"


def test_absent_headers_anonymous():
    ident = identity_from_headers({})
    assert ident.username is None
    assert ident.groups == ()
