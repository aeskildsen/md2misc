"""
The command `md2misc schelp`: the output files, the options and the messages.
"""
from click.testing import CliRunner

from md2misc.cli import main


def schelp(*arguments):
    return CliRunner().invoke(main, ["schelp", *map(str, arguments)])


def write(path, text):
    path.write_text(text)
    return path


def test_stdout_option_prints_the_document(tmp_path):
    result = schelp(write(tmp_path / "page.md", "## Section\n"), "-s")
    assert result.exit_code == 0
    assert result.output == "SECTION::Section\n"


def test_default_output_is_a_file_in_the_output_folder(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    write(tmp_path / "page.md", "## Section\n")
    result = schelp("page.md")
    assert result.exit_code == 0
    assert (tmp_path / "output" / "page.schelp").read_text() == "SECTION::Section\n"
    assert "output/page.schelp" in result.output


def test_output_path_option_gives_the_file(tmp_path):
    result = schelp(write(tmp_path / "page.md", "## Section\n"), "-o", tmp_path / "other.schelp")
    assert result.exit_code == 0
    assert (tmp_path / "other.schelp").read_text() == "SECTION::Section\n"


def test_output_path_option_can_be_a_folder(tmp_path):
    folder = tmp_path / "folder"
    folder.mkdir()
    result = schelp(write(tmp_path / "page.md", "## Section\n"), "-o", folder)
    assert result.exit_code == 0
    assert (folder / "page.schelp").read_text() == "SECTION::Section\n"


def test_output_in_a_missing_folder_is_an_error(tmp_path):
    result = schelp(write(tmp_path / "page.md", "## Section\n"), "-o", tmp_path / "missing" / "page.schelp")
    assert result.exit_code != 0
    assert "don't seem to exist" in result.output


def test_a_file_that_is_not_markdown_is_an_error(tmp_path):
    result = schelp(write(tmp_path / "page.txt", "## Section\n"), "-s")
    assert result.exit_code != 0
    assert "doesn't end with `.md`" in result.output


def test_a_missing_file_is_an_error(tmp_path):
    result = schelp(tmp_path / "missing.md", "-s")
    assert result.exit_code != 0
    assert "not found" in result.output


def test_meta_options_can_be_repeated(tmp_path):
    page = write(tmp_path / "page.md", "## Section\n")
    result = schelp(page, "-s", "--meta", "class=SomeClass", "-m", "summary=A summary", "-m", "related=A, B")
    assert result.exit_code == 0
    assert result.output.startswith("CLASS::SomeClass\nSUMMARY::A summary\nRELATED::A, B\n\n")


def test_meta_option_keeps_an_equals_sign_in_the_value(tmp_path):
    page = write(tmp_path / "page.md", "## Section\n")
    result = schelp(page, "-s", "-m", "title=A = B")
    assert "TITLE::A = B\n" in result.output


def test_insert_option_puts_the_file_at_the_insertion_point(tmp_path):
    page = write(tmp_path / "page.md", "## A\n\n<!-- md2misc: methods -->\n\n## B\n")
    methods = write(tmp_path / "methods.schelp", "CLASSMETHODS::\nMETHOD::ar\n")
    result = schelp(page, "-s", "--insert", f"methods={methods}")
    assert result.exit_code == 0
    assert result.output == "SECTION::A\n\nCLASSMETHODS::\nMETHOD::ar\n\nSECTION::B\n"


def test_error_names_the_file_and_the_line(tmp_path):
    page = write(tmp_path / "page.md", "Text.\n\n> A quote.\n")
    result = schelp(page, "-s")
    assert result.exit_code != 0
    assert "page.md:3: the schelp output cannot write this Markdown construct: block quote" in result.output


def test_output_name_keeps_the_dots_of_the_file_name(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    folder = tmp_path / "folder"
    folder.mkdir()
    write(tmp_path / "my.page.md", "## Section\n")
    assert schelp("my.page.md").exit_code == 0
    assert schelp("my.page.md", "-o", folder).exit_code == 0
    assert (tmp_path / "output" / "my.page.schelp").exists()
    assert (folder / "my.page.schelp").exists()


def test_list_with_bad_indentation_is_an_error(tmp_path):
    result = schelp(write(tmp_path / "page.md", "- a\n   - b\n  - c\n"), "-s")
    assert result.exit_code == 1
    assert isinstance(result.exception, SystemExit)  # a message, not a traceback
    assert "indentation" in result.output
