#!/usr/bin/env python3
"""
The schelp fixtures, and what is needed to test with them.

A fixture is tests/schelp/NAME.md. NAME.json is optional: {"metadata": {...}, "insertions": {...}} are the
values that the caller of the conversion gives. Next to it are the files that the tests compare with:

  NAME.schelp   the output of the converter
  NAME.html     the body of the page that SCDoc (headless sclang) renders from the output

The HTML of a page changes with the version of SuperCollider. SCLANG_VERSION holds the version that made the .html
files; the tests compare a page with its .html file only with that version.

The tests are in test_schelp_*.py. This file is also a tool: it writes the .schelp and .html files again from
the current converter. Look at the diff afterwards.

  python3 tests/schelp_fixtures.py update
"""
import argparse
import importlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
FIXTURES = HERE / "schelp"
VERSION_FILE = FIXTURES / "SCLANG_VERSION"


class RenderError(Exception):
    """SCDoc could not render the fixtures."""


def doc_name(stem: str) -> str:
    return "Md2miscTest" + stem.title().replace("-", "")


def fixtures():
    return sorted(FIXTURES.glob("*.md"))


def options_of(md_path: Path) -> dict:
    options_path = md_path.with_suffix(".json")
    return json.loads(options_path.read_text()) if options_path.exists() else {}


def convert(md_path: Path) -> str:
    options = options_of(md_path)
    return importlib.import_module("md2misc").convert_schelp(
        md_path.read_text(), options.get("metadata"), options.get("insertions")
    )


def body_of(html: str) -> str:
    """The text of the page from its header to the link to the source, without things that change."""
    start = html.index("<div class='header'>")
    end = html.index("<div class='doclink'")
    body = html[start:end]
    body = re.sub(r"<button class='copy-button'.*?</button>", "", body, flags=re.S)
    body = re.sub(r"<a class='anchor' name='[^']*'>(.*?)</a>", r"\1", body)
    return body.strip() + "\n"


def find_sclang(path: str = None):
    """The path of sclang, or `None`."""
    return path or os.environ.get("SCLANG") or shutil.which("sclang")


def sclang_version(sclang: str) -> str:
    """The version of sclang, for example `3.14.1`."""
    env = dict(os.environ, QT_QPA_PLATFORM="offscreen")
    done = subprocess.run([sclang, "-v"], env=env, capture_output=True, text=True, timeout=60)
    found = re.search(r"sclang (\S+)", done.stdout + done.stderr)
    if not found:
        raise RenderError(f"`{sclang} -v` gave no version:\n{done.stdout}{done.stderr}")
    return found[1]


def fixture_version() -> str:
    """The version of sclang that made the .html files."""
    return VERSION_FILE.read_text().strip()


def render_texts(sclang: str, texts: dict, timeout: int = 180) -> dict:
    """
    Render schelp texts with SCDoc, in one run of sclang. `texts` maps a name (letters, digits and `-`) to a
    schelp text. A text without a header gets a test header. Return, by name, the body of the HTML page, or a
    `RenderError` with the errors of SCDoc for that text.
    """
    results = {}
    with tempfile.TemporaryDirectory(prefix="md2misc-scdoc-") as tmp:
        tmp = Path(tmp)
        data = tmp / "data"
        source = data / "SuperCollider/Extensions/md2misc-tests/HelpSource/Reference"
        source.mkdir(parents=True)
        (tmp / "home").mkdir()
        keys = {}  # the key of the page in SCDoc, by name
        for name, text in texts.items():
            klass = re.match(r"CLASS::(\w+)", text)
            if klass:
                # the text has its own header: a page of a class
                key = "Classes/" + klass[1]
            else:
                key = "Reference/" + doc_name(name)
                if not text.startswith("TITLE::"):
                    text = f"TITLE::{doc_name(name)}\nSUMMARY::md2misc test page\nCATEGORIES::Tests\n\n" + text
            keys[name] = key
            target = source.parent / (key + ".schelp")
            target.parent.mkdir(exist_ok=True)
            target.write_text(text)
        script = tmp / "render.scd"
        script.write_text(
            "SCDoc.indexAllDocuments(true);\n"
            + "".join(
                f'SCDoc.prepareHelpForURL(URI("file://" ++ SCDoc.helpTargetDir ++ "/{k}.html"));\n'
                for k in keys.values()
            )
            + "0.exit;\n"
        )
        env = dict(
            os.environ, HOME=str(tmp / "home"), XDG_DATA_HOME=str(data), XDG_CONFIG_HOME=str(data),
            QT_QPA_PLATFORM="offscreen",
        )
        done = subprocess.run([sclang, str(script)], env=env, capture_output=True, text=True, timeout=timeout)
        # SCDoc names the file in a line `ERROR: In <path>:`; the lines after it tell the error
        errors = {}  # error lines, by key
        current = None
        for line in (done.stdout + done.stderr).splitlines():
            place = re.match(r"ERROR: In .*/HelpSource/(.+)\.schelp:", line)
            if place:
                current = place[1]
                errors.setdefault(current, []).append(line)
            elif line.startswith("ERROR"):
                current = None
                errors.setdefault(None, []).append(line)
            elif current and "At line" in line:
                errors[current].append(line)
        for name, key in keys.items():
            html_path = data / f"SuperCollider/Help/{key}.html"
            if key in errors:
                results[name] = RenderError("SCDoc reported errors:\n" + "\n".join(errors[key]))
            elif None in errors:
                results[name] = RenderError("SCDoc reported errors:\n" + "\n".join(errors[None]))
            elif not html_path.exists():
                results[name] = RenderError(f"SCDoc wrote no page for {name}\n" + done.stdout[-2000:])
            else:
                results[name] = body_of(html_path.read_text())
    return results


def render_all(sclang: str, timeout: int = 180) -> dict:
    """Render every fixture with SCDoc. Return the body of each HTML page, by fixture name."""
    results = render_texts(sclang, {md_path.stem: convert(md_path) for md_path in fixtures()}, timeout)
    errors = [f"{name}: {result}" for name, result in results.items() if isinstance(result, RenderError)]
    if errors:
        raise RenderError("\n".join(errors))
    return results


def update(args):
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(REPO))
    sclang = find_sclang(args.sclang)
    if not sclang:
        raise SystemExit("sclang not found. Put it on PATH, set SCLANG or use --sclang.")
    for md_path in fixtures():
        md_path.with_suffix(".schelp").write_text(convert(md_path))
    for stem, body in render_all(sclang).items():
        (FIXTURES / f"{stem}.html").write_text(body)
    VERSION_FILE.write_text(sclang_version(sclang) + "\n")
    print("written; look at the diff")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("update")
    s.add_argument("--sclang", default=None, help="path of sclang (default: SCLANG or from PATH)")
    s.set_defaults(fn=update)
    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
