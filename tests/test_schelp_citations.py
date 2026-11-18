"""
Citations in the schelp output: with a bibliography, pandoc writes each citation (`[@key]`), and the citation
becomes a footnote. The first citation of a source gives its reference entry, later citations the short form.
A citation in a footnote gives the short form in parentheses. The tests that run pandoc are skipped without it.
"""
from pathlib import Path

import pytest

from md2misc import DocumentError, UnsupportedConstruct, convert, convert_schelp

BIBLIOGRAPHY = Path(__file__).parent / "schelp" / "citations.bib"
DOE = "Doe, Jane. 1999. emphasis::Sound and Wood::. Acme"
SMITH = ("Smith, John, and Ann Lee. 2000. “Bars and Rods: A Study of Modes.” emphasis::Journal of Acoustics:: 3: "
         "1–9. link::https://doi.org/10.1000/xyz::")


def schelp(markdown: str) -> str:
    return convert_schelp(markdown, bibliography=BIBLIOGRAPHY)


@pytest.mark.parametrize("citation, footnote", [
    ("[@doe1999]", DOE + "."),
    ("[@doe1999, p. 30]", DOE + ", p. 30."),
    ("[@doe1999, 30]", DOE + ", p. 30."),
    ("[@doe1999, 30-35]", DOE + ", pp. 30–35."),
    ("[@doe1999, chap. 2]", DOE + ", chap. 2."),
    ("[-@doe1999]", DOE + "."),
    ("[@doe1999; @smith2000]", DOE + "; " + SMITH + "."),
], ids=["key", "page", "page number", "pages", "other locator", "no author", "two sources"])
def test_first_citation_gives_the_reference_entry(citation, footnote, pandoc):
    assert schelp(f"A text {citation}.\n") == f"A text footnote::{footnote}::.\n"


def test_later_citation_gives_the_short_form(pandoc):
    out = schelp("One [@doe1999]. Two [@doe1999, 31]. Three [@smith2000; @doe1999].\n")
    assert out == (f"One footnote::{DOE}.::. Two footnote::Doe 1999, 31.::. "
                   f"Three footnote::{SMITH}; Doe 1999.::.\n")


def test_works_of_one_author_and_year_are_told_apart(pandoc):
    out = schelp("One [@doe1999]. Two [@doe1999b]. Again [@doe1999b].\n")
    assert out == ("One footnote::Doe, Jane. 1999b. emphasis::Sound and Wood::. Acme.::. "
                   # the style writes `———` for the second work of an author in a list; a footnote names the
                   # author again
                   "Two footnote::Doe, Jane. 1999a. emphasis::More Wood::. Acme.::. Again footnote::Doe 1999a.::.\n")


def test_citation_in_a_footnote_gives_the_short_form_in_parentheses(pandoc):
    out = schelp("Text.[^1] More [@smith2000].\n\n[^1]: As in [@doe1999, 30].\n\n    And [@smith2000].\n")
    assert out == ("Text.footnote::As in (Doe 1999, 30).\n\nAnd (Smith and Lee 2000).:: "
                   f"More footnote::{SMITH}.::.\n")


def test_citation_directly_after_a_word(pandoc):
    # SCDoc does not find a tag directly after a letter; it removes the space before a footnote mark
    assert schelp("A text[@doe1999].\n") == f"A text footnote::{DOE}.::.\n"


def test_citation_at_the_start_of_a_line(pandoc):
    assert schelp("A text\n[@doe1999].\n") == f"A text\nfootnote::{DOE}.::.\n"


def test_text_in_brackets_with_an_at_sign_later_is_text():
    # as in the TeX output: a citation starts with `@` or `-@`
    assert schelp("A text [see @doe1999].\n") == "A text [see @doe1999].\n"


def test_citation_in_code_is_code():
    assert schelp("Code `[@doe1999]`.\n") == "Code code::[@doe1999]::.\n"


def test_missing_key_stops_the_conversion(pandoc):
    with pytest.raises(DocumentError, match="no entry for: nobody"):
        schelp("A text [@nobody].\n")


def test_bibliography_that_is_not_a_file():
    with pytest.raises(DocumentError, match="is not a file"):
        convert_schelp("A text [@doe1999].\n", bibliography="no-such-file.bib")


def test_pandoc_that_cannot_run(monkeypatch):
    monkeypatch.setenv("PANDOC", "/no/such/pandoc")
    with pytest.raises(DocumentError, match="could not run pandoc"):
        schelp("A text [@doe1999].\n")


@pytest.mark.parametrize("citation", ["[@doe1999; smith]", "[@doe1999 @smith2000]", "[@doe1999, p. 3; see]"])
def test_other_forms_of_a_citation_stop_the_conversion(citation):
    with pytest.raises(UnsupportedConstruct, match="the forms are"):
        schelp(f"A text {citation}.\n")


def test_text_without_citations_does_not_need_the_bibliography(monkeypatch):
    monkeypatch.setenv("PANDOC", "/no/such/pandoc")
    assert schelp("A text.\n") == "A text.\n"


def test_citation_without_a_bibliography_names_the_choices():
    with pytest.raises(UnsupportedConstruct, match="give a bibliography to the conversion, or write the citation "
                                                   "as text"):
        convert_schelp("A text [@doe1999].\n")


def test_tex_output_does_not_change():
    assert convert("A text [@doe1999, 30].\n").strip() == "A text \\parencite[p. 30]{doe1999}."
