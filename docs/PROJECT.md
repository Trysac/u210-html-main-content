# Project record

## Objective

Extract the main content of an HTML page as clean text blocks: drop navigation, ads, hidden and boilerplate elements, then pick the article by structure or text density.

## Scope

- In scope: the public API `extract()`, `Extracted` and `ExtractError`, the CLI in `html_main_content.__main__`, the removal rules and density scoring described in [ARCHITECTURE.md](ARCHITECTURE.md).
- Runtime code uses only the Python standard library; there are no runtime dependencies.

## Out of scope

- JavaScript-rendered pages.
- Markdown conversion.
- Images and captions.
- Charset detection from bytes.

## Timeline

| Date | Event |
|---|---|
| 2026 | Repository created from the factory utility template. |

## Effort metrics

| Metric | Value |
|---|---|
| Tokens (input / output) | 761028 / 85306 |
| Hours (human) | pending measurement |
| Cost (USD) | 0.1132 |

## Factory run u210 (measured from API usage)

| Date (UTC) | Phase | Model | Batch | Input | Output | Cache write | Cache read | Cost (USD) |
|---|---|---|---|---|---|---|---|---|
| 2026-11-10 | generation | deepseek-v4-pro | yes | 1730 | 24264 | 0 | 3200 | 0.0493 |
| 2026-11-10 | fix-1 | deepseek-flash | no | 26773 | 12835 | 0 | 307072 | 0.0126 |
| 2026-11-10 | audit | deepseek-flash | no | 10345 | 17684 | 0 | 74624 | 0.0124 |
| 2026-11-10 | fix-2 | deepseek-flash | no | 9122 | 8026 | 0 | 123776 | 0.0066 |
| 2026-11-10 | threat-model | deepseek-flash | no | 19511 | 6592 | 0 | 79744 | 0.0071 |
| 2026-11-10 | docs | deepseek-flash | no | 104875 | 15905 | 0 | 256 | 0.0253 |

Total: $0.1132. Prices: deepseek line, as measured by its adapter. Providers serve the current version of each model id, so the date tells which version answered; versions, launch stages and price sources per line are in the factory's model register (docs/MODELS.md).
