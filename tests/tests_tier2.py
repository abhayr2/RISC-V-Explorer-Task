import pytest
from tier2_crossref import normalize_ext, crossref, scan_manual_extensions
from pathlib import Path
import tempfile, os


def test_normalize_strips_rv_prefix():
    assert normalize_ext("rv_zba")  == "zba"
    assert normalize_ext("rv_i")    == "i"
    assert normalize_ext("Zba")     == "zba"
    assert normalize_ext("M")       == "m"


def test_crossref_matched():
    json_map = {"rv_zba": ["SH1ADD"], "rv_m": ["MUL"], "rv_f": ["FADD.S"]}
    manual   = {"zba", "m", "zicsr"}
    result   = crossref(json_map, manual)
    assert "zba" in result["matched"]
    assert "m"   in result["matched"]
    assert "f"   in result["json_only"]
    assert "zicsr" in result["manual_only"]


def test_crossref_empty_json():
    result = crossref({}, {"zba", "m"})
    assert result["matched"]   == set()
    assert result["json_only"] == set()
    assert result["manual_only"] == {"zba", "m"}


def test_scan_manual_extensions_adoc(tmp_path):
    """Create a fake .adoc file and check scanning picks up extension names."""
    src = tmp_path / "src"
    src.mkdir()
    (src / "chapter.adoc").write_text(
        "The Zba extension provides address generation.\n"
        "See also the M and F extensions.\n",
        encoding="utf-8",
    )
    found = scan_manual_extensions(tmp_path)
    assert "zba" in found
    assert "m"   in found
    assert "f"   in found