"""
How the schelp output is made, for the cases that the fixtures do not show: header values, special sections,
admonitions, math, code, insertion points and quotation marks.
"""
import pytest

from md2misc import convert_schelp
from md2misc.backends import SchelpBackend
from md2misc.errors_warnings import DocumentError, UnsupportedConstruct

# ---------------------------------------------------------------- header


def test_no_header_without_front_matter_heading_or_values():
    assert convert_schelp("## Section\n\nText.\n") == "SECTION::Section\n\nText.\n"


def test_level_1_heading_is_the_title_if_there_is_no_title_or_class():
    assert convert_schelp("# From the heading\n\nText.\n") == "TITLE::From the heading\n\nText.\n"


def test_level_1_heading_is_left_out_if_front_matter_has_a_title():
    out = convert_schelp("---\ntitle: From front matter\n---\n\n# From the heading\n\nText.\n")
    assert out == "TITLE::From front matter\n\nText.\n"


def test_level_1_heading_is_left_out_if_the_caller_gives_a_class():
    out = convert_schelp("# From the heading\n\nText.\n", {"class": "SomeClass"})
    assert out == "CLASS::SomeClass\n\nText.\n"


def test_class_and_title_are_both_written():
    out = convert_schelp("---\ntitle: A title\nclass: SomeClass\n---\n\nText.\n")
    assert out.startswith("CLASS::SomeClass\nTITLE::A title\n\n")


def test_header_tags_are_in_a_fixed_order():
    out = convert_schelp("---\ncategories: C\nrelated: R\nsummary: S\ntitle: T\nclass: K\n---\n")
    assert out == "CLASS::K\nTITLE::T\nSUMMARY::S\nRELATED::R\nCATEGORIES::C\n"


def test_nothing_gives_nothing():
    assert convert_schelp("") == ""
    assert convert_schelp("\n\n") == ""


def test_metadata_takes_the_place_of_the_front_matter_value():
    out = convert_schelp("---\ntitle: A\nsummary: From the file\n---\n", {"summary": "From the caller"})
    assert "SUMMARY::From the caller\n" in out
    assert "From the file" not in out


@pytest.mark.parametrize("value", ["A, B", ["A", "B"]], ids=["string", "list"])
def test_metadata_lists_are_a_string_with_commas_or_a_list(value):
    assert "CATEGORIES::A, B\n" in convert_schelp("", {"title": "T", "categories": value})


@pytest.mark.parametrize(
    "front_matter, expected",
    [
        ('summary: "Quoted: with a colon"', "SUMMARY::Quoted: with a colon\n"),
        ("summary: 'Single quoted'", "SUMMARY::Single quoted\n"),
        ("summary: Unquoted: with a colon", "SUMMARY::Unquoted: with a colon\n"),
        ('related: ["Classes/A", \'Classes/B\']', "RELATED::Classes/A, Classes/B\n"),
        ("related: Classes/A, Classes/B", "RELATED::Classes/A, Classes/B\n"),
        ('categories:\n  - "A"\n  - B', "CATEGORIES::A, B\n"),
    ],
)
def test_front_matter_values(front_matter, expected):
    assert expected in convert_schelp(f"---\ntitle: T\n{front_matter}\n---\n")


def test_front_matter_can_have_empty_lines():
    assert convert_schelp("---\ntitle: T\n\nsummary: S\n---\n") == "TITLE::T\nSUMMARY::S\n"


def test_front_matter_can_end_with_three_dots():
    assert convert_schelp("---\ntitle: T\n...\n\n## S\n") == "TITLE::T\n\nSECTION::S\n"


def test_front_matter_without_an_end_is_text():
    with pytest.raises(UnsupportedConstruct) as error:
        convert_schelp("---\ntitle: T\n\n## S\n")
    assert error.value.construct == "horizontal rule"
    assert error.value.line == 1


def test_front_matter_keeps_the_line_numbers():
    with pytest.raises(UnsupportedConstruct) as error:
        convert_schelp("---\ntitle: T\nsummary: S\n---\n\nText.\n\n> A block quote.\n")
    assert error.value.line == 8


def test_colons_in_a_header_value_get_a_backslash():
    assert "SUMMARY::a\\::b\n" in convert_schelp("---\ntitle: T\nsummary: a::b\n---\n")


@pytest.mark.parametrize("value", ["a ## b", "a || b"])
def test_hash_pair_and_bar_pair_in_a_header_value_are_not_possible(value):
    with pytest.raises(UnsupportedConstruct):
        convert_schelp("", {"title": "T", "summary": value})


def test_header_without_title_or_class_is_an_error():
    with pytest.raises(DocumentError):
        convert_schelp("", {"summary": "A summary"})


# ------------------------------------------------------ special sections


@pytest.mark.parametrize("heading, expected", [
    ("## Description", "DESCRIPTION::"),
    ("## description", "DESCRIPTION::"),
    ("## Examples", "EXAMPLES::"),
    ("## EXAMPLES", "EXAMPLES::"),
    ("## Other", "SECTION::Other"),
    ("### Description", "SUBSECTION::Description"),
    ("#### Examples", "SUBSUBSECTION::Examples"),
    ("##### Deeper", "SUBSUBSECTION::Deeper"),
])
def test_headings(heading, expected):
    assert convert_schelp(heading + "\n") == expected + "\n"


# ------------------------------------------------------------ admonitions


@pytest.mark.parametrize("mark, tag", [
    ("NOTE", "note"), ("TIP", "note"), ("IMPORTANT", "note"), ("WARNING", "warning"), ("CAUTION", "warning"),
    ("note", "note"), ("Warning", "warning"),
])
def test_admonition_tags(mark, tag):
    assert convert_schelp(f"> [!{mark}]\n> The text.\n") == f"{tag}::\nThe text.\n\n::\n"


def test_admonition_with_several_lines():
    out = convert_schelp("> [!NOTE]\n> One line\n> and another.\n")
    assert out == "note::\nOne line\nand another.\n\n::\n"


# ------------------------------------------------------------------- math


def test_inline_math_with_a_colon_pair_gets_a_backslash():
    assert convert_schelp("Math $a::b$ in text.\n") == "Math math::a\\::b:: in text.\n"


def test_display_math_with_an_end_tag_line_gets_a_backslash():
    out = convert_schelp("Before.\n\n$$\nx\n::\ny\n$$\n\nAfter.\n")
    assert "\nmath::\nx\n\\::\ny\n::\n" in out


# ------------------------------------------------------------------- code


def stashed(backend, token):
    return backend.stash[token]


@pytest.mark.parametrize("language", [None, "sc", "SC", "supercollider", "sclang", "scd"])
def test_supercollider_code_is_a_code_block(language):
    backend = SchelpBackend()
    assert stashed(backend, backend.code_block("x = 1;\n", language)) == "code::\nx = 1;\n::"


@pytest.mark.parametrize("language", ["python", "bash", "text"])
def test_other_code_is_a_teletype_block(language):
    backend = SchelpBackend()
    assert stashed(backend, backend.code_block("x = 1\n", language)) == "teletype::\nx = 1\n::"


def test_code_without_a_final_line_ending_gets_one():
    backend = SchelpBackend()
    assert stashed(backend, backend.code_block("x = 1;")) == "code::\nx = 1;\n::"


def test_inline_code_with_a_colon_pair_gets_a_backslash():
    assert convert_schelp("Use `a::b`.\n") == "Use code::a\\::b::.\n"


def test_code_is_not_changed_by_the_cleaning_of_blank_lines():
    out = convert_schelp("```\na\n\n\n\nb\n```\n")
    assert out == "code::\na\n\n\n\nb\n::\n"


# --------------------------------------------------------------- insertion


def test_insertion_text_is_put_in_as_it_is():
    text = "CLASSMETHODS::\n\n\n\nMETHOD::ar :: ## ||\n"
    out = convert_schelp("## A\n\n<!-- md2misc: x -->\n\n## B\n", insertions={"x": text})
    assert out == "SECTION::A\n\nCLASSMETHODS::\n\n\n\nMETHOD::ar :: ## ||\n\nSECTION::B\n"


@pytest.mark.parametrize("insertions", [None, {}, {"x": ""}, {"x": "\n\n"}], ids=["none", "empty", "text", "blank"])
def test_insertion_point_without_text_gives_nothing(insertions):
    out = convert_schelp("## A\n\n<!-- md2misc: x -->\n\n## B\n", insertions=insertions)
    assert out == "SECTION::A\n\nSECTION::B\n"


def test_insertion_point_in_code_is_text():
    out = convert_schelp("```\n<!-- md2misc: x -->\n```\n", insertions={})
    assert out == "code::\n<!-- md2misc: x -->\n::\n"


@pytest.mark.parametrize("comment", ["<!--md2misc:x-->", "  <!--   md2misc:   x   -->  "])
def test_insertion_point_can_be_written_with_other_spaces(comment):
    assert convert_schelp(f"{comment}\n", insertions={"x": "Inserted."}) == "Inserted.\n"


def test_insertion_point_inside_a_line_is_an_html_comment():
    with pytest.raises(UnsupportedConstruct) as error:
        convert_schelp("Text <!-- md2misc: x --> more.\n", insertions={})
    assert error.value.construct == "HTML comment"


# ------------------------------------------------------------ inline tags


@pytest.mark.parametrize("markdown, expected", [
    ("**Note:** text.", "strong::Note: :: text."),
    ("*Note:* text.", "emphasis::Note: :: text."),
    ("Use `foo:` here.", "Use code::foo: :: here."),
    ("Use `C:\\` here.", "Use code::C:\\ :: here."),
    ("[Note:](https://example.com) text.", "link::https://example.com##Note: :: text."),
    ("Math $a:$ here.", "Math math::a: :: here."),
    ("Text.[^1]\n\n[^1]: Ends:", "Text.footnote::Ends: ::"),
])
def test_inline_tag_with_a_colon_or_backslash_at_the_end_gets_a_space(markdown, expected):
    # SCDoc takes the character as part of the end-tag `::`
    assert convert_schelp(markdown + "\n") == expected + "\n"


def test_link_with_its_address_as_text_has_no_label():
    assert convert_schelp("[Classes/SinOsc#*ar](sc:Classes/SinOsc#*ar)\n") == "link::Classes/SinOsc#*ar::\n"


def test_title_from_the_heading_is_escaped_once():
    assert convert_schelp("# A::B\n") == "TITLE::A\\::B\n"


def test_code_block_in_an_admonition_has_no_quote_marks():
    out = convert_schelp("> [!NOTE]\n> Try this:\n> ```\n> x = 1;\n> ```\n> And then this.\n")
    assert out == "note::\nTry this:\ncode::\nx = 1;\n::\nAnd then this.\n\n::\n"


# -------------------------------------------------- Markdown that is text


def test_dollar_signs_that_are_not_math_are_text():
    # the rules of Pandoc: no space after the first `$` and before the second `$`, and no digit after the second `$`
    assert convert_schelp("It costs $5 and $10.\n") == "It costs $5 and $10.\n"


def test_escaped_dollar_sign_is_a_dollar_sign():
    assert convert_schelp("A \\$x\\$ sign and $y$.\n") == "A $x$ sign and math::y::.\n"


def test_hash_without_a_space_after_it_is_text():
    assert convert_schelp("#1 is text.\n") == "#1 is text.\n"


# ------------------------------------------------------- quotation marks


def test_quotation_marks_stay():
    assert convert_schelp("He said \"it is 'fine' now\".\n") == "He said \"it is 'fine' now\".\n"
