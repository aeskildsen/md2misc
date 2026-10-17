# Development

## Tests

The tests use pytest. In a virtual environment, from a checkout of this repository:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e ".[test]"
python3 -m pytest              # all tests
python3 -m pytest -k schelp    # the schelp tests
```

The tests of the SCDoc output run headless `sclang` (SuperCollider). They are skipped if `sclang` is not on `PATH` or in the `SCLANG` environment variable, so a contributor to another backend does not need SuperCollider. With `MD2MISC_REQUIRE_SCLANG=1`, a missing `sclang` is an error and not a skip.

Each version of `sclang` from 3.14 must parse the schelp output with no error and give the expected parts of the pages. The `.html` files hold whole pages of the SuperCollider version in `tests/schelp/SCLANG_VERSION`. The tests compare whole pages only with that version.

GitHub Actions (`.github/workflows/tests.yml`) runs all tests against the installed package with several Python versions. It runs the SCDoc tests with the SuperCollider of Debian forky (Ubuntu 24.04 has 3.13).

## Test files

- `tests/test_tex_battery.py`: the TeX output is the same as the output of `md2tex`, for the fixtures in `tests/fixtures` (pages of a book and the `md2tex` README, with a coverage table in `tests/COVERAGE.md`).
- `tests/test_schelp_golden.py`: the schelp output is the same as the `.schelp` files in `tests/schelp`.
- `tests/test_schelp_render.py`: SCDoc renders the schelp output to the HTML in the `.html` files in `tests/schelp`, with the sections in order. SCDoc also renders the cases in `tests/schelp_cases.py` (`RENDERS` and `SUPPORTED`) with no error, and the pages hold the expected HTML.
- `tests/test_schelp_errors.py`: the constructs without a schelp form stop the conversion with the file, line and construct, and look-alikes in code are accepted.
- `tests/test_schelp_writer.py`: the writers of the schelp backend stop at the constructs too, when the check of the source does not find them.
- `tests/test_schelp_behavior.py`, `tests/test_schelp_cli.py` and `tests/test_tex_cli.py`: the output of single cases, and the commands.

## Fixture tools

- `python3 tests/battery.py build` makes the TeX fixtures. It needs `pip install -e ".[battery]"` and private checkouts of the book that the fixtures come from, so contributors do not run it. The `.tex` files are the frozen reference (the output of `md2tex`).
- `python3 tests/schelp_fixtures.py update` makes the `.schelp` and `.html` files and `SCLANG_VERSION`. Read the diff afterwards. After an update of SuperCollider, the HTML can change: make the files again and read the diff.
