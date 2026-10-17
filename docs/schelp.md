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

A Markdown construct that has no schelp form raises an error that names the file, the line and the construct. See [below](#constructs-that-stop-the-conversion).

## The header

The header tags come from three places:

1. The front matter at the start of the Markdown file: a block of `key: value` lines between two lines with `---`. The keys are `title`, `class`, `summary`, `related` and `categories`. `related` and `categories` take a list: `[a, b]`, lines with `- item` below the key, or a string with commas.
2. The first level 1 heading (`# Title`). It gives the `TITLE::` if the front matter has no `title` and no `class`. Otherwise it is left out. A second level 1 heading stops the conversion.
3. The `metadata` argument (`--meta KEY=VALUE` on the command line). Use it for a value that the Markdown file does not know, like the class name: `metadata={"class": "PhysWoodbar"}`.

The header is `CLASS::`, `TITLE::` (both, if both are given), `SUMMARY::`, `RELATED::` and `CATEGORIES::`, in this order. In a value, `::` gets a backslash. `##` and `||` stop the conversion, because SCDoc cannot show them in a header line.

A file with no front matter, no level 1 heading and no metadata gives the body only. A header with no title and no class stops the conversion.

## Special sections and insertion points

A level 2 heading `## Description` gives `DESCRIPTION::`, and `## Examples` gives `EXAMPLES::`. Any other level 2 heading gives `SECTION::`.

A line `<!-- md2misc: NAME -->` is an insertion point. Markdown viewers do not show the comment. The `insertions` argument (`--insert NAME=FILE`) puts the schelp text in its place, as it is. A program that writes the `CLASSMETHODS::` section can use this to put it between the description and the examples.

An insertion point with no text gives nothing. Text for a name that the file does not have stops the conversion.

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
- citations, images and audio files, tables, HTML tags and HTML comments (other than insertion points), `<br>` tags
- horizontal rules (`---`, `***`, `___`)
- lists with `*` or `+` marks, and numbered lists with `1)`
- a footnote with more than one line
- a title or highlighted lines in a code block
- bold or italic text, code, math, a link or a footnote in a heading
- bold or italic text that holds code, math, a link, a footnote or other bold or italic text
