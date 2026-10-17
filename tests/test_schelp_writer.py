"""
The writers of the schelp backend stop at the constructs that have no schelp form, too, if the check of the
Markdown source does not find them first. The error has no line then.
"""
import pytest

from md2misc import convert_schelp
from md2misc.backends import SchelpBackend
from md2misc.errors_warnings import UnsupportedConstruct
from schelp_cases import UNSUPPORTED, WRITER_ONLY

# the front matter errors come from the reading of the front matter, not from the writers
FROM_THE_WRITERS = [case for case in UNSUPPORTED if not case[1].startswith("front matter")]

# the construct that the writers name, if it is not the one that the check of the source names: the converter
# takes an audio file for an image, as the audio syntax is the one of an image
NAMED_BY_THE_WRITERS = {"audio file": "image"}


@pytest.fixture
def no_source_check(monkeypatch):
    monkeypatch.setattr(SchelpBackend, "check_source", lambda self, markdown: None)


@pytest.mark.parametrize(
    "markdown, construct, line", FROM_THE_WRITERS, ids=[f"{c}-line{n}" for _, c, n in FROM_THE_WRITERS]
)
def test_writer_stops_at_the_construct(no_source_check, markdown, construct, line):
    with pytest.raises(UnsupportedConstruct) as error:
        convert_schelp(markdown)
    assert NAMED_BY_THE_WRITERS.get(construct, construct) in error.value.message
    assert error.value.line is None


@pytest.mark.parametrize("markdown, construct", WRITER_ONLY, ids=[c + "-" + m[:20] for m, c in WRITER_ONLY])
def test_writer_stops_at_the_construct_without_the_check(no_source_check, markdown, construct):
    with pytest.raises(UnsupportedConstruct) as error:
        convert_schelp(markdown)
    assert construct in error.value.message
