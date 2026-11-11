# Use stdlib HTMLParser with explicit removal rules

Status: accepted (generated, pending human review)

## Context

The utility must extract main content without heavy dependencies. Existing readability ports depend on lxml and are hard to pin for deterministic counts.

## Decision

Implement a pure Python pipeline using `html.parser.HTMLParser`; define explicit removal categories (`tags`, `hidden`, `boilerplate`) with counts; select candidate via a documented density score.

## Consequences

Positive: no runtime dependencies, deterministic output, clear removal accounting. Negative: does not emulate full browser layout, so some complex pages may yield imperfect candidates; document as out of scope.
