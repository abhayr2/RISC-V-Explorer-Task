# RISC-V Instruction Set Explorer

A Python tool that parses the RISC-V instruction set, cross-references it
with the official ISA manual, and visualises extension relationships. 

## Requirements

- Python 3.11+
- Git (for cloning the ISA manual)

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/riscv-explorer.git
cd riscv-explorer
pip install -r requirements.txt
```

## Getting instr_dict.json

The instruction dictionary is generated from the official RISC-V opcodes
repository. Run these commands once to produce it:

```bash
git clone --depth=1 https://github.com/riscv/riscv-opcodes.git /tmp/riscv-opcodes
cd /tmp/riscv-opcodes
pip install uv
uv run riscv_opcodes -j
cp instr_dict.json ~/riscv-explorer/
cd ~/riscv-explorer/
```

## Running

```bash
# Run all tiers (prints to terminal)
python3 main.py

# Run and save output to file
python3 main.py | tee sample_output/output.txt

# Run only Tier 1
python3 -c "from tier1_parser import fetch_instr_dict, run_tier1; run_tier1(fetch_instr_dict())"

# Run only Tier 2
python3 -c "from tier1_parser import fetch_instr_dict, group_by_extension; from tier2_crossref import run_tier2; run_tier2(group_by_extension(fetch_instr_dict()))"

# Run only Tier 3
python3 -c "from tier1_parser import fetch_instr_dict, group_by_extension; from tier3_graph import run_tier3; run_tier3(group_by_extension(fetch_instr_dict()))"

# Run tests (your files are named tests_*.py)
python3 -m pytest -v tests -o "python_files=tests_*.py"

# Run only Tier 1 tests
python3 -m pytest -v tests/tests_tier1.py

# Run only Tier 2 tests
python3 -m pytest -v tests/tests_tier2.py

# Run one specific test
python3 -m pytest -v tests/tests_tier2.py::test_crossref_matched
```

## Sample Output (Tier 1)

```
=== Tier 1: Instruction Set Parsing ===
Total instructions : 1188
Unique extensions  : 114

Extension                      # Instructions  Example
------------------------------------------------------------
rv32_c                                      1  C_JAL
rv64_i                                     15  ADDIW
rv_i                                       37  ADD
rv_m                                        8  DIV
rv_zba                                      3  SH1ADD
rv_zbb                                     17  ANDN
rv_zicsr                                    6  CSRRC
... (remaining extensions) ...

=== Instructions in Multiple Extensions (73) ===
Mnemonic             Extensions
------------------------------------------------------------
ANDN                 rv_zbb, rv_zkn, rv_zks, rv_zk, rv_zbkb
CLMUL                rv_zbc, rv_zkn, rv_zks, rv_zk, rv_zbkc
SHA256SIG0           rv_zknh, rv_zkn, rv_zk
... (remaining) ...
```

## Sample Output (Tier 2)

```
=== Tier 2: Cross-Reference Report ===
  50 matched, 64 in JSON only, 96 in manual only
```

## Sample Output (Tier 3)

```
=== Tier 3: Extension Sharing Graph (text) ===
  rv_zbb     <-> rv_zbkb, rv_zk, rv_zkn, rv_zks
  rv_zbc     <-> rv_zbkc, rv_zk, rv_zkn, rv_zks
  ...
  [graph] Saved to extension_graph.png
```

## Design Decisions

### Normalisation
Extension names are normalised for cross-referencing by stripping the `rv_`
prefix and lowercasing. For example:
- `rv_zba` → `zba`
- `Zba` → `zba`
- `M` → `m`

### Architecture-specific prefixes (JSON-only results)
Extensions like `rv32_zknd` and `rv64_zba` are intentionally reported as
JSON-only. The ISA manual uses architecture-agnostic names (e.g., just
"Zknd" or "Zba") while the opcodes repo uses `rv32_` and `rv64_` prefixes
to distinguish 32-bit and 64-bit variants. This is a real naming convention
difference between the two sources, not a bug.

### Manual-only results
Many manual-only entries are:
- Profile shorthand names (e.g., `rv64gc`, `rv32ifd`)
- Vector length extensions (e.g., `zvl128b`, `zvl256b`)
- Conceptual groupings (e.g., `zve64x`) that exist as documentation
  concepts but don't have their own instruction files in the opcodes repo

This is expected and reflects a genuine structural difference between the
two sources.

### Manual scanning
The ISA manual is shallow-cloned (`depth=1`) to keep runtime short and disk
usage minimal. A regex matches Z-prefixed extension names (e.g., Zba, Zicsr)
and known single-letter ISA extensions (M, F, D, A, H, V, S). The cloned
repo is automatically deleted after Tier 2 completes.

### Fallback loading
`instr_dict.json` is loaded from the local project directory if present.
This avoids repeated network calls and works offline after the first run.

### Extension sharing graph
The graph connects extensions that share at least one instruction. It is
saved as `extension_graph.png` using networkx and matplotlib, and also
printed as a text adjacency list for environments without a display.

**NOTE:** Claude was used to help generate README.md and for debugging.