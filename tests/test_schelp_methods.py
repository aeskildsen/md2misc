"""
The class methods section of a schelp page: `## Class methods` gives `CLASSMETHODS::`, a heading like `### *ar`
gives `METHOD::`, the rows of the argument table of a method give `ARGUMENT::` entries, and a `Returns:`
paragraph gives `returns::`. The checks that stop the conversion are in schelp_cases.py.
"""
import re

import pytest

from md2misc import convert, convert_schelp


def methods(section: str) -> str:
    """The schelp of a page with the Markdown in its class methods section."""
    return convert_schelp("## Class methods\n\n" + section)


def arguments(schelp: str) -> list:
    """The `ARGUMENT::` entries of the schelp as (name, text) pairs. The text is the lines after the tag."""
    return re.findall(r"^ARGUMENT::(\w+)\n(.*?)(?=\n\n|\n?\Z)", schelp, re.M | re.S)


TABLE = "| Argument | Text |\n|---|---|\n| freq | The frequency. |\n| amp | The level. |\n"
ARGUMENTS = [("freq", "The frequency."), ("amp", "The level.")]

# ------------------------------------------------------------- the whole section


def test_method_with_an_argument_table_and_a_return_value():
    out = methods("### *ar\n\n" + TABLE + "\nReturns: one channel.\n\n## Examples\n\nText.\n")
    assert out == ("CLASSMETHODS::\n\nMETHOD::ar\n\n"
                   "ARGUMENT::freq\nThe frequency.\n\nARGUMENT::amp\nThe level.\n\n"
                   "returns::one channel.\n\nEXAMPLES::\n\nText.\n")


def test_methods_without_tables_and_text_before_the_first_method():
    out = methods("Intro.\n\n### *ar, *kr\n\nText.\n\nReturns: two\nchannels.\n\n### *new\n\nMakes one.\n")
    assert out == ("CLASSMETHODS::\n\nIntro.\n\nMETHOD::ar, kr\n\nText.\n\nreturns::two\nchannels.\n\n"
                   "METHOD::new\n\nMakes one.\n")


def test_text_of_a_method_comes_before_its_arguments():
    out = methods("### *ar\n\nPlays a sine.\n\n```\nx = 1;\n```\n\n" + TABLE)
    assert out.index("Plays a sine.") < out.index("code::\nx = 1;\n::") < out.index("ARGUMENT::freq")


def test_two_methods_with_tables():
    out = methods("### *ar\n\n" + TABLE + "\n### *kr\n\n" + TABLE.replace("freq", "rate"))
    assert re.findall(r"^(METHOD|ARGUMENT)::(.*)$", out, re.M) == [
        ("METHOD", "ar"), ("ARGUMENT", "freq"), ("ARGUMENT", "amp"),
        ("METHOD", "kr"), ("ARGUMENT", "rate"), ("ARGUMENT", "amp")]


def test_section_heading_is_not_case_sensitive():
    assert methods("").startswith("CLASSMETHODS::")
    assert convert_schelp("## CLASS METHODS\n\n### *ar\n\n" + TABLE).startswith("CLASSMETHODS::\n\nMETHOD::ar")


def test_next_level_2_heading_ends_the_section():
    out = methods("### *ar\n\nText.\n\n## More\n\nReturns: text, as it is not in a method.\n")
    assert "SECTION::More\n\nReturns: text, as it is not in a method." in out


@pytest.mark.parametrize("heading, names", [
    ("### *ar", "ar"), ("### *ar, *kr", "ar, kr"), ("### *ar,*kr", "ar, kr"), ("###   *ar ,  *kr  ", "ar, kr"),
    ("### *new_2", "new_2"), ("### *ar, *kr, *new", "ar, kr, new"),
], ids=["one name", "two names", "no space", "more spaces", "underscore and digit", "three names"])
def test_method_headings(heading, names):
    assert f"METHOD::{names}\n" in methods(heading + "\n\nText.\n")


# ---------------------------------------------------- forms of the argument table


@pytest.mark.parametrize("table", [
    TABLE,
    "Argument | Text\n---|---\nfreq | The frequency.\namp | The level.\n",
    "| Argument | Text\n|---|---\n| freq | The frequency.\n| amp | The level.\n",
    "Argument | Text |\n---|---|\nfreq | The frequency. |\namp | The level. |\n",
    "| Argument | Text |\n---|---\nfreq | The frequency. |\n| amp | The level.\n",
    "|Argument|Text|\n|-|-|\n|freq|The frequency.|\n|amp|The level.|\n",
    "| Argument | Text |\n|:---|---:|\n| freq | The frequency. |\n| amp | The level. |\n",
    "| Argument | Text |\n| :---: | :-- |\n| freq | The frequency. |\n| amp | The level. |\n",
    "   | Argument | Text |\n   |---|---|\n   | freq | The frequency. |\n   | amp | The level. |\n",
    "|   Argument   |   Text   |\n|---|---|\n|\tfreq\t|  The frequency.  |\n| amp | The level. |   \n",
    "| `Argument` | **Text** |\n|---|---|\n| freq | The frequency. |\n| amp | The level. |\n",
], ids=["outer pipes", "no outer pipes", "leading pipes only", "trailing pipes only", "mixed pipes",
        "no spaces", "alignment colons", "spaces in the delimiter row", "indent of 3", "spaces and tabs",
        "markup in the header"])
def test_forms_of_the_table_give_the_same_arguments(table):
    assert arguments(methods("### *ar\n\n" + table)) == ARGUMENTS


def test_table_directly_after_a_paragraph_line():
    # as in GFM: the paragraph ends at the header row
    out = methods("### *ar\n\nPlays a sine.\n" + TABLE)
    assert "Plays a sine.\n\nARGUMENT::freq" in out
    assert arguments(out) == ARGUMENTS


@pytest.mark.parametrize("after", ["\n## Examples\n", "## Examples\n", "\nReturns: x.\n", "\n### *kr\n",
                                   "### *kr\n"],
                         ids=["section after an empty line", "section directly after", "return value",
                              "method after an empty line", "method directly after"])
def test_what_can_follow_the_table(after):
    assert arguments(methods("### *ar\n\n" + TABLE + after)) == ARGUMENTS


# ------------------------------------------------------------------ the cells


@pytest.mark.parametrize("name", ["freq", "`freq`", " `freq` "], ids=["plain", "in code", "spaces"])
def test_argument_name(name):
    out = methods(f"### *ar\n\n| Argument | Text |\n|---|---|\n|{name}| The frequency. |\n")
    assert arguments(out) == [("freq", "The frequency.")]


@pytest.mark.parametrize("name", ["in_0", "_x", "maxGrains", "x2"])
def test_argument_names_with_underscores_and_digits(name):
    out = methods(f"### *ar\n\n| Argument | Text |\n|---|---|\n| {name} | A. |\n")
    assert arguments(out) == [(name, "A.")]


@pytest.mark.parametrize("cell, text", [
    ("Uses `In.ar`.", "Uses code::In.ar::."),
    ("A **loud** sound.", "A strong::loud:: sound."),
    ("An *odd* one.", "An emphasis::odd:: one."),
    ("See [SinOsc](sc:Classes/SinOsc).", "See link::Classes/SinOsc::."),
    ("See [the site](https://example.com).", "See link::https://example.com##the site::."),
    ("One \\| two.", "One | two."),
    ("Code `a \\| b`.", "Code code::a | b::."),
    ("A \\|\\| B.", "A \\|| B."),
    ("Tag:: and ## here.", "Tag\\:: and \\## here."),
    ("> 0 is on.", "> 0 is on."),
    ("- 1 is off.", "- 1 is off."),
    ("1. is first.", "1. is first."),
    ("# is a sign.", "# is a sign."),
    ("−1 to 1, ≥ 0.5.", "−1 to 1, ≥ 0.5."),
    ("Math $x^2$.", "Math math::x^2::."),
], ids=["code", "bold", "italic", "sc link", "web link", "escaped pipe", "escaped pipe in code",
        "two escaped pipes", "schelp marks", "quote mark", "list mark", "number mark", "heading mark",
        "not ASCII", "math"])
def test_text_of_an_argument(cell, text):
    out = methods(f"### *ar\n\n| Argument | Text |\n|---|---|\n| x | {cell} |\n")
    assert arguments(out) == [("x", text)]


def test_columns_between_the_name_and_the_text():
    table = ("| Argument | Range | Unit | Text |\n|---|---|---|---|\n"
             "| freq | 20 to 20000 | Hz | The frequency. |\n"
             "| amp | | | The level. |\n"
             "| pan | −1 to 1 | | The position. |\n")
    assert arguments(methods("### *ar\n\n" + table)) == [
        ("freq", "The frequency.\nRange: 20 to 20000\nUnit: Hz"),
        ("amp", "The level."),
        ("pan", "The position.\nRange: −1 to 1"),
    ]


def test_markup_in_the_other_columns():
    table = "| Argument | Range | Text |\n|---|---|---|\n| x | `0` to **1** | A. |\n"
    assert arguments(methods("### *ar\n\n" + table)) == [("x", "A.\nRange: code::0:: to strong::1::")]


# ------------------------------------------------------------- the return value


@pytest.mark.parametrize("paragraph, returns", [
    ("Returns: one channel.", "returns::one channel."),
    ("Returns:one channel.", "returns::one channel."),
    ("Returns: an `Array`, two\nchannels.", "returns::an code::Array::, two\nchannels."),
], ids=["one line", "no space", "markup and two lines"])
def test_return_value(paragraph, returns):
    assert returns in methods("### *ar\n\n" + TABLE + "\n" + paragraph + "\n")


@pytest.mark.parametrize("markdown", [
    "## Class methods\n\nReturns: before a method.\n",
    "## Description\n\nReturns: in another section.\n",
    "## Class methods\n\n### *ar\n\nThe text. Returns: in a paragraph.\n",
    "## Class methods\n\n### *ar\n\nThe text.\nReturns: on the second line of a paragraph.\n",
], ids=["before a method", "in another section", "in the text", "second line of a paragraph"])
def test_returns_that_is_text(markdown):
    out = convert_schelp(markdown)
    assert "returns::" not in out
    assert "Returns:" in out


# ------------------------------------------------------------ the other backend


def test_tex_output_does_not_change():
    markdown = "## Class methods\n\n### *ar\n\n" + TABLE + "\nReturns: one channel.\n"
    tex = convert(markdown)
    assert "ARGUMENT" not in tex and "METHOD" not in tex and "returns::" not in tex
    assert "Returns: one channel." in tex
