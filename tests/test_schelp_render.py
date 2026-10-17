"""
SCDoc (headless sclang) parses and renders the schelp output, and the page is as expected. These tests are skipped
if sclang is not there. The pages are rendered in one run of sclang for all fixtures, and in one run for all cases.

All versions of sclang must parse the output with no error and give the expected parts of the pages. Only the
version that made the .html files must give the same whole pages.
"""
import re

import pytest

from md2misc import convert_schelp
from schelp_cases import RENDERS, SUPPORTED
from schelp_fixtures import FIXTURES, RenderError, fixtures, render_texts

FIXTURE_FILES = fixtures()

# the cases: Markdown, and the parts of the page. SCDoc must render a case of SUPPORTED with no error
CASES = RENDERS + [(markdown, []) for markdown in SUPPORTED]
CASE_NAMES = [f"case-{i:02}" for i in range(len(CASES))]

# The sections (h2) of a page, in order, for the fixtures where the order is the point of the test.
SECTIONS = {
    "structure": ["Description", "Class Methods", "Instance Methods", "Examples", "References"],
    "title": ["Description", "A named section"],
}


@pytest.mark.parametrize("stem", [p.stem for p in FIXTURE_FILES])
def test_fixture_renders_without_error(stem, rendered_pages):
    # `rendered_pages` fails if SCDoc reports an error for a fixture
    assert stem in rendered_pages


@pytest.mark.parametrize("stem", [p.stem for p in FIXTURE_FILES])
def test_page_is_as_expected(stem, rendered_pages, same_version_as_fixtures):
    assert rendered_pages[stem] == (FIXTURES / f"{stem}.html").read_text()


@pytest.mark.parametrize("stem", list(SECTIONS))
def test_sections_are_in_order(stem, rendered_pages):
    assert re.findall(r"<h2>(.*?)</h2>", rendered_pages[stem]) == SECTIONS[stem]


@pytest.fixture(scope="session")
def rendered_cases(sclang):
    """The page that SCDoc makes from the schelp output of each case, or the error, by case name."""
    texts, errors = {}, {}
    for name, (markdown, _) in zip(CASE_NAMES, CASES):
        try:
            texts[name] = convert_schelp(markdown)
        except Exception as error:  # the test of the case shows it
            errors[name] = error
    return {**render_texts(sclang, texts), **errors}


@pytest.mark.parametrize("markdown, parts", CASES, ids=[f"{n}-{c[0][:30]}" for n, c in zip(CASE_NAMES, CASES)])
def test_case_renders(markdown, parts, rendered_cases):
    page = rendered_cases[CASE_NAMES[CASES.index((markdown, parts))]]
    if isinstance(page, RenderError):
        pytest.fail(f"{convert_schelp(markdown)!r}\n{page}", pytrace=False)
    if isinstance(page, Exception):
        raise page
    for part in parts:
        assert part in page
