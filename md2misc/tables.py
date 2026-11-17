"""
the rows of a pipe table, in the form of GitHub Flavored Markdown (GFM).

a table is a header row, a delimiter row and body rows. pipes separate the cells. a pipe at the start and at the
end of a row is optional. a backslash before a pipe makes it text in the cell (`\\|`). the delimiter row has one
cell for each column: hyphens with an optional colon at each end (`---`, `:--`, `--:`, `:-:`).

the backends use these functions to find tables in the source and in the converters, so that both find the same
tables.
"""
import re

# a cell of the delimiter row. the colons give the alignment, which no backend uses
DELIMITER_CELL = r":?-+:?"

# the indentation of a table: more spaces make an indented code block
MAX_INDENT = 3


def pipe_positions(line: str) -> list:
    """
    the positions of the pipes that separate cells: the pipes without a backslash before them.
    """
    return [m.start() for m in re.finditer(r"(?<!\\)\|", line)]


def has_pipe(line: str) -> bool:
    return bool(pipe_positions(line))


def indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def split_row(line: str) -> list:
    """
    the cells of a table row, without the spaces around them. the pipe at the start and at the end of the row,
    if there is one, does not make an empty cell. a `\\|` in a cell is kept as it is.
    """
    text = line.strip()
    cells, start = [], 0
    for position in pipe_positions(text):
        cells.append(text[start:position])
        start = position + 1
    cells.append(text[start:])
    if text.startswith("|"):
        cells.pop(0)
    if len(text) > 1 and text.endswith("|") and not text.endswith("\\|") and cells:
        cells.pop()
    return [cell.strip() for cell in cells]


def unescape(cell: str) -> str:
    """
    the text of a cell, with `|` in place of `\\|`.
    """
    return cell.replace("\\|", "|")


def is_delimiter_row(line: str) -> bool:
    """
    whether the line is a delimiter row: it has a pipe, and each cell is hyphens with optional colons.
    """
    if not has_pipe(line) or indent(line) > MAX_INDENT:
        return False
    cells = split_row(line)
    return bool(cells) and all(re.fullmatch(DELIMITER_CELL, cell) for cell in cells)


def starts_table(lines: list, number: int) -> bool:
    """
    whether `lines[number]` is the header row of a table: it has a pipe, and the next line is a delimiter row.
    """
    if number + 1 >= len(lines):
        return False
    header = lines[number]
    return (bool(header.strip()) and has_pipe(header) and indent(header) <= MAX_INDENT
            and is_delimiter_row(lines[number + 1]))


# a line that starts another block ends a table. other lines without a pipe would be rows in GFM, but not in
# Pandoc and other forms: the backends that write tables stop at them
BLOCK_START = r"[ ]{0,3}(#{1,6}([ \t]|$)|>|```|~~~|[-*+][ \t]|\d+[.)][ \t]|([-*_])([ \t]*\3){2,}[ \t]*$)"


def ends_table(line: str) -> bool:
    """
    whether the line ends a table and is not a row of it: an empty line, or the start of another block.
    """
    return not line.strip() or re.match(BLOCK_START, line) is not None


def table_end(lines: list, number: int) -> int:
    """
    the index after the last row of the table whose header row is `lines[number]`. the rows go on to an empty
    line, to the start of another block or to the end of the text.
    """
    end = number + 2
    while end < len(lines) and not ends_table(lines[end]):
        end += 1
    return end
