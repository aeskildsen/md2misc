import os

import pytest

import schelp_fixtures


@pytest.fixture(scope="session")
def sclang():
    """The path of sclang. Tests that need it are skipped if it is not there."""
    path = schelp_fixtures.find_sclang()
    if not path:
        message = "sclang not found (put it on PATH or set SCLANG)"
        if os.environ.get("MD2MISC_REQUIRE_SCLANG"):
            pytest.fail(message)  # a check must not pass without these tests
        pytest.skip(message)
    return path


@pytest.fixture(scope="session")
def same_version_as_fixtures(sclang):
    """Skip a test that compares whole pages if sclang is not the version that made the .html files."""
    version, expected = schelp_fixtures.sclang_version(sclang), schelp_fixtures.fixture_version()
    if version != expected:
        pytest.skip(f"the .html files are from sclang {expected}, this is sclang {version}")


@pytest.fixture(scope="session")
def rendered_pages(sclang):
    """The body of the page that SCDoc makes from each schelp fixture, by fixture name. One sclang run."""
    try:
        return schelp_fixtures.render_all(sclang)
    except schelp_fixtures.RenderError as error:
        pytest.fail(str(error), pytrace=False)
