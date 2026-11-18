"""
The schelp output has not changed: every fixture in tests/schelp is converted and compared with the .schelp file
next to it.
"""
import pytest

from schelp_fixtures import convert, fixtures, needs_pandoc

FIXTURE_FILES = fixtures()


@pytest.mark.parametrize("md_path", FIXTURE_FILES, ids=[p.stem for p in FIXTURE_FILES])
def test_schelp_output_is_unchanged(md_path, request):
    if needs_pandoc(md_path):
        request.getfixturevalue("same_pandoc_as_fixtures")
    assert convert(md_path) == md_path.with_suffix(".schelp").read_text()
