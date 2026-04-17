"""
RISC-V Instruction Set Explorer
Entry point — runs Tier 1, Tier 2, and Tier 3 in sequence.
"""

from tier1_parser import fetch_instr_dict, run_tier1
from tier2_crossref import run_tier2
from tier3_graph import run_tier3


def main() -> None:
    print("=" * 60)
    print("  RISC-V Instruction Set Explorer")
    print("=" * 60)

    # ── Tier 1 ─────────────────────────────────────────────────
    instr_dict = fetch_instr_dict()
    ext_map, multi = run_tier1(instr_dict)

    # ── Tier 2 ─────────────────────────────────────────────────
    run_tier2(ext_map)          # clones ISA manual to a temp dir internally

    # ── Tier 3 ─────────────────────────────────────────────────
    run_tier3(ext_map)

    print("\nDone.")


if __name__ == "__main__":
    main()