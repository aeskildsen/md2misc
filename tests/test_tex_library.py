"""
The TeX backend as a library: the arguments of `convert`, the default template, the warnings and the errors.
"""
import subprocess
import sys
from pathlib import Path

import pytest

from md2misc import DocumentError, Md2miscWarning, ParsingException, convert, default_template

ROOT = Path(__file__).resolve().parent.parent


def test_the_package_needs_only_the_standard_library():
    # -S: no site-packages, so a missing dependency is an import error
    code = f"import sys; sys.path.insert(0, {str(ROOT)!r}); import md2misc; print(md2misc.convert_schelp('## A'))"
    done = subprocess.run([sys.executable, "-I", "-S", "-c", code], capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    assert done.stdout == "SECTION::A\n\n"


def test_document_class_book_gives_chapters():
    assert "\\chapter{A title}" in convert("# A title\n", document_class="book")


def test_invalid_document_class_is_an_error():
    with pytest.raises(DocumentError, match="`report`"):
        convert("# A title\n", document_class="report")


def test_unnumbered_headings():
    assert "\\section*{A title}" in convert("# A title\n", unnumbered=True)


def test_override_language_gives_every_code_block_the_language():
    markdown = "```python\nx = 1\n```\n"
    assert "\\begin{minted}{python}" in convert(markdown)
    assert "\\begin{minted}{supercollider}" in convert(markdown, minted_language="supercollider",
                                                       override_language=True)


def test_default_template_has_the_tokens_for_the_body_and_the_document_class():
    template = default_template()
    assert "@@BODYTOKEN@@" in template
    assert "@@DOCUMENTCLASSTOKEN@@" in template


def test_unknown_code_language_gives_a_warning_and_the_language_text():
    markdown = "```nolanguage\nx = 1\n```\n"
    with pytest.warns(Md2miscWarning, match="language `nolanguage` is not supported"):
        tex = convert(markdown)
    assert "\\begin{minted}{text}" in tex


def test_link_that_is_not_a_url_gives_a_warning():
    with pytest.warns(Md2miscWarning, match="type of link `other.md` is not supported"):
        convert("A [link](other.md).\n")


def test_list_with_bad_indentation_is_an_error():
    with pytest.raises(ParsingException, match="indentation"):
        convert("- a\n   - b\n  - c\n")
