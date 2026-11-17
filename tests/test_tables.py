"""
The rows of a pipe table (md2misc/tables.py): which lines are a table, the cells of each row, and where the
table ends. The expected values are those of cmark-gfm 0.29.0.gfm.13, the GitHub Flavored Markdown parser of
GitHub, where the comments do not say otherwise (checked on 2026-11-17).
"""
import pytest

from md2misc import tables


def table(markdown: str):
    """The rows of the first table in the Markdown as lists of cells, with short rows padded, or None."""
    lines = markdown.split("\n")
    for number in range(len(lines)):
        if tables.starts_table(lines, number):
            header = tables.split_row(lines[number])
            rows = [header]
            for row in lines[number + 2:tables.table_end(lines, number)]:
                cells = tables.split_row(row)
                rows.append(cells + [""] * (len(header) - len(cells)))
            return rows
    return None


@pytest.mark.parametrize("markdown, rows", [
    ("| a | b |\n|---|---|\n| 1 | 2 |\n", [["a", "b"], ["1", "2"]]),
    ("a | b\n---|---\n1 | 2\n", [["a", "b"], ["1", "2"]]),
    ("| a | b\n|--|--\n| 1 | 2\n", [["a", "b"], ["1", "2"]]),
    ("a | b |\n--|--|\n1 | 2 |\n", [["a", "b"], ["1", "2"]]),
    ("| abc | defghi |\n:-: | -----------:\nbar | baz\n", [["abc", "defghi"], ["bar", "baz"]]),
    ("|a|b|\n|-|-|\n|1|2|\n", [["a", "b"], ["1", "2"]]),
    ("|a|b|c|d|\n|:--|:-:|--:|---|\n|1|2|3|4|\n", [["a", "b", "c", "d"], ["1", "2", "3", "4"]]),
    ("|a|b|\n|  :---:  |  ---:  |\n|1|2|\n", [["a", "b"], ["1", "2"]]),
    ("|a|b|  \n|-|-|  \n|1|2|  \n", [["a", "b"], ["1", "2"]]),
    ("   |a|b|\n   |-|-|\n   |1|2|\n", [["a", "b"], ["1", "2"]]),
], ids=["outer pipes", "no outer pipes", "leading pipes only", "trailing pipes only", "mixed outer pipes",
        "one hyphen", "alignment", "spaces around delimiter cells", "trailing spaces", "indent of 3"])
def test_forms_of_a_table(markdown, rows):
    assert table(markdown) == rows


@pytest.mark.parametrize("markdown", [
    "|a|b|\n|- -|---|\n|1|2|\n",
    "|a|b|\n|:|---|\n",
    "|a|b|\n|=|=|\n",
    "|a|b|\n|-||\n",
    "|a|\n---\n|1|\n",
    "    |a|b|\n    |-|-|\n    |1|2|\n",
    "|a|b|\n    |-|-|\n|1|2|\n",
    "|a|b|\n\n|-|-|\n|1|2|\n",
    "| a | b |\n| --- \\|| --- |\n",
    "- a | b\n- c | d\n",
    "a | b\n--- ---\n",
    "Text without a pipe.\n---|---\n",
], ids=["space in a delimiter cell", "colon only", "equals signs", "empty delimiter cell",
        "delimiter row without a pipe (a heading)", "indent of 4 (code)", "delimiter row with an indent of 4",
        "empty line after the header", "escaped pipe in the delimiter row", "list items with pipes",
        "delimiter row without pipes", "header without a pipe"])
def test_not_a_table(markdown):
    assert table(markdown) is None


@pytest.mark.parametrize("markdown, rows", [
    ("|a|\n|---|\n|1|\n", [["a"], ["1"]]),
    ("a |\n--|\n1 |\n", [["a"], ["1"]]),
    ("| a\n|--\n| 1\n", [["a"], ["1"]]),
    ("||\n|-|\n|1|\n", [[""], ["1"]]),
], ids=["outer pipes", "trailing pipes", "leading pipes", "empty header"])
def test_one_column(markdown, rows):
    assert table(markdown) == rows


@pytest.mark.parametrize("markdown, rows", [
    ("|a|b|\n|-|-|\n", [["a", "b"]]),
    ("|a|b|\n|-|-|\n|1|\n", [["a", "b"], ["1", ""]]),
    ("|a|b|\n|-|-|\n||2|\n|1||\n", [["a", "b"], ["", "2"], ["1", ""]]),
    ("|  a  |  b  |\n|-|-|\n|  1  |\t2\t|\n", [["a", "b"], ["1", "2"]]),
    ("| | |\n|-|-|\n|1|2|\n", [["", ""], ["1", "2"]]),
    ("| name | range |\n|---|---|\n| pan | −1 to 1 |\n", [["name", "range"], ["pan", "−1 to 1"]]),
], ids=["header only", "short row padded", "empty cells", "spaces and tabs trimmed", "empty header cells",
        "text that is not ASCII"])
def test_cells(markdown, rows):
    assert table(markdown) == rows


def test_long_row_keeps_its_cells():
    # GFM drops the third cell; the backends that write tables stop at it, thus the cells are kept
    assert table("|a|b|\n|-|-|\n|1|2|3|\n") == [["a", "b"], ["1", "2", "3"]]


def test_text_after_the_last_pipe_is_a_cell():
    assert table("|a|b|\n|-|-|\n|1|2| tail\n") == [["a", "b"], ["1", "2", "tail"]]


def test_delimiter_row_with_another_number_of_cells_starts_a_table():
    # GFM: no table. The backends that write tables stop at it with a message, which is clearer than text with
    # pipes in it
    assert table("|a|b|\n|---|\n|1|2|\n") == [["a", "b"], ["1", "2"]]
    assert table("|a|b|\n|---|---|---|\n|1|2|\n") == [["a", "b"], ["1", "2"]]


@pytest.mark.parametrize("row, cells", [
    ("|x\\|y|2|", ["x\\|y", "2"]),
    ("|`x\\|y`|2|", ["`x\\|y`", "2"]),
    ("|1|2\\|", ["1", "2\\|"]),
    ("|`x|y`|2|", ["`x", "y`", "2"]),
], ids=["escaped pipe", "escaped pipe in code", "escaped pipe at the end", "pipe in code splits the cell"])
def test_split_row_with_pipes_in_cells(row, cells):
    assert tables.split_row(row) == cells


def test_unescape_gives_the_pipe():
    assert tables.unescape("x\\|y") == "x|y"
    assert tables.unescape("`x\\|y`") == "`x|y`"


@pytest.mark.parametrize("after", ["", "\n\nnext", "\n# H", "\n> q", "\n```\nx\n```", "\n- x", "\n1. x", "\n***"],
                         ids=["end of the text", "empty line", "heading", "block quote", "code block", "list",
                              "numbered list", "horizontal rule"])
def test_end_of_a_table(after):
    lines = ("|a|b|\n|-|-|\n|1|2|" + after).split("\n")
    assert tables.table_end(lines, 0) == 3


def test_line_without_a_pipe_is_a_row():
    # as in GFM; the backends that write tables stop at it, because Pandoc ends the table there
    lines = "|a|b|\n|-|-|\n|1|2|\nnext\n".split("\n")
    assert tables.table_end(lines, 0) == 4


def test_second_delimiter_row_is_a_row():
    assert table("|a|b|\n|-|-|\n|1|2|\n|-|-|\n") == [["a", "b"], ["1", "2"], ["-", "-"]]


@pytest.mark.parametrize("markdown, header", [
    ("para\n|a|b|\n|-|-|\n|1|2|\n", 1),
    ("p1\np2\n|a|b|\n|-|-|\n", 2),
    ("|a|\n|b|\n|-|\n", 1),
], ids=["after a paragraph line", "after two paragraph lines", "only one header row"])
def test_header_is_the_line_before_the_delimiter_row(markdown, header):
    lines = markdown.split("\n")
    assert [n for n in range(len(lines)) if tables.starts_table(lines, n)] == [header]
