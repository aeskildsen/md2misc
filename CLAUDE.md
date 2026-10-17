# md2misc

Markdown to TeX (the same output as md2tex) and to SuperCollider help (schelp). README.md has the usage.

## Tests

- There is no Nix tooling: the package is `pyproject.toml` only. The tests run in `.venv`, made in the `dev` distrobox with the Python of Ubuntu (in the container, `python3` on `PATH` is the Nix one of the host): `distrobox enter dev -- fish -lc 'cd ~/gp/md2misc; and uv venv --python /usr/bin/python3 .venv; and uv pip install --python .venv/bin/python -e ".[test]"'`. Then `distrobox enter dev -- fish -lc 'cd ~/gp/md2misc; and .venv/bin/python -m pytest'`.
- The SCDoc tests need `sclang`; they are skipped without it. The host `sclang` (3.14.1, the version in `tests/schelp/SCLANG_VERSION`) is on `PATH` in the container. GitHub Actions (`.github/workflows/tests.yml`) runs the tests against the installed package, and the SCDoc tests in a `debian:forky` container, for `sclang` 3.14 (Ubuntu 24.04 has 3.13, which does not know `math::` and `subsubsection::`).
- `tests/fixtures/*.tex` is the output of md2tex f90f23b. It is the reference. Never run `tests/battery.py build` against changed converter code. Change a `.tex` file only if the TeX output is meant to change.
- The fixtures test article-numbered TeX and the heading variants only. After a change in the converters, also compare with the old code on edge cases.
- After a schelp change, run `.venv/bin/python tests/schelp_fixtures.py update` in the container (needs `sclang`) and read the diff. It also writes the `sclang` version to `tests/schelp/SCLANG_VERSION`.

## Design

- `converters.py` finds the Markdown. `backends/` writes the output. There is no TeX or schelp string in `converters.py`.
- `syntax.py` holds the regular expressions of the Markdown constructs. The converters and `SchelpBackend.check_source()` use them, so that both find the same constructs. A backend selects the strict CommonMark/Pandoc form of headings and inline math, and whether quote marks are removed from code in a block quote; `TeXBackend` keeps the md2tex forms.
- Kept from md2tex, so that the TeX output stays the same: `TeXBackend.remove_quote_marks()` turns every `>` into a space, so a `<br>` tag is never found. One known difference: a `#` followed at once by an escaped character (`#_x`) is a heading now (md2tex: text).
- A Markdown construct without a schelp form goes in three places: the writer in `SchelpBackend`, `SchelpBackend.check_source()` (it gives the line, which the converters cannot) and `tests/schelp_cases.py` (`UNSUPPORTED`). If the converters take the construct for text (tables, `*` lists, HTML), it goes in `check_source()` and `SOURCE_ONLY` only.
- SCDoc (3.14.1): in prose, `::`, `##` and `||` need a backslash. In a header line only `::` does, and `##` or `||` cannot be written. Modal tags (`strong::`, `emphasis::`, inline `code::`, `link::`) cannot hold other tags. The name of a section is plain text. In the inline form of a tag, a `:` or `\` at the end of the text joins the end-tag: a space before `::` keeps them apart (`\::` there is a syntax error). A link splits at each `#` (page, anchor, label), and a `#` in the label cannot be escaped. A backslash before other characters, `$` too, is text.
