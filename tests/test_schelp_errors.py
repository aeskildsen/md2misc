"""
Markdown that has no schelp form stops the conversion: `convert_schelp` raises an error that holds the construct
and its line, and `describe()` names the file too. Markdown that only looks like such a construct is accepted.
"""
import re

import pytest

from md2misc import DocumentError, ParsingException, UnsupportedConstruct, convert_schelp
from schelp_cases import DOCUMENT_ERRORS, SOURCE_ONLY, SUPPORTED, UNSUPPORTED, WRITER_ONLY

CHECKED = UNSUPPORTED + SOURCE_ONLY


@pytest.mark.parametrize("markdown, construct, line", CHECKED, ids=[f"{c}-line{n}" for _, c, n in CHECKED])
def test_unsupported_construct_stops_the_conversion(markdown, construct, line):
    with pytest.raises(UnsupportedConstruct) as error:
        convert_schelp(markdown)
    assert error.value.line == line
    assert construct in error.value.describe("page.md")
    assert f"page.md:{line}:" in error.value.describe("page.md")


def test_error_names_the_file_and_the_line():
    with pytest.raises(UnsupportedConstruct) as error:
        convert_schelp("Text.\n\n---\n")
    assert str(error.value) == "line 3: the schelp output cannot write this Markdown construct: horizontal rule"
    assert error.value.describe("page.md") == \
        "page.md:3: the schelp output cannot write this Markdown construct: horizontal rule"


@pytest.mark.parametrize("markdown, metadata, insertions, message", DOCUMENT_ERRORS,
                         ids=[m for *_, m in DOCUMENT_ERRORS])
def test_document_error_stops_the_conversion(markdown, metadata, insertions, message):
    with pytest.raises((DocumentError, UnsupportedConstruct)) as error:
        convert_schelp(markdown, metadata, insertions)
    assert message in str(error.value)


@pytest.mark.parametrize("markdown", SUPPORTED, ids=[m[:30] for m in SUPPORTED])
def test_look_alike_is_accepted(markdown):
    convert_schelp(markdown)


@pytest.mark.parametrize("markdown, construct", WRITER_ONLY, ids=[c + "-" + m[:20] for m, c in WRITER_ONLY])
def test_writer_stops_where_the_check_of_the_source_does_not(markdown, construct):
    with pytest.raises(UnsupportedConstruct) as error:
        convert_schelp(markdown)
    assert construct in str(error.value)
    assert not re.search(r"page.md:\d+:", error.value.describe("page.md"))  # the error has no line


def test_list_with_bad_indentation_is_an_error():
    with pytest.raises(ParsingException, match="indentation"):
        convert_schelp("- a\n   - b\n  - c\n")
