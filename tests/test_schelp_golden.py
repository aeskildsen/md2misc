"""
The schelp output has not changed: every fixture in tests/schelp is converted and compared with the .schelp file
next to it.
"""
import pytest

from schelp_fixtures import convert, fixtures

FIXTURE_FILES = fixtures()


@pytest.mark.parametrize("md_path", FIXTURE_FILES, ids=[p.stem for p in FIXTURE_FILES])
def test_schelp_output_is_unchanged(md_path):
    assert convert(md_path) == md_path.with_suffix(".schelp").read_text()
