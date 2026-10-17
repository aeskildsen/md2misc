"""
Markdown that has no schelp form stops the conversion: the command exits with a non-zero status and the error
names the file, the line and the construct. Markdown that only looks like such a construct is accepted.
"""
import re

import pytest
from click.testing import CliRunner

from md2misc.cli import main
from schelp_cases import DOCUMENT_ERRORS, SOURCE_ONLY, SUPPORTED, UNSUPPORTED, WRITER_ONLY

CHECKED = UNSUPPORTED + SOURCE_ONLY

def schelp(tmp_path, markdown, *arguments):
    """Run `md2misc schelp -s` on the Markdown. Return the file name and the result."""
    path = tmp_path / "page.md"
    path.write_text(markdown)
    return path.name, CliRunner().invoke(main, ["schelp", "-s", str(path), *arguments])


@pytest.mark.parametrize("markdown, construct, line", CHECKED, ids=[f"{c}-line{n}" for _, c, n in CHECKED])
def test_unsupported_construct_stops_the_conversion(tmp_path, markdown, construct, line):
    name, result = schelp(tmp_path, markdown)
    assert result.exit_code != 0
    assert construct in result.output
    assert f"{name}:{line}:" in result.output


@pytest.mark.parametrize("markdown, arguments, message", DOCUMENT_ERRORS, ids=[m for _, _, m in DOCUMENT_ERRORS])
def test_document_error_stops_the_conversion(tmp_path, markdown, arguments, message):
    insertion = tmp_path / "insertion.schelp"
    insertion.write_text("CLASSMETHODS::\n")
    _, result = schelp(tmp_path, markdown, *[a.replace("{file}", str(insertion)) for a in arguments])
    assert result.exit_code != 0
    assert message in result.output


@pytest.mark.parametrize("markdown", SUPPORTED, ids=[m[:30] for m in SUPPORTED])
def test_look_alike_is_accepted(tmp_path, markdown):
    _, result = schelp(tmp_path, markdown)
    assert result.exit_code == 0, result.output


@pytest.mark.parametrize("markdown, construct", WRITER_ONLY, ids=[c + "-" + m[:20] for m, c in WRITER_ONLY])
def test_writer_stops_where_the_check_of_the_source_does_not(tmp_path, markdown, construct):
    name, result = schelp(tmp_path, markdown)
    assert result.exit_code != 0
    assert construct in result.output
    assert not re.search(rf"{name}:\d+:", result.output)  # the error has no line
