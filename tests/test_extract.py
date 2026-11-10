"""Acceptance tests for html_main_content.extract."""

import pytest

from html_main_content import ExtractError, extract

EXAMPLE = (
    '<html><head><title>T</title></head><body><nav><a href="/">Home</a></nav>'
    "<article><h1>Title</h1><p>First paragraph.</p><p>Second one.</p></article>"
    "<footer>(c) 2026</footer></body></html>"
)


def test_example_page_title_and_text():
    result = extract(EXAMPLE)
    assert result.title == "T"
    assert result.text == "Title\n\nFirst paragraph.\n\nSecond one."
    assert result.blocks == ("Title", "First paragraph.", "Second one.")


def test_example_page_removed_counts():
    result = extract(EXAMPLE)
    assert result.removed == {"boilerplate": 0, "hidden": 0, "tags": 2}


def test_density_fallback_without_article_or_main():
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
        "<script>var secret = 1;</script>"
        "<style>.x{}</style>"
        "<form><input><button>Send</button></form>"
        "<p>Visible</p>"
        "</article>"
    )
    result = extract(html)
    assert result.text == "Visible"
    for removed_text in ("cookies", "secret", "Send"):
        assert removed_text not in result.text
    assert result.removed["tags"] == 3  # script, style, form
    assert result.removed["hidden"] == 3  # hidden, aria-hidden, style
    assert result.removed["boilerplate"] == 1  # cookie-banner


def test_whitespace_entities_br_and_pre():
    assert extract("<p>Hello <b>world</b>\n  again &amp; more</p>").text == (
        "Hello world again & more"
    )
    assert extract("<p>line1<br>line2</p>").text == "line1\nline2"
    assert extract("<pre>  a  b\n c </pre>").text == "  a  b\n c "


def test_no_content_on_empty_body():
    with pytest.raises(ExtractError) as excinfo:
        extract("<html><head><title>x</title></head><body></body></html>")
    assert excinfo.value.code == "no_content"


def test_input_too_large_limit():
    with pytest.raises(ExtractError) as excinfo:
        extract("a" * 5_000_001)
    assert excinfo.value.code == "input_too_large"

    # Exactly max_bytes is accepted; such input simply has no blocks.
    with pytest.raises(ExtractError) as excinfo:
        extract("a" * 5_000_000)
    assert excinfo.value.code == "no_content"


def test_too_deep_limit():
    with pytest.raises(ExtractError) as excinfo:
        extract("<div>" * 513 + "x" + "</div>" * 513)
    assert excinfo.value.code == "too_deep"

    accepted = "<div>" * 511 + "<p>x</p>" + "</div>" * 511
    assert extract(accepted).text == "x"


def test_two_articles_uses_scoring():
    html = (
        "<article><p>Short.</p></article>"
        "<article><p>" + "a" * 30 + "</p><p>" + "b" * 30 + "</p></article>"
    )
    result = extract(html)
    assert result.text == "a" * 30 + "\n\n" + "b" * 30


def test_main_inside_body():
    assert extract("<body><main><p>Main content</p></main></body>").text == "Main content"


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


def test_boilerplate_tokens_split_on_underscore():
    html = (
        '<div class="header_ad"><p>Buy now!</p></div>'
        '<div id="ad_slot"><p>Advert</p></div>'
        "<article><p>Body text</p></article>"
    )
    result = extract(html)
    assert result.text == "Body text"
    assert result.removed["boilerplate"] == 2


def test_class_shadow_not_boilerplate():
    result = extract('<div class="shadow"><p>Keep me</p></div>')
    assert result.text == "Keep me"
    assert result.removed["boilerplate"] == 0


def test_uppercase_tags():
    html = (
        "<HTML><HEAD><TITLE>Test</TITLE></HEAD><BODY><ARTICLE><P>Hello</P></ARTICLE></BODY></HTML>"
    )
    result = extract(html)
    assert result.title == "Test"
    assert result.text == "Hello"


def test_nested_blocks_are_emitted_once():
    quote = "This is a long quote that must not disappear."
    html = f"<article><blockquote><p>{quote}</p></blockquote></article>"
    assert extract(html).text == quote

    item = "This is a long list item that must not disappear."
    html = f"<article><ul><li><p>{item}</p></li></ul></article>"
    assert extract(html).text == item

    html = "<article><table><tr><td><p>cell text</p></td></tr></table></article>"
    assert extract(html).text == "cell text"


def test_unclosed_paragraphs_nested_by_parser():
    assert extract("<article><p>a<p>b</article>").text == "a\n\nb"


def test_header_inside_article_is_kept():
    html = "<article><header><h1>Headline</h1></header><p>Body</p></article>"
    result = extract(html)
    assert result.text == "Headline\n\nBody"
    assert result.removed["tags"] == 0
