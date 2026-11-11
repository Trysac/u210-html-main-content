# html-main-content

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)](https://www.python.org/)

Extract the main content of an HTML page as clean text blocks: drop navigation, ads, hidden and boilerplate elements, then pick the article by structure or text density.

## Features

- Standard library only; no runtime dependencies.
- `extract()` returns an immutable `Extracted` with `title`, `text`, `blocks` and `removed`.
- Removal counts are reported under `removed['tags']`, `removed['hidden']` and `removed['boilerplate']`.
- Candidate selection uses a single `article`, else a single `main`, else density scoring among `div`, `section`, `td` and `body`.
- CLI entry point: `python -m html_main_content`.

## Installation

```bash
pip install trysac-html-main-content
```

Requires Python >= 3.10. The import name is `html_main_content`.

## Usage

```python
from html_main_content import extract

html = "<article><h1>Title</h1><p>Hello world.</p></article>"
result = extract(html)
print(result.title)  # ''
print(result.text)  # 'Title\n\nHello world.'
```

### Command line

```bash
python -m html_main_content page.html
python -m html_main_content --json page.html
```

The CLI reads the file as UTF-8 with `errors='replace'`. Exit codes: 0 success, 1 when `extract` raises `no_content`, 2 for usage or file I/O errors.

## Public API

`extract(html: str, *, max_bytes: int = 5_000_000, max_depth: int = 512) -> Extracted`

- `html`: HTML document or fragment as `str`.
- `max_bytes`: maximum size in UTF-8 bytes; input larger than this raises `ExtractError('input_too_large')`.
- `max_depth`: maximum element nesting depth; exceeding it raises `ExtractError('too_deep')`.
- `Extracted.title`: text of the first `title` element with whitespace collapsed, or `''` when absent.
- `Extracted.text`: blocks joined with two newlines.
- `Extracted.blocks`: tuple of text blocks in document order; nested blocks are not duplicated inside a parent block.
- `Extracted.removed`: mapping with the keys `tags`, `hidden` and `boilerplate`.

`ExtractError` has a `code` attribute. Codes are `input_too_large`, `too_deep` and `no_content`; `no_content` is raised when no text blocks are produced.

## Why not readability ports

Readability ports depend on lxml and do not report what they removed. This library parses with the standard-library `html.parser`, applies explicit removal rules with counts and uses a documented density score that tests can pin.

## How it works

1. Parse with `html.parser.HTMLParser(convert_charrefs=True)` into a light element tree.
2. Remove subtrees by tag, hidden-state and boilerplate rules and count each removal.
3. Choose the only `article`, else the only `main`, else the highest-scoring `div`, `section`, `td` or `body`.
4. Extract `h1`-`h6`, `p`, `li`, `pre`, `blockquote`, `th`, `td` and loose text directly inside the candidate.
5. Normalize inline whitespace, keep `pre` text verbatim, turn `br` into a newline and join blocks with two newlines.

## Development

```bash
python -m pytest
```

The tests are `tests/test_extract.py` and `tests/test_cli.py`. See [docs/SECURITY.md](docs/SECURITY.md) for the threat model.
