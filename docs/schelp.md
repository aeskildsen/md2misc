# The schelp backend

```python
from md2misc import convert_schelp

schelp = convert_schelp(markdown, metadata=None, insertions=None)
```

`convert_schelp` returns a SuperCollider help document: the markup that SCDoc renders to HTML.

| Argument | Meaning |
|---|---|
| `metadata` | A dict of header values. A value here replaces the front matter value with the same key. |
| `insertions` | A dict that maps the name of an insertion point to the schelp text that takes its place. |

The output needs SuperCollider 3.14 or later. SCDoc 3.13 does not know the `MATH::` and `SUBSUBSECTION::` tags, which `md2misc` writes for math and for headings of level 4 and lower, and stops with a syntax error.

A Markdown construct that has no schelp form raises `UnsupportedConstruct`, with the line and the construct. `describe(source)` gives the message with the file name too. See [below](#constructs-that-stop-the-conversion).

## The header

The header tags come from three places:

1. The front matter at the start of the Markdown file: a block of `key: value` lines between two lines with `---`. The keys are `title`, `class`, `summary`, `related` and `categories`. `related` and `categories` take a list: `[a, b]`, lines with `- item` below the key, or a string with commas.
2. The first level 1 heading (`# Title`). It gives the `TITLE::` if the front matter has no `title` and no `class`. Otherwise it is left out. A second level 1 heading stops the conversion.
3. The `metadata` argument. Use it for a value that the Markdown file does not know, like the class name: `metadata={"class": "PhysWoodbar"}`.

The header is `CLASS::`, `TITLE::` (both, if both are given), `SUMMARY::`, `RELATED::` and `CATEGORIES::`, in this order. In a value, `::` gets a backslash. `##` and `||` stop the conversion, because SCDoc cannot show them in a header line.

A file with no front matter, no level 1 heading and no metadata gives the body only. A header with no title and no class stops the conversion.

## Special sections and insertion points

A level 2 heading `## Description` gives `DESCRIPTION::`, and `## Examples` gives `EXAMPLES::`. Any other level 2 heading gives `SECTION::`.

A line `<!-- md2misc: NAME -->` is an insertion point. Markdown viewers do not show the comment. The `insertions` argument puts the schelp text in its place, as it is. A program that writes the `CLASSMETHODS::` section can use this to put it between the description and the examples.

An insertion point with no text gives nothing. Text for a name that the file does not have stops the conversion.

## Class methods

A level 2 heading `## Class methods` gives `CLASSMETHODS::`. In this section, md2misc writes the methods, their arguments and their return values from Markdown that GitHub shows as it is:

```markdown
## Class methods

### *ar, *kr

Plays grains from a buffer.

| Argument | Range | What it does |
|---|---|---|
| `bufnum` | | A mono buffer. |
| `grainDur` | seconds | The length of a grain. |

Returns: two channels.
```

gives

```
CLASSMETHODS::

METHOD::ar, kr

Plays grains from a buffer.

ARGUMENT::bufnum
A mono buffer.

ARGUMENT::grainDur
The length of a grain.
Range: seconds

returns::two channels.
```

- A level 3 heading `### *name` starts a method. More names share one entry: `### *ar, *kr`. In the section, every level 3 heading must be a method, and deeper headings stop the conversion.
- The text after the method heading is the text of the method.
- The argument table follows the text. Each row is an argument. The first column is the name, plain or as code (`` `bufnum` ``). The last column is the text of the argument. Each column between them adds a line `heading: value` to the text, if its cell is not empty. The text of the header row of the first and last columns is not used.
- A paragraph that starts with `Returns:` gives `returns::`. It can follow the table, or the text if the method has no arguments.

SCDoc puts all text after an argument into that argument, and all text after `returns::` into the return value. Thus a method has its parts in this order: text, table, `Returns:` paragraph. Text after the table (other than `Returns:`), or after the `Returns:` paragraph, stops the conversion.

The section ends at the next level 2 heading. Outside a method of this section, a `Returns:` paragraph is text, and a table stops the conversion.

An insertion point can also hold a `CLASSMETHODS::` section that a program writes (see above). Use either the insertion point or the `## Class methods` section, not both.

### The argument table

The table is a pipe table of GitHub Flavored Markdown (GFM), with the same rules as on GitHub:

- A header row, a delimiter row and one row for each argument. The pipes at the start and at the end of a row are optional, and a row can have them or not.
- Each cell of the delimiter row is one or more hyphens, with an optional colon at each end (`---`, `:--`, `:-:`). The colons give the alignment, which schelp does not use.
- A table can have an indent of up to 3 spaces. It can follow the last line of a paragraph directly.
- A row with fewer cells than the header gets empty cells.
- Spaces around a cell are removed. `\|` in a cell is a `|`, also in code (`` `a \| b` ``).
- The table ends at an empty line or at the start of another block: a heading, a code block, a list, a block quote or a horizontal rule.

Where Markdown renderers do not agree, or where GitHub does not show what md2misc writes, the table stops the conversion, with its line:

- a delimiter row with more or fewer cells than the header row (GitHub shows text, not a table)
- a row with more cells than the header row (GitHub drops the extra cells)
- a `|` in code in a cell (GitHub splits the cell there, Pandoc does not): write `\|`
- `\\|` in a row
- a line without `|` directly after the table (GitHub takes it as a row, Pandoc as text): put an empty line before it
- a table without rows, a table with one column, a column between the first and the last without a heading
- an argument name that is not a name (letters, digits and `_`, not a digit first), a name twice in one table, an argument without text
- a second table in a method, or a table after `Returns:`

## The body

| Markdown | schelp |
|---|---|
| `## Heading` | `SECTION::Heading` (`## Description` and `## Examples` are special) |
| `### Heading` | `SUBSECTION::Heading` |
| `#### Heading` and deeper | `SUBSUBSECTION::Heading` |
| `**bold**` | `strong::bold::` |
| `*italics*` | `emphasis::italics::` |
| `` `code` `` | `code::code::` |
| a fenced code block with no language, or `supercollider`, `sc`, `scd`, `sclang` | `code::` block |
| a fenced code block in another language | `teletype::` block |
| `- item` and nested items | `LIST::` with `## item` lines, nested `LIST::` |
| `1. item` and nested items | `NUMBEREDLIST::` |
| `Term` and `:   definition` | `DEFINITIONLIST::` with `## term` and `\|\| definition` |
| `[text](https://example.com)` | `link::https://example.com##text::` |
| `[text](sc:Classes/SinOsc)`, `[text](sc:Classes/SinOsc#*ar)` | `link::Classes/SinOsc##text::`, `link::Classes/SinOsc#*ar#text::` (no label if the text is the name of the page) |
| `[^1]` and `[^1]: note` | `footnote::note::` at the place of the mark |
| `$x$` | `math::x::` |
| `$$` block `$$` | `math::` block |
| `> [!NOTE]` and the lines after it | `note::` block (`TIP` and `IMPORTANT` too) |
| `> [!WARNING]` and the lines after it | `warning::` block (`CAUTION` too) |

The `sc:` address is the one convention that only `md2misc` understands. The rest is Markdown that GitHub shows as it is.

### Escapes

In text, `::`, `##` and `||` get a backslash, because SCDoc takes them as markup. In code, only a `::` inside inline code, and a line with `::` alone in a code block, get a backslash.

If the text of an inline tag (bold, italic, inline code, a link, inline math, a footnote) ends with `:` or `\`, a space comes before the end-tag `::`, because SCDoc takes the character as part of the end-tag. SCDoc does not show the space.

### Differences from the TeX backend

Three rules of the schelp backend are those of CommonMark and Pandoc, not those of the TeX backend:

- A heading needs a space after the `#` characters. `#1 priority` at the start of a line is text.
- Inline math follows the rules of Pandoc: no space after the first `$` and before the second `$`, and no digit after the second `$`. Thus `$5 and $10` is text. `\$` is a dollar sign.
- A code block can be in an alert: the `>` marks are not part of the code.

## Constructs that stop the conversion

- a second level 1 heading, and a heading underlined with `=` or `-`
- block quotes that are not alerts
- links that are not `http` URLs or `sc:` links, links in `<` and `>`, a `#` in the text of a link (SCDoc splits a link at each `#`; a link without a label, where the text is the address or the name of the page, is fine), and more than one `#` in the address of a link
- citations, images and audio files, HTML tags and HTML comments (other than insertion points), `<br>` tags
- tables, other than the argument table of a method in the class methods section (see [Class methods](#class-methods), also for the rules of that section)
- horizontal rules (`---`, `***`, `___`)
- lists with `*` or `+` marks, and numbered lists with `1)`
- a footnote with more than one line
- a title or highlighted lines in a code block
- bold or italic text, code, math, a link or a footnote in a heading
- bold or italic text that holds code, math, a link, a footnote or other bold or italic text
