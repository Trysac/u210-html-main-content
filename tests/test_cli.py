"""CLI tests for html_main_content.__main__."""

import json
from pathlib import Path

import pytest

from html_main_content.__main__ import main


def test_cli_prints_text(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    file = tmp_path / "page.html"
    file.write_text("<article><p>Hello CLI</p></article>", encoding="utf-8")
    exit_code = main([str(file)])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out == "Hello CLI\n"


def test_cli_json_sorted_keys(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    html = (
        "<html><head><title>JSON</title></head><body>"
        "<article><p>Content</p></article></body></html>"
    )
    file = tmp_path / "page.html"
    file.write_text(html, encoding="utf-8")
    exit_code = main(["--json", str(file)])
    captured = capsys.readouterr()
    assert exit_code == 0
    data = json.loads(captured.out)
    assert data["title"] == "JSON"
    assert data["text"] == "Content"
    assert data["removed"] == {"boilerplate": 0, "hidden": 0, "tags": 0}
    assert list(data) == sorted(data)


def test_cli_no_content_returns_one(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    file = tmp_path / "empty.html"
    file.write_text("<html><body></body></html>", encoding="utf-8")
    assert main([str(file)]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""


def test_cli_missing_file_returns_two(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    missing = tmp_path / "missing.html"
    assert main([str(missing)]) == 2
    captured = capsys.readouterr()
    assert "error: cannot read" in captured.err


def test_cli_usage_error_returns_two():
    with pytest.raises(SystemExit) as excinfo:
        main([])
    assert excinfo.value.code == 2
