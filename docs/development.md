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

The tests of the citations run `pandoc`. They are skipped if `pandoc` is not on `PATH` or in the `PANDOC` environment variable. With `MD2MISC_REQUIRE_PANDOC=1`, a missing `pandoc` is an error. The text of a citation can change between versions of Pandoc: the tests compare the files of the fixtures with a bibliography only with the version in `tests/schelp/PANDOC_VERSION`.

GitHub Actions (`.github/workflows/tests.yml`) runs all tests against the installed package with several Python versions. It runs the SCDoc tests with the SuperCollider of Debian forky (Ubuntu 24.04 has 3.13). Both jobs install the `pandoc` of the distribution.

## Test files

- `tests/test_tex_battery.py`: the TeX output is the same as the output of `md2tex`, for the fixtures in `tests/fixtures` (pages of a book and the `md2tex` README, with a coverage table in `tests/COVERAGE.md`).
- `tests/test_schelp_golden.py`: the schelp output is the same as the `.schelp` files in `tests/schelp`.
- `tests/test_schelp_render.py`: SCDoc renders the schelp output to the HTML in the `.html` files in `tests/schelp`, with the sections in order. SCDoc also renders the cases in `tests/schelp_cases.py` (`RENDERS` and `SUPPORTED`) with no error, and the pages hold the expected HTML.
- `tests/test_schelp_errors.py`: the constructs without a schelp form stop the conversion with the file, line and construct, and look-alikes in code are accepted.
- `tests/test_schelp_writer.py`: the writers of the schelp backend stop at the constructs too, when the check of the source does not find them.
- `tests/test_schelp_behavior.py`: the output of single cases.
- `tests/test_schelp_methods.py`: the methods sections: method headings, the forms of the argument table, the cells, the return value and the discussion.
- `tests/test_schelp_tables.py`: the tables outside the methods sections.
- `tests/test_schelp_citations.py`: the citations, with the bibliography `tests/schelp/citations.bib`.
- `tests/test_tables.py`: the rows of a pipe table (`md2misc/tables.py`): which lines are a table, the cells and the end of the table. The expected values are those of cmark-gfm, the GFM parser of GitHub, where a comment does not say otherwise.
- `tests/test_tex_library.py`: the arguments of `convert`, the default template, the warnings and the errors of the TeX backend, and that the package needs only the standard library.

## Fixture tools

- `python3 tests/battery.py build` makes the TeX fixtures. It needs `pip install -e ".[battery]"` and private checkouts of the book that the fixtures come from, so contributors do not run it. The `.tex` files are the frozen reference (the output of `md2tex`).
- `python3 tests/schelp_fixtures.py update` makes the `.schelp` and `.html` files, `SCLANG_VERSION` and `PANDOC_VERSION`. It needs `sclang` and `pandoc`. Read the diff afterwards. After an update of SuperCollider or Pandoc, the output can change: make the files again and read the diff. The files in `tests/schelp/images` are next to the schelp files when SCDoc renders them.

## Releases

A release is an annotated git tag `vX.Y.Z` on `main`. Other projects pin md2misc to a tag (for example as a git submodule), so do not move or delete a tag after it is pushed.

1. Set `version` in `pyproject.toml` to the new version, in the same commit as the last change of the release or in a commit of its own.
2. Make sure that GitHub Actions passes on that commit of `main`. GitHub Actions runs the SCDoc tests too, so SuperCollider is not necessary on your computer.
3. Tag that commit: `git tag -a vX.Y.Z -m "md2misc X.Y.Z"`. The tag and the version in `pyproject.toml` must agree.
4. Push the tag: `git push origin vX.Y.Z`. A GitHub release for the tag is optional.
