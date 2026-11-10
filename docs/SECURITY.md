# Security

`html-main-content` parses untrusted HTML as text and does not execute JavaScript or fetch external resources. It is a text extractor, not an HTML sanitizer.

## Defended

- Input size: `extract()` raises `ExtractError('input_too_large')` when `len(html.encode('utf-8')) > max_bytes`; the default `max_bytes` is 5,000,000 UTF-8 bytes.
- Nesting depth: parsing raises `ExtractError('too_deep')` when a start tag would exceed `max_depth`; the default `max_depth` is 512 elements.
- Script and style text: `script`, `style`, `noscript`, `template`, `iframe`, `svg`, `canvas`, `form`, `button`, `select`, `input`, `nav`, `aside`, and `header`/`footer` outside `article`/`main` are removed before block extraction.
- Hidden and boilerplate text: elements matching the hidden or boilerplate rules are removed and counted.
- No JavaScript execution, no network requests and no external resource loading by the library.
- Logging uses `logging.getLogger(__name__)` with a `NullHandler`; the library does not configure global logging or write files.

## Not defended

- Output escaping: `Extracted.text` and `Extracted.blocks` are plain text and are not HTML-escaped. Callers must escape them before inserting into HTML.
- Charset detection: the API expects `str`; decoding bytes is the caller's responsibility. The CLI reads files as UTF-8 with `errors='replace'`.
- CSS: only inline `style` containing `display:none` or `visibility:hidden` is considered. External stylesheets are ignored.
- CPU time: size and depth limits bound input, but there is no separate timeout or CPU quota.
- JavaScript-rendered content, Markdown conversion, images and captions are out of scope.
