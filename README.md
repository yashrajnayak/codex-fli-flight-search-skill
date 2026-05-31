# Codex Fli Flight Search Skill

A Codex skill for searching and comparing flights with [`fli`](https://github.com/punitarani/fli), a Python wrapper around Google Flights data.

The skill helps Codex:

- compare nearby departure and arrival airports
- include checked bags and carry-ons in searches
- filter by cabin, stops, airlines, and departure time windows
- parse `fli --format json` output into compact ranked options
- treat results as discovery and verify final fares before booking

## Install

Clone this repository and copy the skill folder into your Codex skills directory:

```bash
git clone https://github.com/yashrajnayak/codex-fli-flight-search-skill.git
mkdir -p ~/.codex/skills
cp -R codex-fli-flight-search-skill/fli-flight-search ~/.codex/skills/
```

Or install with Codex's skill installer by pointing at the nested skill path:

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo yashrajnayak/codex-fli-flight-search-skill \
  --path fli-flight-search
```

Restart Codex after installing the skill.

## Set Up Fli

Install `fli` with pipx:

```bash
pipx install flights
```

Or use a local checkout:

```bash
git clone https://github.com/punitarani/fli.git ~/src/fli
cd ~/src/fli
python3.10 -m venv .venv
.venv/bin/python -m pip install -e .
```

If you use a local checkout, set:

```bash
export FLI_REPO=~/src/fli
```

You can also pass the checkout path per command with `--fli-repo /path/to/fli`.

## Example

Ask Codex:

```text
Use fli to compare JFK, LGA, and EWR to Toronto on May 10 2026 with one checked bag.
```

Or run the helper directly:

```bash
python ~/.codex/skills/fli-flight-search/scripts/fli_search.py \
  --origin LGA --destination YYZ --date 2026-05-10 --bags 1 --limit 8
```

For a local checkout outside the default search paths:

```bash
python ~/.codex/skills/fli-flight-search/scripts/fli_search.py \
  --fli-repo "/path/to/fli" \
  --origin LGA --destination YYZ --date 2026-05-10 --bags 1 --limit 8
```

## Notes

`fli` results are best used for exploration. Always verify final fares, baggage rules, fare class, and booking details on Google Flights or the airline site before purchasing.

Real searches require network access to Google Flights. In sandboxed Codex sessions, rerun with approval if DNS or network access is blocked. The helper prints concise failures by default; add `--debug` when you need the full `fli` traceback.
