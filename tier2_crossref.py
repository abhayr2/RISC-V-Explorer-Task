"""
Tier 2: Cross-Reference with the ISA Manual
- Clones the riscv-isa-manual repo (shallow)
- Scans .adoc files for RISC-V extension names
- Cross-references against instr_dict.json extensions
- Reports matched / JSON-only / manual-only
"""

import re
import subprocess
import shutil
import tempfile
from pathlib import Path

ISA_MANUAL_URL = "https://github.com/riscv/riscv-isa-manual"

# Tight pattern — only matches real extension name shapes:
#   Z-extensions : Zba, Zicsr, Zifencei, Zbkb ...
#   Short caps   : M, F, D, A, H, V, S, N (single letter only)
#   RV prefixed  : RV32I, RV64GC ...
_EXT_PATTERN = re.compile(
    r'\b('
    r'Z[a-z][a-zA-Z0-9]{1,10}'   # Z-extensions (Zba, Zicsr, ...)
    r'|[MFDAHVSNCBPQ]'            # Known single-letter ISA extensions
    r'|RV(?:32|64)[A-Z]{1,6}'    # RV32I, RV64GC style
    r')\b'
)

# Known noise words that match our pattern but aren't extensions
_NOISE = {
    "zhang", "zero", "zeros", "zeroes", "zabrocki", "zandijk",
}


def normalize_ext(name: str) -> str:
    """rv_zba -> zba, Zba -> zba, M -> m"""
    name = name.strip().lower()
    if name.startswith("rv_"):
        name = name[3:]
    return name


def clone_isa_manual(dest: Path) -> None:
    print(f"  Cloning ISA manual (shallow) ...")
    if shutil.which("git") is None:
        raise RuntimeError("git is not available on PATH")
    subprocess.run(
        ["git", "clone", "--depth", "1", ISA_MANUAL_URL, str(dest)],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def scan_manual_extensions(repo_path: Path) -> set:
    """Scan .adoc files and return a set of normalised extension names."""
    src_dir = repo_path / "src"
    if not src_dir.exists():
        src_dir = repo_path  # fallback

    raw: set = set()
    for adoc in src_dir.rglob("*.adoc"):
        try:
            text = adoc.read_text(encoding="utf-8", errors="ignore")
            for m in _EXT_PATTERN.finditer(text):
                token = m.group(1)
                if token.lower() not in _NOISE:
                    raw.add(token)
        except Exception:
            pass

    return {normalize_ext(n) for n in raw}


def crossref(json_ext_map: dict, manual_exts: set) -> dict:
    json_norm = {normalize_ext(k) for k in json_ext_map}
    matched    = json_norm & manual_exts
    json_only  = json_norm - manual_exts
    manual_only = manual_exts - json_norm
    return {
        "matched":     matched,
        "json_only":   json_only,
        "manual_only": manual_only,
    }


def print_crossref_report(result: dict) -> None:
    matched     = result["matched"]
    json_only   = result["json_only"]
    manual_only = result["manual_only"]

    print(f"\n=== Tier 2: Cross-Reference Report ===")
    print(f"  {len(matched)} matched, "
          f"{len(json_only)} in JSON only, "
          f"{len(manual_only)} in manual only")

    if json_only:
        print(f"\n-- In instr_dict.json but NOT in manual ({len(json_only)}) --")
        for n in sorted(json_only):
            print(f"  {n}")

    if manual_only:
        print(f"\n-- In manual but NOT in instr_dict.json ({len(manual_only)}) --")
        for n in sorted(manual_only):
            print(f"  {n}")


def run_tier2(ext_map: dict, repo_path: Path = None) -> dict:
    print(f"\n=== Tier 2: Cross-Reference with ISA Manual ===")
    cleanup = False
    if repo_path is None:
        repo_path = Path(tempfile.mkdtemp(prefix="riscv_manual_"))
        clone_isa_manual(repo_path)
        cleanup = True

    try:
        print(f"  Scanning AsciiDoc sources ...")
        manual_exts = scan_manual_extensions(repo_path)
        print(f"  Found {len(manual_exts)} extension tokens in manual.")

        result = crossref(ext_map, manual_exts)
        print_crossref_report(result)
        return result
    finally:
        if cleanup:
            shutil.rmtree(repo_path, ignore_errors=True)