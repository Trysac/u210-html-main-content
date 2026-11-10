"""Command-line interface for html_main_content."""

from __future__ import annotations

import argparse
import json
import sys

from html_main_content import ExtractError, extract


def main(argv: list[str] | None = None) -> int:
    """Run the CLI and return an exit code."""
    parser = argparse.ArgumentParser(
        prog="html-main-content",
        description="Extract the main content of an HTML file as clean text blocks.",
    )
    parser.add_argument("file", help="HTML file to parse (UTF-8)")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Output JSON")
    args = parser.parse_args(argv)

    try:
        with open(args.file, encoding="utf-8", errors="replace") as f:
            html = f.read()
    except OSError:
        print(f"error: cannot read {args.file}", file=sys.stderr)
        return 2

    try:
        result = extract(html)
    except ExtractError as exc:
        if exc.code == "no_content":
            return 1
        print(f"error: {exc.code}", file=sys.stderr)
        return 2

    if args.as_json:
        print(
            json.dumps(
                {
                    "removed": dict(result.removed),
                    "text": result.text,
                    "title": result.title,
                },
                sort_keys=True,
            )
        )
    else:
        print(result.text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
