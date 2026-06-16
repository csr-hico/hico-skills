from __future__ import annotations

from hico_skills.auth import identity_from_headers, is_allowed
from hico_skills.models import Identity


def test_headers_parsed_case_insensitive():
    ident = identity_from_headers(
        {"X-Authentik-Username": "jdoe", "X-Authentik-Groups": "HICO, dev "}
    )
    assert ident.username == "jdoe"
    assert ident.groups == ("HICO", "dev")


def test_absent_headers_anonymous():
    ident = identity_from_headers({})
    assert ident.username is None
    assert ident.groups == ()


def test_is_allowed_open_when_no_required_group():
    assert is_allowed(Identity("jdoe", ()), None) is True
    assert is_allowed(Identity("jdoe", ()), "") is True


def test_is_allowed_membership():
    assert is_allowed(Identity("jdoe", ("HICO",)), "HICO") is True
    assert is_allowed(Identity("jdoe", ("dev",)), "HICO") is False
