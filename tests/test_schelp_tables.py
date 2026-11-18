"""
Tables outside the methods sections: a pipe table of GitHub Flavored Markdown gives `table::`. SCDoc has no header
row, thus the header row is a first row in bold. The checks that stop the conversion are in schelp_cases.py.
"""
import pytest

from md2misc import convert, convert_schelp


@pytest.mark.parametrize("markdown, schelp", [
    ("| A | B |\n|---|---|\n| 1 | 2 |\n| 3 | 4 |\n",
     "table::\n## strong::A:: || strong::B::\n## 1 || 2\n## 3 || 4\n::\n"),
    ("| | |\n|---|---|\n| 1 | 2 |\n", "table::\n## 1 || 2\n::\n"),
    ("| A | |\n|---|---|\n| 1 | 2 |\n", "table::\n## strong::A:: ||\n## 1 || 2\n::\n"),
    ("| A | B |\n|---|---|\n| 1 |\n", "table::\n## strong::A:: || strong::B::\n## 1 ||\n::\n"),
    ("A | B\n:-:|--:\n1 | 2\n", "table::\n## strong::A:: || strong::B::\n## 1 || 2\n::\n"),
    ("| A |\n|---|\n| 1 |\n", "table::\n## strong::A::\n## 1\n::\n"),
], ids=["header and rows", "empty header row", "empty header cell", "short row", "no outer pipes and alignment",
        "one column"])
def test_table(markdown, schelp):
    assert convert_schelp(markdown) == schelp


@pytest.mark.parametrize("cell, text", [
    ("Uses `In.ar`.", "Uses code::In.ar::."),
    ("A **loud** sound.", "A strong::loud:: sound."),
    ("See [SinOsc](sc:Classes/SinOsc).", "See link::Classes/SinOsc::."),
    ("One \\| two.", "One | two."),
    ("Code `a \\| b`.", "Code code::a | b::."),
    ("A \\|\\| B and ## C.", "A \\|| B and \\## C."),
    ("Math $x^2$.", "Math math::x^2::."),
], ids=["code", "bold", "link", "escaped pipe", "escaped pipe in code", "schelp marks", "math"])
def test_markup_in_a_cell(cell, text):
    assert convert_schelp(f"| A |\n|---|\n| {cell} |\n") == f"table::\n## strong::A::\n## {text}\n::\n"


def test_table_between_paragraphs():
    out = convert_schelp("## Section\n\nBefore.\n\n| A |\n|---|\n| 1 |\n\nAfter.\n")
    assert out == "SECTION::Section\n\nBefore.\n\ntable::\n## strong::A::\n## 1\n::\n\nAfter.\n"


def test_table_in_the_examples_section_of_a_class():
    out = convert_schelp("## Class methods\n\n### *ar\n\nText.\n\n## Examples\n\n| A |\n|---|\n| 1 |\n")
    assert out.endswith("EXAMPLES::\n\ntable::\n## strong::A::\n## 1\n::\n")


def test_tex_output_does_not_change():
    tex = convert("| A | B |\n|---|---|\n| 1 | 2 |\n")
    assert "table" not in tex and "| A | B |" in tex
