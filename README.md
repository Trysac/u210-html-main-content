# html-main-content

[![PyPI version](https://img.shields.io/pypi/v/trysac-html-main-content)](https://pypi.org/project/trysac-html-main-content/)
[![License: MIT](https://img.shields.io/pypi/l/trysac-html-main-content)](LICENSE)
[![CI](https://github.com/Trysac/u210-html-main-content/actions/workflows/ci.yml/badge.svg)](https://github.com/Trysac/u210-html-main-content/actions/workflows/ci.yml)

Extract the main content of an HTML page as clean text blocks: drop navigation, ads, hidden and boilerplate elements, then pick the article by structure or text density

## Problem

Describe in two or three sentences the concrete problem this utility solves, who hits it, and what
they do today without it. Replace this paragraph when the first real feature lands.

## Install

```sh
pip install trysac-html-main-content
# or
uv add trysac-html-main-content
```

Requires Python 3.10 or newer. No runtime dependencies.

## Usage

```python
import html_main_content

# normalize() trims surrounding whitespace and lower-cases the text.
print(html_main_content.normalize("  Hello World "))  # -> "hello world"

# Blank input is rejected explicitly instead of returning an empty string.
try:
    html_main_content.normalize("   ")
except ValueError as exc:
    print(f"rejected: {exc}")
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md) and [decisions](docs/decisions/)
- [Testing](docs/TESTING.md) and [security](docs/SECURITY.md)
- [Project record](docs/PROJECT.md) and [stack](docs/STACK.md)
- [Changelog](CHANGELOG.md) and [contributing guide](CONTRIBUTING.md)

## License

[MIT](LICENSE) (c) 2026 Miguel Gomez
