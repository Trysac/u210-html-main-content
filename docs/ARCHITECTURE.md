# Architecture

## Overview

`html-main-content` extracts the main textual content of an HTML page. It uses only Python's standard library (`html.parser`) and has no runtime dependencies.

## Pipeline

1. **Parse** with `HTMLParser(convert_charrefs=True)` into a light element tree. Void elements are not pushed on the stack. Mismatched end tags close up to the nearest open match. If a start tag would make `len(stack)` reach `max_depth`, parsing raises `ExtractError('too_deep')`.
2. **Remove** subtrees and count removals under `removed['tags']`, `removed['hidden']` and `removed['boilerplate']`.
   - `tags`: `script`, `style`, `noscript`, `template`, `iframe`, `svg`, `canvas`, `form`, `button`, `select`, `input`, `nav`, `aside`, and `header`/`footer` unless inside `article` or `main`.
   - `hidden`: `hidden` attribute, `aria-hidden='true'`, or a style attribute containing `display:none` or `visibility:hidden` after removing whitespace and lowercasing.
   - `boilerplate`: role `navigation`, `banner`, `contentinfo` or `complementary`, or a class/id token equal to one of `nav`, `menu`, `footer`, `sidebar`, `comment`, `comments`, `share`, `social`, `advert`, `ad`, `ads`, `promo`, `cookie`, `banner`, `related`, `breadcrumb`, `newsletter`, `popup`. Tokens are split on whitespace, `-` and `_` and compared whole after lowercasing.
3. **Choose candidate**: the only `article` if exactly one exists, else the only `main`, else the highest-scoring element among `div`, `section`, `td` and `body`. Ties go to the first in document order. Score is the sum of text lengths of direct `p`, `pre` and `blockquote` children whose text is at least 25 characters, multiplied by `(1 - link_chars / text_chars)`; an element with no text scores 0. If no such element exists, it falls back to the articles or mains, then the root when it has element children, otherwise raises `no_content`.
4. **Extract blocks** from the candidate: each `h1`-`h6`, `p`, `li`, `pre`, `blockquote`, `th` and `td` descendant, plus loose text directly inside the candidate, in document order. Nested blocks are not duplicated inside a parent block. Inline whitespace is collapsed to one space and stripped, except `pre`, whose text is kept verbatim. `br` becomes a newline; empty blocks are dropped.
5. **Assemble** `Extracted(title, text, blocks, removed)`, where `text` is `blocks` joined with two newlines and `title` is the first `title` element with whitespace collapsed, or `''` when absent.

## Error handling

`ExtractError` carries a `code` attribute. Codes are `input_too_large` when `len(html.encode('utf-8')) > max_bytes`, `too_deep` when nesting exceeds `max_depth`, and `no_content` when no text blocks are produced. Defaults are `max_bytes=5_000_000` and `max_depth=512`.

## CLI

`python -m html_main_content [--json] file.html` reads UTF-8 with `errors='replace'`. It exits 0 on success, 1 when `extract` raises `no_content`, and 2 for usage or file I/O errors. `--json` prints an object with sorted keys: `removed`, `text` and `title`.
