"""
citations through Pandoc: Pandoc's citeproc turns citations like `[@doe1999, p. 30]` into text, with the
references of a bibliography file. md2misc calls the `pandoc` program only for the citations; it converts the
rest of the text itself.

the output of Pandoc is its JSON form (the document tree), so that the text of a citation does not need to be
read as Markdown again.
"""
import json
import os
import shutil
import subprocess
from pathlib import Path

from .errors_warnings import DocumentError

# the arguments of pandoc: Markdown in, the document tree out, citations processed with the built-in style
# (Chicago author-date)
PANDOC_ARGUMENTS = ["--from", "markdown", "--to", "json", "--citeproc"]


def find_pandoc() -> str:
    """
    the path of the `pandoc` program: the environment variable `PANDOC`, or `pandoc` on the `PATH`.
    """
    path = os.environ.get("PANDOC") or shutil.which("pandoc")
    if not path:
        raise DocumentError("citations need the program `pandoc`: put it on the PATH, or set the environment "
                            "variable PANDOC to its path")
    return path


def process(citations: list, bibliography) -> tuple:
    """
    let Pandoc write the citations, in one run, so that the style can tell apart works with the same author and
    year (`1999a`, `1999b`).
    :param citations: the citations in Pandoc's form (`[@doe1999, p. 30]`), in the order of the text
    :param bibliography: the path of the bibliography file (BibTeX, BibLaTeX, CSL JSON or CSL YAML)
    :return: the text of each citation, and the reference entry of each key; both as lists of Pandoc inline
             elements (the JSON form)
    """
    path = Path(bibliography)
    if not path.is_file():
        raise DocumentError(f"the bibliography `{bibliography}` is not a file")
    source = "".join(citation + "\n\n" for citation in citations) + "::: {#refs}\n:::\n"
    pandoc = find_pandoc()
    try:
        done = subprocess.run([pandoc, *PANDOC_ARGUMENTS, "--bibliography", str(path)],
                              input=source, capture_output=True, text=True)
    except OSError as error:
        raise DocumentError(f"md2misc could not run pandoc (`{pandoc}`): {error}") from error
    if done.returncode != 0:
        raise DocumentError(f"pandoc could not process the citations:\n{done.stderr.strip()}")
    blocks = json.loads(done.stdout)["blocks"]

    texts = []
    entries = {}
    for block in blocks:
        if block["t"] == "Para":
            cites = [inline for inline in block["c"] if inline["t"] == "Cite"]
            texts.append(cites[0]["c"][1] if len(cites) == 1 else block["c"])
        elif block["t"] == "Div" and block["c"][0][0] == "refs":
            for entry in block["c"][1]:
                key = entry["c"][0][0].removeprefix("ref-")
                paragraphs = [b["c"] for b in entry["c"][1] if b["t"] in ("Para", "Plain")]
                entries[key] = [inline for paragraph in paragraphs for inline in paragraph]
    if len(texts) != len(citations):
        raise DocumentError(f"pandoc gave {len(texts)} citations for {len(citations)}")
    return texts, entries
