from __future__ import annotations

from hico_skills.config import load_settings


def test_version_label_truncates_sha_and_includes_build_time():
    s = load_settings({"GIT_SHA": "abcdef1234567890", "BUILD_TIME": "2026-06-18 09:30 UTC"})
    assert s.version_label == "abcdef1, 2026-06-18 09:30 UTC"


def test_version_label_defaults_to_dev_with_start_time():
    s = load_settings({})
    assert s.git_sha == "dev"
    assert s.version_label.startswith("dev, ")  # build_time falls back to process start time
