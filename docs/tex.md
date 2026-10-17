# The TeX backend

```python
from md2misc import convert

tex = convert(markdown, unnumbered=False, document_class="article",
              minted_language="text", override_language=False)
```

`convert` returns the body of a TeX document. The output is the same as the output of `md2tex`.

| Argument | Meaning |
|---|---|
| `unnumbered` | Write `\section*{}` and not `\section{}`. |
| `document_class` | `article` (default) or `book`. It changes the heading commands: `\chapter` is used only for `book`. |
| `minted_language` | The language of code blocks that have none (default `text`). |
| `override_language` | Give every code block `minted_language`. |

For a complete document, put the body in a template. `md2misc.core.default_template()` returns the text of the default template. The body goes where the template has `@@BODYTOKEN@@`.

## Requirements

Code blocks use the [`minted`](http://tug.ctan.org/macros/latex/contrib/minted/minted.pdf) package. The output also needs other LaTeX packages, for example `csquotes`. The default template loads them.

## Supported Markdown

- Paragraphs, and line breaks with `<br>` and `<br/>`
- **Bold** and *italic* with asterisks, and `inline code`
- Block quotes. Only the outer level of a nested block quote is rendered.
- Fenced code blocks. Indentation is kept.
- Ordered and unordered lists, nested lists too (see below)
- Definition lists
- Headings of different levels
- Images
- URLs, in text and as Markdown links
- Inline quotes
- Footnotes. A reference with no note, and a note with no reference, are deleted.
- Math, with `$x$` and `$$` blocks
- Citations in the style of Pandoc. The support is basic.

Not supported: tables, strikethrough, emojis, task lists. A text block inside a list item is taken as a continuation of the item.

## What gives a bad output

- Badly formed Markdown. A badly formed list stops the conversion.
- Unsupported constructs.
- Heading levels that skip. The output is valid, but the look of the document and of the table of contents is odd, especially with numbered headings.
- Lists with other marks than `-` (unordered) or `1.` (ordered). The unordered ones are not found. For ordered lists with a second mark (`1. a.`), the second mark stays in the text, and the list has two numberings.
- Lists nested deeper than LaTeX allows. You can change the limit in the preamble.
- Two footnotes with the same key.

Clean the Markdown first. You can also do most of the work with `md2misc` and fix the `.tex` file by hand.

## Lists

### What is a valid list?

Every item must have at least the indentation of the first item. `md2misc` removes the indentation of the first item before it reads the list. These two lists give the same result:

```
- item with no leading space
- another item
```

```
  - item with two leading spaces
  - another item
```

Every indentation must be a multiple of the indentation of the first nested item. If the first nested item has 4 spaces, a nested item cannot have 3 spaces.

A list that breaks one of these two rules stops the conversion, with a message that shows the list.

An item cannot skip a nesting level. If it does, `md2misc` sets the level back and does not stop:

```
- level 0
  - level 1: the indentation is 2 spaces
  - level 1
      - this item has 6 spaces, which looks like level 3.
        It is set back to level 2.
  - level 1
```

### How it works

1. `md2misc` finds the whole list.
2. It gives each item its indentation, in spaces.
3. It checks the list. An invalid list stops the conversion.
4. The indentation of the first nested item is the multiplier.
5. With the multiplier, each item gets a nesting level.
6. The Markdown marks become TeX.

### Valid lists

```
- level 0
- level 0
  - level 1. The indentation of the list is 2 spaces.
    - level 2, with 4 spaces.
- level 0
```

```
     - level 0
     - level 0
```

```
- level 0
    - level 1. The indentation of the list is 4 spaces.
            - 12 spaces. This is set back to level 2.
    - level 1
```

### Invalid lists

```
  - level 0
  - level 0
- this item has less indentation than the first item.
```

```
- level 0
	- the indentation is 4 spaces
	  - 6 spaces. This is not a multiple of 4.
```
