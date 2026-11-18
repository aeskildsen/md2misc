# The schelp backend

```python
from md2misc import convert_schelp

schelp = convert_schelp(markdown, metadata=None, insertions=None, bibliography=None)
```

`convert_schelp` returns a SuperCollider help document: the markup that SCDoc renders to HTML.

| Argument | Meaning |
|---|---|
| `metadata` | A dict of header values. A value here replaces the front matter value with the same key. |
| `insertions` | A dict that maps the name of an insertion point to the schelp text that takes its place. |
| `bibliography` | The path of a bibliography file for the citations (BibTeX, BibLaTeX, CSL JSON or CSL YAML). See [Citations](#citations). |

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

A level 2 heading `## Description` gives `DESCRIPTION::`, `## Class methods` gives `CLASSMETHODS::`, `## Instance methods` gives `INSTANCEMETHODS::`, and `## Examples` gives `EXAMPLES::`. Any other level 2 heading gives `SECTION::`.

A line `<!-- md2misc: NAME -->` is an insertion point. Markdown viewers do not show the comment. The `insertions` argument puts the schelp text in its place, as it is. A program that writes the `CLASSMETHODS::` section can use this to put it between the description and the examples.

An insertion point with no text gives nothing. Text for a name that the file does not have stops the conversion.

## Methods

In the two methods sections, `## Class methods` and `## Instance methods`, md2misc writes the methods, their arguments, their return values and their discussions from Markdown that GitHub shows as it is:

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

- A level 3 heading starts a method: `### *name` in the class methods section, `### -name` in the instance methods section. These are the marks of SCDoc's anchors (`*ar`, `-play`). More names share one entry: `### *ar, *kr`. In a methods section, every level 3 heading must be a method.
- The text after the method heading is the text of the method.
- The argument table follows the text. Each row is an argument. The first column is the name, plain or as code (`` `bufnum` ``). The last column is the text of the argument. Each column between them adds a line `heading: value` to the text, if its cell is not empty. The text of the header row of the first and last columns is not used.
- A paragraph that starts with `Returns:` gives `returns::`. It can follow the table, or the text if the method has no arguments.
- A level 4 heading `#### Discussion` gives `discussion::`. The text after it, to the next method or section, is the discussion: more text and examples. Any Markdown with a schelp form can be in it, except a table. Other level 4 headings in a method stop the conversion.

SCDoc puts all text after an argument into that argument, and all text after `returns::` into the return value. Thus a method has its parts in this order: text, table, `Returns:` paragraph, discussion. Text after the table or after the `Returns:` paragraph stops the conversion, if a `#### Discussion` heading does not come before it.

A methods section ends at the next level 2 heading. Outside a method, a `Returns:` paragraph is text. In a methods section, a table outside a method stops the conversion.

An insertion point can also hold a `CLASSMETHODS::` or `INSTANCEMETHODS::` section that a program writes (see above). Use either the insertion point or the Markdown section, not both.

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

## Tables

Outside the methods sections, a pipe table gives `table::`. The rules of GFM and the checks are the same as for the argument table (see above). The cells can hold bold and italic text, code, links, math and footnotes.

SCDoc has no header row. The header row is the first row, in bold. A header cell that is empty stays empty. A header row with only empty cells gives no row: this is the form for a table without a header. Bold text cannot hold other tags in SCDoc, thus code, math, links, footnotes, citations, and bold or italic text in the header row stop the conversion. The alignment of the columns is not used.

```markdown
| Parameter | Range |
|---|---|
| `freq` | 20 to 20000 |
```

gives

```
table::
## strong::Parameter:: || strong::Range::
## code::freq:: || 20 to 20000
::
```

## Images

An image alone in a paragraph, `![caption](path)`, gives `image::path#caption::`. With no caption, it gives `image::path::`. SCDoc shows the caption below the image.

The path is relative to the schelp file. SCDoc copies the files in the `HelpSource` folder that are not schelp files to the help folder, thus put the image file next to the schelp file (for example in `HelpSource/Classes/images/`). md2misc does not copy files.

These stop the conversion: an image in a line of text, a URL or an absolute path, a `#` in the caption or the path (SCDoc splits the tag at `#`), and markup in the caption. A width (`{ width="50%" }`) is not used.

## Block quotes

SCDoc has no tag for a block quote. A block quote that is not an alert gives its paragraphs in italics, with quotation marks at the start of the first paragraph and at the end of the last one, as in the JITLib overview of SuperCollider. A line with `>` alone separates the paragraphs.

```markdown
> The first paragraph.
>
> The second paragraph.
```

gives

```
emphasis::"The first paragraph.::

emphasis::The second paragraph."::
```

Italic text cannot hold other tags in SCDoc: thus code, math, links, footnotes, citations, bold or italic text, lists, headings, code blocks and block quotes in a block quote stop the conversion. The source of a quote is not part of the quote: write it after the block quote, as a paragraph or a footnote.

## Footnotes

`[^1]` and `[^1]: text` give `footnote::text::` at the place of the mark. SCDoc puts the footnotes at the end of the page. A footnote can have more than one line and more than one paragraph: the lines of a later paragraph have an indent of 4 spaces or a tab. A list, a code block or another block in a footnote stops the conversion.

SCDoc does not find a tag directly after a letter, but it removes the space before a footnote mark. Thus md2misc puts a space between a letter and `footnote::`.

## Citations

With the `bibliography` argument, a citation gives a footnote, in the manner of Wikipedia. md2misc runs the program `pandoc` to write the citations, with Pandoc's built-in style (Chicago author-date). `pandoc` must be on the `PATH`, or the environment variable `PANDOC` must give its path. A text without citations does not run `pandoc`.

| Markdown | The footnote |
|---|---|
| `[@doe1999]`, the first citation of the source | `Doe, Jane. 1999. emphasis::Sound and Wood::. Acme.` |
| `[@doe1999, 30]` | `Doe, Jane. 1999. …, p. 30.` |
| `[@doe1999, 30-35]` | `Doe, Jane. 1999. …, pp. 30–35.` |
| `[@doe1999, p. 31]`, a later citation of the source | `Doe 1999, 31.` |
| `[@doe1999; @smith2000]` | the parts of the two sources, separated by `;` |

- The first citation of a source gives its reference entry, with the locator. A later citation gives the short form. There is no list of references: SCDoc puts the footnotes at the end of the page.
- A locator that is not a page or pages is written as it is: `[@doe1999, chap. 2]`.
- `[-@doe1999]` is the same as `[@doe1999]`: a footnote does not name the author in the text.
- A citation in a footnote gives the short form in parentheses: `(Doe 1999, 30)`. SCDoc cannot put a footnote in a footnote.
- If the bibliography has two works of one author and year, the style tells them apart: `1999a`, `1999b`.

These stop the conversion: a citation without a `bibliography` (write the citation as text, or give a bibliography), a key that is not in the bibliography, and a citation in another form. A citation in a heading, in bold or italic text, in a block quote or in the header row of a table also stops the conversion.

The TeX backend writes the same citations as `\parencite` (biblatex), with no `pandoc`.

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
| `[^1]` and `[^1]: note` | `footnote::note::` at the place of the mark (see [Footnotes](#footnotes)) |
| `[@key]` and a `bibliography` | `footnote::` with the reference (see [Citations](#citations)) |
| a pipe table | `table::` (see [Tables](#tables)) |
| `![caption](path)` alone in a paragraph | `image::path#caption::` (see [Images](#images)) |
| `> text` | `emphasis::"text"::` (see [Block quotes](#block-quotes)) |
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
- alerts of a kind that is not known (`> [!FOO]`), and markup or blocks in a block quote (see [Block quotes](#block-quotes))
- links that are not `http` URLs or `sc:` links, links in `<` and `>`, a `#` in the text of a link (SCDoc splits a link at each `#`; a link without a label, where the text is the address or the name of the page, is fine), and more than one `#` in the address of a link
- citations without a bibliography (see [Citations](#citations)), audio files, HTML tags and HTML comments (other than insertion points), `<br>` tags
- images that are not alone in a paragraph, or not at a relative path (see [Images](#images))
- tables that GFM renderers read in different ways, markup in the header row of a table, and tables in a methods section that are not the argument table of a method (see [Methods](#methods) and [Tables](#tables))
- horizontal rules (`---`, `***`, `___`)
- lists with `*` or `+` marks, and numbered lists with `1)`
- a list, a code block or another block in a footnote
- a title or highlighted lines in a code block
- bold or italic text, code, math, a link, a footnote or a citation in a heading
- bold or italic text that holds code, math, a link, a footnote, a citation or other bold or italic text

## Limits of SCDoc

SCDoc writes HTML, but its markup has no tag for some elements of HTML:

- a horizontal rule (`<hr>`): `---`, `***` and `___` stop the conversion.
- a block quote (`<blockquote>`): md2misc writes the quote in italics (see [Block quotes](#block-quotes)).
- the header row of a table (`<th>`): md2misc writes the header row in bold (see [Tables](#tables)).
- the width of an image.
