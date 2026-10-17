#!/usr/bin/env python3
"""
Golden battery for the Markdown to TeX converter: the tool that makes the fixtures.

The fixtures are the pairs name.md and name.tex in tests/fixtures. test_tex_battery.py compares the output of the
converter with the .tex files. There is one command:

  build   Export the book at a fixed commit, preprocess every page with the
          book build's own preprocessing, pick the smallest set of pages that
          covers every Markdown construct, and write each page as a fixture
          pair (name.md, name.tex). The .tex file is the output of the
          converter, thus run `build` only with a converter whose output is
          known to be right (md2tex f90f23b gave the stored output). The
          fixtures readme.md and synthetic-*.md are kept as they are; only
          their .tex files are rewritten. Also writes COVERAGE.md.

`build` needs PyYAML and pathvalidate (`pip install -e ".[battery]"`), and checkouts
of the book repository and the book build repository, which are private. Thus
contributors do not run `build`: the fixtures are the frozen reference.

  python3 tests/battery.py build
"""
import argparse
import contextlib
import importlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"
BOOK_EXPORT = HERE / "book-export"

BOOK_REPO = Path.home() / "gp/komposition-og-lydproduktion-med-supercollider"
BOOK_COMMIT = "8896a4c"
BUILD_REPO = Path.home() / "gp/klsc-book-build"
REPO = HERE.parent

# The arguments that the book build gives to convert().
CONVERT_ARGS = dict(
    document_class="article",
    minted_language="./sc_lexer.py:SuperColliderLexer",
    override_language=True,
)

# The private markers that the book build puts into the Markdown.
MARKER_RE = re.compile(
    r"!!!(?:LABEL:[^!\n]*|NEWPAGE|RESETPAGECOLOR|Øvelser|Cheat sheets|faHeadphones|faLink"
    r"|AUDIO:[^\n]*?|CAPTIONEDAUDIO:[^\n]*?)!!!"
)

# Each construct: (name, regex, flags). Matched on the preprocessed Markdown.
# Code blocks and inline code are cut out before the "text" constructs run.
CODE_BLOCK_RE = re.compile(r"```(?:.|\n)*?```")
INLINE_CODE_RE = re.compile(r"`.+?`")

CONSTRUCTS = [
    # name, regex, flags, where ("raw" = whole text, "text" = text without code)
    ("heading level 1", r"^# ", re.M, "text"),
    ("heading level 2", r"^## ", re.M, "text"),
    ("heading level 3", r"^### ", re.M, "text"),
    ("heading level 4+", r"^#{4,} ", re.M, "text"),
    ("bold", r"(?<!\*)\*{2}(?!\*).+?(?<!\*)\*{2}(?!\*)", 0, "text"),
    ("italics", r"(?<![*\w])\*(?!\*)[^*\n]+?(?<!\*)\*(?!\*)", 0, "text"),
    ("inline code", r"`.+?`", 0, "raw"),
    ("code block", r"^```", re.M, "raw"),
    ("code block with title=", r'^```[^\n]*title="', re.M, "raw"),
    ("code block with hl_lines=", r'^```[^\n]*hl_lines="', re.M, "raw"),
    ("code block without info string", r"^```[ \t]*$(?=\n(?:.|\n)*?^```)", re.M, "raw"),
    ("unordered list", r"^[ \t]*-(?!-{2,}) ", re.M, "text"),
    ("nested unordered list", r"^[ \t]+-(?!-{2,}) ", re.M, "text"),
    ("ordered list", r"^[ \t]*\d+\. ", re.M, "text"),
    ("nested ordered list", r"^[ \t]+\d+\. ", re.M, "text"),
    ("definition list", r"^[^\n]+\n{1,3}: {3}", re.M, "text"),
    ("footnote", r"\[\^\d+\]", 0, "text"),
    ("citation", r"\[-?@[^\]]+\](?!\()", 0, "text"),
    ("citation with multiple keys", r"\[-?@[^\];]+;[^\]]*\](?!\()", 0, "text"),
    ("citation with locator", r"\[-?@[^\],]+, (?:pp?\. )?\d+(?:-\d+)?\](?!\()", 0, "text"),
    ("inline math", r"(?<!\$)\$(?!\$)[^$\n]+?\$(?!\$)", 0, "text"),
    ("block math", r"\$\$.+?\$\$", re.S, "text"),
    ("image", r"!\[[^\]]*\]\([^)]*\)", 0, "text"),
    ("image with width", r"!\[[^\]]*\]\([^)]*\)\{[^}]*width=\"\d+%\"", 0, "text"),
    ("block quote", r"^>", re.M, "text"),
    ("inline quote", r"\"[^\"\n]*?\"", 0, "text"),
    ("external link", r"(?<!!)\[[^\]\n]+\]\(http[^)]*\)", 0, "text"),
    ("internal link", r"(?<!!)\[[^\]\n@]+\]\((?!http)[^)]*\)", 0, "text"),
    ("horizontal rule", r"^-{3,}[ \t]*$", re.M, "text"),
    ("line break tag", r"<br/?>", 0, "text"),
    ("highlight marks", r"\{==", 0, "text"),
    ("escape: curly braces", r"[{}]", 0, "text"),
    ("escape: hash in text", r"(?<!^)(?<!^#)(?<!^##)(?<!^###)#", re.M, "text"),
    ("escape: dollar sign", r"\\\$|\$(?!\$)", 0, "text"),
    ("escape: percent", r"%", 0, "text"),
    ("escape: ampersand", r"&", 0, "text"),
    ("escape: underscore", r"_", 0, "text"),
    ("escape: caret", r"\^", 0, "text"),
    ("escape: backslash", r"\\", 0, "text"),
    ("escape: tilde", r"~", 0, "text"),
]


def strip_markers(md: str) -> str:
    return MARKER_RE.sub("", md)


def count_constructs(md: str) -> dict:
    text = INLINE_CODE_RE.sub("", CODE_BLOCK_RE.sub("", md))
    counts = {}
    for name, rx, flags, where in CONSTRUCTS:
        source = md if where == "raw" else text
        counts[name] = len(re.findall(rx, source, flags))
    return counts


# ------------------------------------------------------------------ build

def export_book():
    """Export the docs folder of the book at the fixed commit."""
    if BOOK_EXPORT.exists():
        shutil.rmtree(BOOK_EXPORT)
    BOOK_EXPORT.mkdir()
    archive = subprocess.run(
        ["git", "-C", str(BOOK_REPO), "archive", BOOK_COMMIT],
        check=True, capture_output=True,
    ).stdout
    subprocess.run(["tar", "-x", "-C", str(BOOK_EXPORT)], input=archive, check=True)


def load_preprocessor(workdir: Path):
    """Import the book build's own preprocessing, with mermaid stubbed out."""
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(BUILD_REPO))
    # parse_docs imports md2tex at module level, but the preprocessing never
    # calls it. A stand-in module is enough.
    sys.modules.setdefault("md2tex", types.SimpleNamespace(convert=None))
    parse_docs = importlib.import_module("parse_docs")

    (workdir / "tex/diagrams").mkdir(parents=True)
    os.chdir(workdir)
    parse_docs.MERMAID_DIAGRAM_DIR = "./tex/diagrams/"
    parse_docs.subprocess.run = lambda *a, **k: None  # no headless browser
    return parse_docs.preprocess_mkdocs_markdown


def page_list():
    ignored = (BUILD_REPO / "build_scripts/ignored_MD_files.txt").read_text().split("\n")
    docs = BOOK_EXPORT / "docs"
    pages = []
    for path in sorted(docs.rglob("*.md")):
        if path.name in ignored or path.name == "index.md":
            continue
        pages.append(path)
    pages.append(BOOK_EXPORT / "book-preface.md")
    return pages


def fixture_name(path: Path) -> str:
    rel = path.relative_to(BOOK_EXPORT)
    parts = [p for p in rel.parts if p != "docs"]
    return "book-" + "-".join(parts).removesuffix(".md")


def pick_pages(candidates: dict, required: set) -> list:
    """Greedy set cover. Prefer the page that covers most open constructs;
    break ties with the smaller page."""
    open_constructs = set(required)
    chosen = []
    while open_constructs:
        best = max(
            candidates.items(),
            key=lambda kv: (
                len(open_constructs & kv[1]["covers"]),
                -len(kv[1]["md"]),
            ),
        )
        gained = open_constructs & best[1]["covers"]
        if not gained:
            break
        chosen.append(best[0])
        open_constructs -= gained
    return chosen


def build(args):
    use_checkout(args)
    export_book()
    workdir = Path(tempfile.mkdtemp(prefix="battery-"))
    cwd = os.getcwd()
    try:
        preprocess = load_preprocessor(workdir)
        candidates = {}
        for path in page_list():
            with contextlib.redirect_stdout(io.StringIO()):
                md = strip_markers(preprocess(path.read_text()))
            counts = count_constructs(md)
            candidates[fixture_name(path)] = {
                "md": md,
                "counts": counts,
                "covers": {k for k, v in counts.items() if v},
            }
    finally:
        os.chdir(cwd)
        shutil.rmtree(workdir, ignore_errors=True)

    readme_md = (FIXTURES / "readme.md").read_text()
    readme = {
        "md": readme_md,
        "counts": count_constructs(readme_md),
    }
    readme["covers"] = {k for k, v in readme["counts"].items() if v}

    # Hand-written fixtures and the md2tex README stay in place; they cover
    # what the book lacks. Their coverage counts, too.
    synthetic = {}
    for path in sorted(FIXTURES.glob("synthetic-*.md")):
        md = path.read_text()
        counts = count_constructs(md)
        synthetic[path.stem] = {
            "md": md, "counts": counts,
            "covers": {k for k, v in counts.items() if v},
        }

    names = [c[0] for c in CONSTRUCTS]
    covered_by_fixed = readme["covers"].union(*(s["covers"] for s in synthetic.values()))
    book_union = set().union(*(c["covers"] for c in candidates.values()))
    # book pages that are fixtures already stay; new pages are added only for open constructs
    kept = [p.stem for p in sorted(FIXTURES.glob("book-*.tex")) if p.stem in candidates]
    covered = covered_by_fixed.union(*(candidates[n]["covers"] for n in kept))
    chosen = kept + pick_pages(candidates, book_union - covered)

    selected = {"readme": readme, **synthetic, **{n: candidates[n] for n in chosen}}
    gaps = [n for n in names if not any(s["counts"][n] for s in selected.values())]

    FIXTURES.mkdir(exist_ok=True)
    for old in FIXTURES.glob("*.tex"):
        if not old.stem.startswith("synthetic-") and old.stem != "readme":
            old.with_suffix(".md").unlink()
    for old in FIXTURES.glob("*.tex"):
        old.unlink()

    convert = importlib.import_module(args.module).convert
    for name, fx in selected.items():
        if not name.startswith("synthetic-") and name != "readme":
            (FIXTURES / f"{name}.md").write_text(fx["md"])
        with contextlib.redirect_stdout(io.StringIO()):
            tex = convert(fx["md"], **CONVERT_ARGS)
        (FIXTURES / f"{name}.tex").write_text(tex)

    # variants: the same Markdown with other convert() arguments
    for args_path in sorted(FIXTURES.glob("*@*.args")):
        base = args_path.stem.split("@")[0]
        variant = {**CONVERT_ARGS, **json.loads(args_path.read_text())}
        with contextlib.redirect_stdout(io.StringIO()):
            tex = convert((FIXTURES / f"{base}.md").read_text(), **variant)
        args_path.with_suffix(".tex").write_text(tex)

    write_coverage(selected, names, gaps, len(candidates))
    print(f"{len(selected)} fixtures written to {FIXTURES}")
    if gaps:
        print("constructs not covered:", ", ".join(gaps))


def write_coverage(selected: dict, names: list, gaps: list, n_pages: int):
    cols = list(selected)
    lines = [
        "# Coverage of the golden battery",
        "",
        f"Book pages considered: {n_pages} (commit `{BOOK_COMMIT}` of the book). "
        f"Fixtures: {len(selected)}. Each cell is the number of occurrences of the construct in the fixture.",
        "",
        "| construct | " + " | ".join(cols) + " | total |",
        "|---|" + "---|" * (len(cols) + 1),
    ]
    for n in names:
        row = [selected[c]["counts"][n] for c in cols]
        lines.append(f"| {n} | " + " | ".join(str(v) if v else "·" for v in row) + f" | {sum(row)} |")
    lines.append("")
    lines.append("Constructs without a fixture: " + (", ".join(gaps) if gaps else "none") + ".")
    (HERE / "COVERAGE.md").write_text("\n".join(lines) + "\n")


def use_checkout(args):
    """Import the converter from a source folder, unless --installed is given."""
    sys.dont_write_bytecode = True
    if not args.installed:
        sys.path.insert(0, str(Path(args.converter).expanduser()))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    for name, fn in (("build", build),):
        s = sub.add_parser(name)
        s.add_argument("--converter", default=str(REPO),
                       help="folder that holds the converter module (default: %(default)s)")
        s.add_argument("--installed", action="store_true",
                       help="import the converter from the Python environment, not from --converter")
        s.add_argument("--module", default="md2misc",
                       help="module that exposes convert() (default: %(default)s)")
        s.set_defaults(fn=fn)
    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
