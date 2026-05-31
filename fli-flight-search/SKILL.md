---
name: fli-flight-search
description: Search and compare flights with the local `fli` Google Flights wrapper. Use when the user asks Codex to find flights, compare airports or dates, include baggage, filter by stops/cabin/airlines/time windows, look for cheaper nearby-airport alternatives, or monitor/structure flight-search options before final booking verification.
---

# Fli Flight Search

## Overview

Use `fli` for fast, repeatable, machine-readable Google Flights exploration. Treat results as discovery: verify final fares, fare class, baggage rules, and booking links on Google Flights or the airline site before purchase.

## Workflow

1. Clarify ambiguous city airports before searching. Common defaults:
   - New York: compare `JFK`, `LGA`, `EWR` when the user says "New York" and asks for cheaper alternatives.
   - Toronto: use `YYZ` unless the user says downtown/Billy Bishop; compare `YYZ` and `YTZ` when useful.
2. Include user constraints directly in the command:
   - Checked bag: `--bags 1` or `--bags 2`
   - Carry-on: `--carry-on`
   - Nonstop: `--stops NON_STOP`
   - Cabin in raw `fli`: `--class ECONOMY`, `PREMIUM_ECONOMY`, `BUSINESS`, or `FIRST`
   - Cabin in the helper script: `--cabin ECONOMY`, `PREMIUM_ECONOMY`, `BUSINESS`, or `FIRST`
   - Departure window: `--time 6-12`
   - Airlines: `--airlines AA DL AC`
3. Use JSON output for comparisons:

```bash
PYTHONPATH=. .venv/bin/python -m fli.cli.main flights JFK YYZ 2026-05-10 --bags 1 --format json --sort CHEAPEST
```

4. Ignore parser artifacts with `price` equal to `0.0` unless independently verified.
5. Summarize the top practical options, not the whole JSON. Prefer tables with route, airline/flight, departure/arrival, stops, duration, price, and caveats.
6. For nearby-airport questions, compare total trip value, not just airfare. Include likely ground-transfer time/cost when the alternate airport is outside the destination city, such as Buffalo for Toronto.

## Helper Script

Use `scripts/fli_search.py` when available to locate `fli`, run a search, parse JSON, drop zero-price artifacts, and print a concise table.

```bash
python ~/.codex/skills/fli-flight-search/scripts/fli_search.py \
  --origin LGA --destination YYZ --date 2026-05-10 --bags 1 --limit 8
```

Set `FLI_REPO=/path/to/fli` or pass `--fli-repo /path/to/fli` if the script cannot locate the checkout. The helper searches the current directory, parent directories, `~/src/fli`, and `~/fli`.

```bash
python ~/.codex/skills/fli-flight-search/scripts/fli_search.py \
  --fli-repo "/path/to/fli" \
  --origin LGA --destination YYZ --date 2026-05-10 --bags 1 --limit 8
```

Real searches require network access to Google Flights. In Codex sandboxes, retry with approval if DNS or network access fails. The helper prints concise errors by default; use `--debug` to show the full `fli` output and traceback.

## Setup Notes

Prefer an existing installation in this order:

1. `FLI_REPO` pointing at a cloned `punitarani/fli` repo with `.venv`.
2. A local checkout named `fli` in the workspace.
3. A shell executable from `pipx install flights`, invoked as `fli`.

If setup is needed:

```bash
git clone https://github.com/punitarani/fli.git
cd fli
/opt/homebrew/bin/python3.10 -m venv .venv || python3.10 -m venv .venv
.venv/bin/python -m pip install -e .
```

If `pypi.org` is blocked but `files.pythonhosted.org` works, use the repo's `uv.lock` direct wheel URLs as an install fallback, then run from source with `PYTHONPATH=.`. Prefer documenting that workaround in the final answer rather than editing system DNS or `/etc/hosts`.
