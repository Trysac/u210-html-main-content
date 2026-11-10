"""Behavior tests for the public API of html_main_content."""

from __future__ import annotations

import pytest

import html_main_content


def test_normalize_trims_and_lowercases() -> None:
    assert html_main_content.normalize("  Hello World ") == "hello world"


@pytest.mark.parametrize("value", ["", "   ", "\t\n"])
def test_normalize_rejects_blank_input(value: str) -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        html_main_content.normalize(value)


def test_version_is_semver() -> None:
    parts = html_main_content.__version__.split(".")
    assert len(parts) == 3
    assert all(part.isdigit() for part in parts)
