#!/usr/bin/env python3
"""Merge generated JSON outputs into a single file per section directory.

Usage:
    python merge_json_outputs.py                  # merge under data/output
    python merge_json_outputs.py --root other_dir # custom root directory

Each immediate subdirectory under the root is treated as a section directory.
All JSON files within a section are loaded and combined into a single list that
is written back to `<section>/<section>_merged.json`.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List


def collect_json_files(section_dir: Path) -> List[Path]:
    """Return JSON files in the section directory sorted by name."""
    files = [
        path
        for path in section_dir.glob("*.json")
        if path.is_file() and not path.name.endswith("_merged.json")
    ]
    return sorted(files, key=lambda p: p.name.lower())


def merge_section(section_dir: Path) -> Path:
    """Merge all JSON files in a section directory into a single file."""
    json_files = collect_json_files(section_dir)
    if not json_files:
        return None

    merged_data = []
    for json_file in json_files:
        try:
            with json_file.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
            merged_data.append(data)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Failed to parse {json_file}: {exc}") from exc

    output_path = section_dir / f"{section_dir.name}_merged.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(merged_data, handle, ensure_ascii=False, indent=2)

    return output_path


def merge_outputs(root: Path) -> int:
    """Merge JSON outputs for every section found under the root directory."""
    if not root.exists() or not root.is_dir():
        print(f"❌ Root directory not found: {root}")
        return 1

    section_dirs = [d for d in sorted(root.iterdir()) if d.is_dir()]
    if not section_dirs:
        print(f"❌ No section directories found under {root}")
        return 1

    merged_any = False
    for section_dir in section_dirs:
        try:
            merged_file = merge_section(section_dir)
        except ValueError as error:
            print(f"❌ {error}")
            return 1

        if merged_file:
            merged_any = True
            print(f"✅ Merged {section_dir.name} → {merged_file}")
        else:
            print(f"⚠️  No JSON files found in {section_dir}")

    if not merged_any:
        print("⚠️  No JSON files were merged")
        return 1

    print("\n✅ All available sections merged successfully")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("data/output"),
        help="Root directory containing section subdirectories (default: data/output)",
    )
    return parser


def main(argv: List[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return merge_outputs(args.root)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

