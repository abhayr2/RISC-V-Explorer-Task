"""
Tier 1: Instruction Set Parsing
- Loads instr_dict.json from the project root when available
- Falls back to the GitHub raw URL if the local file is missing
- Groups instructions by extension tag
- Prints summary table
- Lists instructions in multiple extensions
"""

import json
from collections import defaultdict
from pathlib import Path

import requests

INSTR_DICT_URL = (
    "https://raw.githubusercontent.com/rpsene/"
    "riscv-extensions-landscape/main/src/instr_dict.json"
)


def _load_local_instr_dict(local_path: Path) -> dict | None:
    """Return a local instruction dictionary when the file exists and is valid."""
    if not local_path.exists() or local_path.stat().st_size == 0:
        return None

    try:
        with local_path.open(encoding="utf-8") as file_handle:
            return json.load(file_handle)
    except json.JSONDecodeError:
        return None


def fetch_instr_dict() -> dict:
    """Load instr_dict.json from disk first, then fall back to GitHub."""
    local_path = Path(__file__).with_name("instr_dict.json")
    local_data = _load_local_instr_dict(local_path)
    if local_data is not None:
        print(f"  Loading instr_dict.json from {local_path.name}...")
        return local_data

    print("  Fetching instr_dict.json from GitHub...")
    resp = requests.get(INSTR_DICT_URL, timeout=30)
    resp.raise_for_status()
    return resp.json()


def group_by_extension(instr_dict: dict) -> dict:
    ext_map = defaultdict(list)
    for mnemonic, meta in instr_dict.items():
        tags = meta.get("extension", [])
        if isinstance(tags, str):
            tags = [tags]
        for tag in tags:
            ext_map[tag].append(mnemonic.upper())
    return dict(ext_map)


def find_multi_extension_instructions(instr_dict: dict) -> list:
    multi = []
    for mnemonic, meta in instr_dict.items():
        tags = meta.get("extension", [])
        if isinstance(tags, str):
            tags = [tags]
        if len(tags) > 1:
            multi.append((mnemonic.upper(), tags))
    return sorted(multi, key=lambda x: x[0])


def print_summary_table(ext_map: dict) -> None:
    print(f"\n{'Extension':<30} {'# Instructions':>14}  {'Example'}")
    print("-" * 60)
    for tag in sorted(ext_map):
        mnemonics = ext_map[tag]
        print(f"{tag:<30} {len(mnemonics):>14}  {mnemonics[0]}")


def run_tier1(instr_dict: dict = None) -> tuple:
    if instr_dict is None:
        instr_dict = fetch_instr_dict()

    ext_map = group_by_extension(instr_dict)
    multi   = find_multi_extension_instructions(instr_dict)

    print(f"\n=== Tier 1: Instruction Set Parsing ===")
    print(f"Total instructions : {len(instr_dict)}")
    print(f"Unique extensions  : {len(ext_map)}")
    print_summary_table(ext_map)

    print(f"\n=== Instructions in Multiple Extensions ({len(multi)}) ===")
    if multi:
        print(f"\n{'Mnemonic':<20} Extensions")
        print("-" * 60)
        for mnemonic, tags in multi:
            print(f"{mnemonic:<20} {', '.join(tags)}")
    else:
        print("  None found.")

    return ext_map, multi