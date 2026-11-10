"""Tests for html_main_content."""

import json
from pathlib import Path

import pytest

from html_main_content import ExtractError, extract
from html_main_content.__main__ import main


def test_extract_basic_article():
    html = (
        "<html><head><title>T</title></head><body>"
        '<nav><a href="/">Home</a></nav>'
        "<article><h1>Title</h1><p>First paragraph.</p><p>Second one.</p></article>"
        "<footer>(c) 2026</footer></body></html>"
    )
    result = extract(html)
    assert result.title == "T"
    assert result.text == "Title\n\nFirst paragraph.\n\nSecond one."
    assert result.blocks == ("Title", "First paragraph.", "Second one.")
    assert result.removed == {"boilerplate": 0, "hidden": 0, "tags": 2}


def test_scoring_without_article_or_main():
    html = (
        '<body><div class="x"><p>Short.</p></div>'
        '<div class="y">'
        "<p>This is the first long paragraph of the story.</p>"
        "<p>And here is the second long paragraph.</p>"
        "</div></body>"
    )
    result = extract(html)
    assert result.text == (
        "This is the first long paragraph of the story.\n\nAnd here is the second long paragraph."
    )


def test_removals_inside_article():
    html = (
        "<article>"
        '<div class="cookie-banner"><p>We use cookies to improve this site for you.</p></div>'
        "<p hidden>secret</p>"
        '<p aria-hidden="true">x</p>'
        '<p style="display: none">y</p>'
        "<script>var a=1;</script>"
        "<style>.x{}</style>"
        "<form><input><button>Send</button></form>"
        "<p>Visible</p>"
        "</article>"
    )
    result = extract(html)
    assert result.text == "Visible"
    assert result.removed["tags"] == 3  # script style form
    assert result.removed["hidden"] == 3  # hidden, aria-hidden, style
    assert result.removed["boilerplate"] == 1  # cookie-banner


def test_whitespace_normalization_and_entities():
    html = "<p>Hello <b>world</b>\n  again &amp; more</p>"
    result = extract(html)
    assert result.text == "Hello world again & more"

    html_br = "<p>line1<br>line2</p>"
    assert extract(html_br).text == "line1\nline2"

    html_pre = "<pre>  a  b\n c </pre>"
    assert extract(html_pre).text == "  a  b\n c "


def test_no_content():
    with pytest.raises(ExtractError) as excinfo:
        extract("<html><head><title>x</title></head><body></body></html>")
    assert excinfo.value.code == "no_content"


def test_input_too_large_and_accepted():
    with pytest.raises(ExtractError) as excinfo:
        extract("a" * 5_000_001)
    assert excinfo.value.code == "input_too_large"

    with pytest.raises(ExtractError) as excinfo:
        extract("a" * 5_000_000)
    assert excinfo.value.code == "no_content"


def test_too_deep():
    html = "<div>" * 513 + "x" + "</div>" * 513
    with pytest.raises(ExtractError) as excinfo:
        extract(html)
    assert excinfo.value.code == "too_deep"


def test_two_articles_uses_scoring():
    html = (
        "<article><p>Short.</p></article>"
        "<article><p>" + "a" * 30 + "</p><p>" + "b" * 30 + "</p></article>"
    )
    result = extract(html)
    assert result.text == "a" * 30 + "\n\n" + "b" * 30


def test_main_inside_body():
    html = "<body><main><p>Main content</p></main></body>"
    result = extract(html)
    assert result.text == "Main content"


def test_table_layout_td_wins():
    html = (
        "<table><tr><td><p>Short.</p></td>"
        "<td><p>" + "c" * 40 + "</p><p>" + "d" * 40 + "</p></td></tr></table>"
    )
    result = extract(html)
    assert result.text == "c" * 40 + "\n\n" + "d" * 40


def test_boilerplate_token_header_ad():
    html = '<div class="header-ad"><p>Buy now!</p></div><div><p>Real article</p></div>'
    result = extract(html)
    assert result.text == "Real article"
    assert result.removed["boilerplate"] == 1


def test_class_shadow_not_boilerplate():
    html = '<div class="shadow"><p>Keep me</p></div>'
    result = extract(html)
    assert result.text == "Keep me"
    assert result.removed["boilerplate"] == 0


def test_uppercase_tags():
    html = (
        "<HTML><HEAD><TITLE>Test</TITLE></HEAD><BODY><ARTICLE><P>Hello</P></ARTICLE></BODY></HTML>"
    )
    result = extract(html)
    assert result.title == "Test"
    assert result.text == "Hello"


def test_cli_text(tmp_path: Path):
    html = "<article><p>Hello CLI</p></article>"
    file = tmp_path / "page.html"
    file.write_text(html, encoding="utf-8")
    exit_code = main([str(file)])
    assert exit_code == 0


def test_cli_json(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
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
    assert set(data["removed"].keys()) == {"tags", "hidden", "boilerplate"}


def test_cli_no_content(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    file = tmp_path / "empty.html"
    file.write_text("<html><body></body></html>", encoding="utf-8")
    exit_code = main([str(file)])
    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert captured.err == ""


def test_cli_missing_file(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    missing = tmp_path / "missing.html"
    exit_code = main([str(missing)])
    captured = capsys.readouterr()
    assert exit_code == 2
    assert "error: cannot read" in captured.err
