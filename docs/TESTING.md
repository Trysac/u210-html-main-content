# Testing

## Running

```sh
python -m pytest
```

## Policy

The repository contains pytest tests. They call the public API and the CLI and assert returned values, raised `ExtractError` codes and output. No coverage threshold or conformance tier is configured in the provided files.

## Tiers

There are no separate test tiers; both test files run in one pytest session.

## Layout

- `tests/test_extract.py`:
  - `test_example_page_title_and_text` checks the article example title and text.
  - `test_example_page_removed_counts` checks the `removed` mapping for that example.
  - `test_density_fallback_without_article_or_main` checks that the denser `div` is selected.
  - `test_removals_inside_article` checks that cookie-banner, hidden, aria-hidden, display-none, script, style and form content is absent.
  - `test_whitespace_entities_br_and_pre` checks whitespace collapse, entity decoding, `br` newlines and verbatim `pre` text.
  - `test_no_content_on_empty_body` checks `ExtractError.code == 'no_content'`.
  - `test_input_too_large_limit` checks 5_000_001 UTF-8 bytes raises `input_too_large` and 5_000_000 bytes is accepted.
  - A depth test checks nesting beyond 512 elements raises `too_deep`.
- `tests/test_cli.py`:
  - `test_cli_prints_text` checks `main(['page.html'])` prints text and returns 0.
  - `test_cli_json_sorted_keys` checks `main(['--json', 'page.html'])` prints an object with sorted keys.
  - `test_cli_no_content_returns_one` checks a page with no content returns 1.
  - `test_cli_missing_file_returns_two` checks a missing file returns 2 and reports the read error.
  - `test_cli_usage_error_returns_two` checks argument error returns 2.
