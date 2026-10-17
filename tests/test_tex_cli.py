"""
The command `md2misc tex`: the output files, the options and the messages.
"""
import pytest
from click.testing import CliRunner

from md2misc import convert
from md2misc.cli import main

MARKDOWN = "# A title\n\nText with **bold** and `code`.\n"


def tex(*arguments):
    return CliRunner().invoke(main, ["tex", *map(str, arguments)])


@pytest.fixture
def page(tmp_path, monkeypatch):
    # the command writes to the output folder in the current folder
    monkeypatch.chdir(tmp_path)
    path = tmp_path / "page.md"
    path.write_text(MARKDOWN)
    return path


def test_stdout_option_prints_the_tex(page):
    result = tex(page, "-s")
    assert result.exit_code == 0
    assert result.output == convert(MARKDOWN) + "\n"


def test_default_output_is_a_file_in_the_output_folder(page, tmp_path):
    result = tex(page)
    assert result.exit_code == 0
    assert (tmp_path / "output" / "page.tex").read_text() == convert(MARKDOWN)


def test_complete_file_uses_the_template_of_the_package(page, tmp_path):
    result = tex(page, "-c", "-o", tmp_path / "complete.tex")
    assert result.exit_code == 0
    text = (tmp_path / "complete.tex").read_text()
    assert text.startswith("\\documentclass[a4paper, 12pt, twoside]{article}")
    assert convert(MARKDOWN) in text
    assert "@@BODYTOKEN@@" not in text


def test_document_class_option_goes_in_the_template_and_the_headings(page, tmp_path):
    tex(page, "-c", "-d", "book", "-o", tmp_path / "book.tex")
    text = (tmp_path / "book.tex").read_text()
    assert "{book}" in text
    assert "\\chapter{A title}" in text


def test_custom_template_option(page, tmp_path):
    template = tmp_path / "template.tex"
    template.write_text("\\begin{document}\n@@BODYTOKEN@@\n\\end{document}\n")
    tex(page, "-c", "-t", template, "-o", tmp_path / "custom.tex")
    assert (tmp_path / "custom.tex").read_text().startswith("\\begin{document}\n\\section{A title}")


def test_template_without_the_body_token_is_an_error(page, tmp_path):
    template = tmp_path / "template.tex"
    template.write_text("\\begin{document}\n\\end{document}\n")
    result = tex(page, "-c", "-t", template)
    assert result.exit_code != 0
    assert "@@BODYTOKEN@@" in result.output


def test_missing_template_is_an_error(page, tmp_path):
    result = tex(page, "-c", "-t", tmp_path / "missing.tex")
    assert result.exit_code != 0
    assert "not found" in result.output


def test_unnumbered_option(page):
    assert "\\section*{A title}" in tex(page, "-u", "-s").output


def test_override_language_option_has_its_own_short_flag(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    path = tmp_path / "code.md"
    path.write_text("```python\nx = 1\n```\n")
    assert "\\begin{minted}{python}" in tex(path, "-s").output
    assert "\\begin{minted}{supercollider}" in tex(path, "-s", "-l", "supercollider", "-O").output


def test_output_file_without_the_tex_extension_gets_it(page, tmp_path):
    result = tex(page, "-o", tmp_path / "result")
    assert (tmp_path / "result.tex").exists()
    assert "WARNING" in result.output


def test_a_file_that_is_not_markdown_is_an_error(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    path = tmp_path / "page.txt"
    path.write_text(MARKDOWN)
    result = tex(path, "-s")
    assert result.exit_code != 0
    assert "doesn't end with `.md`" in result.output


def test_warnings_go_to_standard_error(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    path = tmp_path / "code.md"
    path.write_text("```nolanguage\nx = 1\n```\n")
    result = tex(path, "-s")
    assert result.exit_code == 0
    assert "WARNING" not in result.stdout
    assert "language `nolanguage` is not supported" in result.stderr


def test_link_that_is_not_a_url_gives_a_warning(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    path = tmp_path / "link.md"
    path.write_text("A [link](other.md).\n")
    result = tex(path, "-s")
    assert result.stdout == convert("A [link](other.md).\n") + "\n"
    assert "type of link `other.md` is not supported" in result.stderr


def test_list_with_bad_indentation_is_an_error(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    path = tmp_path / "list.md"
    path.write_text("- a\n   - b\n  - c\n")
    result = tex(path, "-s")
    assert result.exit_code == 1
    assert isinstance(result.exception, SystemExit)  # a message, not a traceback
    assert "indentation" in result.output


def test_invalid_document_class_is_an_error(page):
    result = tex(page, "-s", "-d", "report")
    assert result.exit_code != 0
    assert "allowed values are `article` or `book`" in result.output
