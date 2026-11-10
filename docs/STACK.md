# Stack

## Used

| Tool | Why |
|---|---|
| Python >= 3.10 | The code uses PEP 604 annotations such as `str | None` and built-in generics. |
| Standard library | Runtime code uses `html.parser`, `dataclasses`, `logging`, `re`, `collections.abc`, `typing`, `argparse`, `json` and `sys`; there are no runtime dependencies. |
| pytest | Tests exist in `tests/test_extract.py` and `tests/test_cli.py`. |
| `py.typed` marker | The package includes `src/html_main_content/py.typed`. |

## Discarded

| Tool | Why not |
|---|---|
| lxml | Not used; parsing uses the standard-library `html.parser`. |
| Readability ports | Not used; this library has no lxml dependency, reports removal counts and uses a documented density score. |
| JavaScript rendering | Out of scope; the library parses only the supplied HTML string. |
