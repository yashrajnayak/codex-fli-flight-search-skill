#!/usr/bin/env python3
"""Run fli flight searches and print compact ranked results."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


KNOWN_REPOS = [
    Path("~/src/fli").expanduser(),
    Path("~/fli").expanduser(),
]


def find_repo() -> Path | None:
    env_repo = os.environ.get("FLI_REPO")
    candidates: list[Path] = []
    if env_repo:
        candidates.append(Path(env_repo))
    cwd = Path.cwd()
    candidates.extend([cwd, cwd / "fli"])
    candidates.extend(parent / "fli" for parent in cwd.parents)
    candidates.extend(KNOWN_REPOS)
    for candidate in candidates:
        if (candidate / "fli" / "cli" / "main.py").exists():
            return candidate
    return None


def build_base_command(repo: Path | None) -> tuple[list[str], dict[str, str]]:
    env = os.environ.copy()
    if repo:
        python = repo / ".venv" / "bin" / "python"
        if not python.exists():
            raise SystemExit(f"Found fli repo at {repo}, but {python} does not exist.")
        env["PYTHONPATH"] = str(repo)
        return [str(python), "-m", "fli.cli.main"], env
    executable = shutil.which("fli")
    if executable:
        return [executable], env
    raise SystemExit("Could not find fli. Set FLI_REPO=/path/to/fli or install `flights`.")


def extract_json(output: str) -> dict:
    start = output.find("{")
    end = output.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in fli output.")
    return json.loads(output[start : end + 1])


def format_duration(minutes: int | float | None) -> str:
    if minutes is None:
        return ""
    minutes = int(minutes)
    hours, mins = divmod(minutes, 60)
    return f"{hours}h {mins:02d}m" if hours else f"{mins}m"


def summarize(data: dict, limit: int) -> str:
    flights = [f for f in data.get("flights", []) if f.get("price", 0) > 0]
    flights.sort(key=lambda f: (f.get("price", 10**18), f.get("stops", 99), f.get("duration", 10**9)))
    lines = []
    query = data.get("query", {})
    lines.append(
        f"{query.get('origin')} -> {query.get('destination')} on {query.get('departure_date')} "
        f"({len(flights)} priced results)"
    )
    lines.append("price | stops | duration | flight | depart -> arrive")
    lines.append("--- | --- | --- | --- | ---")
    for flight in flights[:limit]:
        legs = flight.get("legs", [])
        first = legs[0] if legs else {}
        last = legs[-1] if legs else {}
        airline = first.get("airline", {}).get("code", "")
        number = first.get("flight_number", "")
        flight_label = f"{airline}{number}" if airline or number else ""
        if len(legs) > 1:
            flight_label += f" +{len(legs) - 1}"
        price = f"{flight.get('currency', '')} {flight.get('price', '')}".strip()
        lines.append(
            f"{price} | {flight.get('stops', '')} | {format_duration(flight.get('duration'))} | "
            f"{flight_label} | {first.get('departure_time', '')} -> {last.get('arrival_time', '')}"
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--origin", required=True)
    parser.add_argument("--destination", required=True)
    parser.add_argument("--date", required=True, help="Departure date YYYY-MM-DD")
    parser.add_argument("--return-date")
    parser.add_argument("--bags", type=int, default=0)
    parser.add_argument("--carry-on", action="store_true")
    parser.add_argument("--cabin", default="ECONOMY")
    parser.add_argument("--stops", default="ANY")
    parser.add_argument("--sort", default="CHEAPEST")
    parser.add_argument("--time")
    parser.add_argument("--airlines", nargs="*")
    parser.add_argument("--currency", default="USD")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--raw-json", action="store_true")
    args = parser.parse_args()

    repo = find_repo()
    base_cmd, env = build_base_command(repo)
    cmd = [
        *base_cmd,
        "flights",
        args.origin.upper(),
        args.destination.upper(),
        args.date,
        "--format",
        "json",
        "--sort",
        args.sort,
        "--class",
        args.cabin,
        "--stops",
        args.stops,
        "--currency",
        args.currency,
    ]
    if args.return_date:
        cmd.extend(["--return", args.return_date])
    if args.bags:
        cmd.extend(["--bags", str(args.bags)])
    if args.carry_on:
        cmd.append("--carry-on")
    if args.time:
        cmd.extend(["--time", args.time])
    if args.airlines:
        cmd.append("--airlines")
        cmd.extend(code.upper() for code in args.airlines)

    proc = subprocess.run(
        cmd,
        cwd=str(repo) if repo else None,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if proc.returncode != 0:
        sys.stderr.write(proc.stdout)
        return proc.returncode
    data = extract_json(proc.stdout)
    if args.raw_json:
        print(json.dumps(data, indent=2))
    else:
        print(summarize(data, args.limit))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
