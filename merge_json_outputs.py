#!/usr/bin/env python3
"""Merge generated JSON outputs into a single file per category directory.

Usage:
    python merge_json_outputs.py                  # merge under data/output
    python merge_json_outputs.py --root other_dir # custom root directory

Each immediate subdirectory under the root is treated as a category directory.
All JSON files within a category are loaded and combined into a single list that
is written back to `<category>/<category>_merged.json`.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List


def collect_json_files(category_dir: Path) -> List[Path]:
    """Return JSON files in the category directory sorted by name."""
    files = [
        path
        for path in category_dir.glob("*.json")
        if path.is_file() and not path.name.endswith("_merged.json")
    ]
    return sorted(files, key=lambda p: p.name.lower())


def merge_category(category_dir: Path) -> Path:
    """Merge all JSON files in a category directory into a single file."""
    json_files = collect_json_files(category_dir)
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

    output_path = category_dir / f"{category_dir.name}_merged.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(merged_data, handle, ensure_ascii=False, indent=2)

    return output_path


def merge_outputs(root: Path) -> int:
    """Merge JSON outputs for every category found under the root directory."""
    if not root.exists() or not root.is_dir():
        print(f"❌ Root directory not found: {root}")
        return 1

    category_dirs = [d for d in sorted(root.iterdir()) if d.is_dir()]
    if not category_dirs:
        print(f"❌ No category directories found under {root}")
        return 1

    merged_any = False
    for category_dir in category_dirs:
        try:
            merged_file = merge_category(category_dir)
        except ValueError as error:
            print(f"❌ {error}")
            return 1

        if merged_file:
            merged_any = True
            print(f"✅ Merged {category_dir.name} → {merged_file}")
        else:
            print(f"⚠️  No JSON files found in {category_dir}")

    if not merged_any:
        print("⚠️  No JSON files were merged")
        return 1

    print("\n✅ All available categories merged successfully")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("data/output"),
        help="Root directory containing category subdirectories (default: data/output)",
    )
    return parser


def main(argv: List[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return merge_outputs(args.root)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

