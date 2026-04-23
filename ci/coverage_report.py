#!/usr/bin/env python3
"""Generate a coverage summary markdown table from Cobertura XML files.

Usage:
    python ci/coverage_report.py <version>:<path/to/cobertura.xml> ...

Each positional argument is a colon-separated pair of a label (e.g. the
Python version) and the path to a Cobertura-format XML coverage report.
The script reads the top-level ``line-rate`` attribute from each file,
formats it as a percentage, and prints a markdown table to stdout.
"""

import argparse
import sys
import xml.etree.ElementTree as ET


def parse_line_rate(xml_path: str) -> float:
    """Return the top-level line coverage rate (0–1) from a Cobertura XML file."""
    try:
        tree = ET.parse(xml_path)  # noqa: S314 — file is a trusted CI artifact
    except ET.ParseError as exc:
        raise SystemExit(f"Failed to parse {xml_path!r}: {exc}") from exc
    root = tree.getroot()
    try:
        return float(root.attrib["line-rate"])
    except (KeyError, ValueError) as exc:
        raise SystemExit(f"Missing or invalid 'line-rate' in {xml_path!r}: {exc}") from exc


def build_table(rows: list[tuple[str, float]]) -> str:
    lines = [
        "## Coverage Report",
        "",
        "| Python Version | Line Coverage |",
        "| :---: | :---: |",
    ]
    for version, rate in sorted(rows):
        pct = rate * 100
        badge = "✅" if pct >= 80 else "❌"
        lines.append(f"| {version} | {badge} {pct:.1f}% |")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Summarise Cobertura coverage reports into a GitHub step summary."
    )
    parser.add_argument(
        "entries",
        nargs="+",
        metavar="VERSION:XML_PATH",
        help="Colon-separated pair of a label and the path to a Cobertura XML file.",
    )
    args = parser.parse_args()

    rows: list[tuple[str, float]] = []
    for entry in args.entries:
        if ":" not in entry:
            print(f"Error: expected VERSION:PATH, got {entry!r}", file=sys.stderr)
            sys.exit(1)
        version, xml_path = entry.split(":", 1)
        rate = parse_line_rate(xml_path)
        rows.append((version, rate))

    table = build_table(rows)
    print(table)


if __name__ == "__main__":
    main()
