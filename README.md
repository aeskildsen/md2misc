# `md2misc` - a CLI to convert Markdown to other formats

`md2misc` converts Markdown to other text formats. Rather than using fancy object oriented libraries, it locates elements of Markdown syntax using regular expressions and translates them into the target syntax. It has only been tested with latin script so far.

Each output format is a *backend* with its own subcommand:

| Backend | Subcommand | Status |
|---|---|---|
| TeX | `md2misc tex` | available |
| SuperCollider help (schelp) | `md2misc schelp` | available: a whole document, with header and special sections; more constructs may follow |

## Origin

`md2misc` is derived from [`md2tex`](https://github.com/paulhectork/md2tex) by Paul Kervegan. The full history of `md2tex`, with the commits of both authors, is part of this repository's git history. See `NOTICE` for details. The TeX output is meant to stay identical to the output of `md2tex`.

---

## Features
- Translation from Markdown to TeX
- Creation of a complete and valid TeX document, either from a generic template or using your own 
  template
- Reading Markdown from custom locations and writing a TeX file to a custom location
- Several options for extra customization: numbered or unnumbered headers, document classes, etc. ...
- Core functionality (converting Markdown to TeX) can be used in other Python scripts as a module
---

## Commands / How to 

### Requirements

The TeX output relies on the [`minted`](http://tug.ctan.org/macros/latex/contrib/minted/minted.pdf) package for code blocks, so this needs to be installed on your machine. The tool has been tested on a Linux machine and should work on UNIX and affiliated systems. It has not been tested on Windows.

The TeX output requires a number of LaTeX packages, including:
- csquotes

### Installation

md2misc needs Python 3.10 or later. Its only dependency is `click`.

With pipx, as a command line tool:

```bash
pipx install git+https://github.com/aeskildsen/md2misc
md2misc tex path/to/file.md
```

With pip, from a checkout of this repository:

```bash
pip install .
md2misc tex path/to/file.md
```

### Base functionning
```bash
md2misc tex path/to/markdown/file.md --options
```

### Arguments and options of `md2misc tex`

#### Argument
The only **compulsory argument** is the path to the markdown file that needs to be processed.
- The file must finish with `.md` so that we're sure that a markdown file is being processed.

#### Optional parameters
All of the below parameters are optional.
- **`-o`, `--output-path`**: give a specific path and filename to write the `.tex` file to?
	- if none is provided, the output path defaults to `output/input_filename.tex` in the current folder
	- if the output path contain directories that do not exist, the output will not be 
	  written. Directories must be created manually beforehand.
    - if the extension of the output file is not `.tex`, a `.tex` extension will be added to the filename.
- **`-c`, `--complete-tex-file`**: if provided, a complete TeX file will be created, with preamble and table of
  contents. 
	- the default template is part of the package. For a custom template, see `-t` below.
	- if not provided, only the body of the Markdown file will be converted. It will need to be included
	  in another file with a premable.
- **`-t`, `--custom-tex-template`**: the path to a custom TeX template to build a complete document from, instead
  of the default template.
	- this argument must be used in conjunction with `-c` for an actual template to be used.
	- a path to an existing template must be provided.
	- this template must contain the string `@@BODYTOKEN@@`: this token will be replaced by the contents of the
	  converted Markdown file.
	- the document class can also be defined in the document by the CLI: 
	  in the template's preamble, write `documentclass{@@DOCUMENTCLASSTOKEN@@}`.
- **`-d`, `--document-class`**: this argument indicates the class of the final TeX document. it indicates 
  wether to process the Markdown file as a LaTeX `book` or as an `article`.
	- defaults to `article`.
	- if used with a custom TeX template (see `-c` and `-t`), the template must contain an `@@DOCUMENTCLASSTOKEN@@`
	  in the preamble where the document class is specified so that the TeX document class can actually change.
	- in fact, this argument only impacts the headers used in the TeX template.
- **`-u`, `--unnumbered-headers`**: if this argument is provided, the TeX headers (`\chapter`, `section`...)
  will be unnumbered.
	- by default, the headers are numbered.
- **`-s`, `--stdout`**: write the TeX to standard output instead of a file. Warnings go to standard error.
- **`-l`, `--minted-language`**: the language that `minted` uses for syntax highlighting (default `text`).
- **`-O`, `--override-language`**: replace the language of every code block with the language from `-l`.
	- in `md2tex` this option also used the short flag `-o`, which clashed with `--output-path`. In `md2misc` the short flag is `-O`.

### Command line help
```bash
md2misc --help
md2misc tex --help
```

---

## Examples

A complete article with unnumbered headers and the default template:
```bash
md2misc tex README.md -c -u -o README.tex
```

A complete book with a custom template and numbered headers:
```bash
md2misc tex README.md -c -t my_template.tex -d book -o README_book.tex
```

A partial TeX file (body only), printed to the terminal:
```bash
md2misc tex README.md -s
```

Example outputs of the original `md2tex` (TeX and PDF files made from the `md2tex` README) are in the git history of this repository.

## Usage in other Python scripts

The core functionality (conversion from Markdown to TeX) can be used in other Python scripts like this:
```python
from md2misc import convert

markdown = "# A title"
tex = convert(markdown)
print(tex)  # Prints: \section{A title}
```

The `convert` function takes four optional, additional arguments corresponding to the `tex` command line arguments: `unnumbered` (`--unnumbered-headers`), `document_class` (`--document-class`), `minted_language` (`--minted-language`) and `override_language` (`--override-language`).

## The schelp output

`md2misc schelp in.md` writes a SuperCollider help document (the markup that SCDoc renders to HTML). The options are `-o`/`--output-path`, `-s`/`--stdout`, `-m`/`--meta KEY=VALUE` and `-i`/`--insert NAME=FILE`. In Python: `from md2misc import convert_schelp`.

### The header

The header tags come from three places:

1. The front matter at the start of the Markdown file, a block of `key: value` lines between two lines with `---`. The keys are `title`, `class`, `summary`, `related` and `categories`. `related` and `categories` take a list: `[a, b]`, lines with `- item` below the key, or a string with commas.
2. The first level 1 heading (`# Title`). It gives the `TITLE::` if the front matter has no `title` and no `class`; otherwise it is left out. A second level 1 heading stops the conversion.
3. The `--meta KEY=VALUE` options (the `metadata` argument in Python). A value given here takes the place of the front matter value with the same key. Use this for a value that the Markdown file does not know, like the class name `--meta class=PhysWoodbar`.

The header is `CLASS::`, `TITLE::` (both are written if both are given), `SUMMARY::`, `RELATED::` and `CATEGORIES::`, in this order. In a value, `::` gets a backslash; `##` and `||` stop the conversion, because SCDoc cannot show them in a header line. A file with no front matter, no level 1 heading and no `--meta` gives the body of the document only. A header with no title and no class stops the conversion.

### Special sections and insertion points

A level 2 heading `## Description` gives `DESCRIPTION::` and `## Examples` gives `EXAMPLES::`. Any other level 2 heading gives `SECTION::`.

A line `<!-- md2misc: NAME -->` is an insertion point. Markdown viewers do not show the comment. `--insert NAME=FILE` (the `insertions` dictionary in Python) puts the schelp text of FILE in its place, as it is. This is how a program that writes the `CLASSMETHODS::` section puts it between the description and the examples. An insertion point that gets no text gives nothing; text for a name that the file does not have stops the conversion.

### The body

| Markdown | schelp |
|---|---|
| `## Heading` | `SECTION::Heading` (`## Description` and `## Examples` are special, see above) |
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

In text, `::`, `##` and `||` get a backslash, because SCDoc takes them as markup. In code, only a `::` inside inline code and a line with `::` alone in a code block get a backslash. If the text of an inline tag (bold, italic, inline code, a link, inline math, a footnote) ends with `:` or `\`, a space comes before the end-tag `::`, because SCDoc takes the character as part of the end-tag. SCDoc does not show the space.

Three Markdown rules of the schelp output are those of CommonMark and Pandoc, not those of the TeX output:

- A heading needs a space after the `#` characters: `#1 priority` at the start of a line is text.
- Inline math follows the rules of Pandoc: no space after the first `$` and before the second `$`, and no digit after the second `$`. Thus `$5 and $10` is text. `\$` is a dollar sign.
- A code block can be in an alert: the `>` marks are not part of the code.

A Markdown construct that has no schelp form stops the conversion: the command shows an error that names the file, the line and the construct, and exits with a non-zero status. This holds for:

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

The `sc:` address is the one convention that only md2misc understands. The rest is Markdown that GitHub shows as it is.

The schelp fixtures are in `tests/schelp/`. The tests let headless `sclang` parse and render the output with SCDoc and compare the HTML; see Tests below.

---

## Tests

The tests use pytest. In a virtual environment, from a checkout of this repository:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e ".[test]"
python3 -m pytest              # all tests
python3 -m pytest -k schelp    # the schelp tests
```

The tests of the SCDoc output run headless `sclang` (SuperCollider). They are skipped if `sclang` is not on `PATH` or in the `SCLANG` environment variable, thus a contributor to another backend does not need SuperCollider. With `MD2MISC_REQUIRE_SCLANG=1`, a missing `sclang` is an error and not a skip.

All versions of `sclang` must parse the schelp output with no error and give the expected parts of the pages. The `.html` files hold whole pages of the SuperCollider version in `tests/schelp/SCLANG_VERSION`; the tests compare whole pages only with that version.

GitHub Actions (`.github/workflows/tests.yml`) runs all tests against the installed package with several Python versions, and the SCDoc tests with the SuperCollider of Ubuntu.

- `tests/test_tex_battery.py`: the TeX output is the same as the output of md2tex, for the fixtures in `tests/fixtures` (pages of a book and the md2tex README, with a coverage table in `tests/COVERAGE.md`).
- `tests/test_schelp_golden.py`: the schelp output is the same as the `.schelp` files in `tests/schelp`.
- `tests/test_schelp_render.py`: SCDoc renders the schelp output to the HTML in the `.html` files in `tests/schelp`, with the sections in order. SCDoc also renders the cases in `tests/schelp_cases.py` (`RENDERS` and `SUPPORTED`) with no error, and the pages hold the expected HTML.
- `tests/test_schelp_errors.py`: the constructs without a schelp form stop the conversion with the file, line and construct, and look-alikes in code are accepted.
- `tests/test_schelp_writer.py`: the writers of the schelp backend stop at the constructs too, when the check of the source does not find them.
- `tests/test_schelp_behavior.py`, `tests/test_schelp_cli.py` and `tests/test_tex_cli.py`: the output of single cases, and the commands.

The fixture files that are made by a tool:

- `python3 tests/battery.py build` makes the TeX fixtures. It needs `pip install -e ".[battery]"` and private checkouts of the book that the fixtures come from, thus contributors do not run it: the `.tex` files are the frozen reference (the output of md2tex).
- `python3 tests/schelp_fixtures.py update` makes the `.schelp` and `.html` files and `SCLANG_VERSION`. Read the diff afterwards. After an update of SuperCollider, the HTML can change: make the files again and read the diff.

---

## Markdown syntax

### Currently supported

- Line breaks: paragraph changes using `\n\n`, `<br>` and `<br/>`
- Different styles of text: **bold**, *italic* and `inline code`. **Warning**:
  - only bold and italics made using asterisks will be translated.
- Block quotes (lines beginning with `>`). **Warning**: only non-nested block quotes -- or the outer
  level of a nested block quote --  will be rendered.
- Multiline code; if possible, the code is colored using `minted`. Indentation levels are **always**
  respected within multiline code.
- Ordrered and unordered lists, including nested lists. **Warning**:
  - To be processed, all indentation levels must be a multiplier of the indentation of the first
    indented item. See below for details on how nested lists are handled.
  - Unordered lists will only be converted if they begin with `-`. any other list token
    will be ignored.
  - The only list token replaced in ordered lists is `\d+.` (digits followed by a point: `1.`).
    If an other list token is used (a letter...), the numbered list won't be processed.
    If additional tokens are added (for nested lists: `1. a.`), the list will be processed, but
    the second token (`a.`) will not be deleted. This is because the use of additional tokens is
    specific to the Markdown interpreter used.
- Definition lists
- Titles and different title levels
- Images
- URLs, both in text and as Markdown hyperlinks.
- Inline quotes
- Footnotes. **Warning**: loose footnotes (references in the body that point to nothing
  or footnotes that point to nothing in the body) will be deleted.
- Citations in pandoc-markdown style. **Warning**: Only rudimentary support.

### Currently unsupported

- Markdown tables
- Strikethrough
- Emojis
- Tasks lists
- Text blocks inside lists will be processed as the continuation
  of a list item

---

## Things that will mess with the output

The things in the list below will either cause the script to exit or produce a messy output.

- Poorly formed Markdown. If a list is not properly formed, the script will exit.
- Using things that are currently not supported.
- Incoherent use of header levels (`#`, `##`...) will be processed and render a valid document,
  but it will mess with the appearence of the TeX file and of the table of contents, especially
  if the headers are numbered.
- Unnumbered lists made using non-standard markdown syntax (lists not beginning with `-`...).
  These will simply not be matched.
- Numbered lists using additional numbering keys, such as `1. a`. These will be matched, but in this case, 
  `1.` will be deleted and replaced by TeX syntax; `a` will be kept, so the TeX file will contain double 
  numbering (the TeX numbering and this second numbering key)
- Highly nested lists are not supported by default in LaTeX, but this can be changed in your preamble.
- Multiple footnotes with the same key; for the footnote processing to work,
  there must be unique footnote numbers and only one note per footnote number.
- Loose footnotes that point to nothing will be deleted.

Clean your file first ! You can also make the bulk of the translation using this cli and fine tune your `.tex` 
file later on.

---

## About nested lists and visual indentation

List nesting and visual indentation is a bit of a pickle, so here's an explanation of how
the indentation is processed and what constitutes a valid list for this tool.

### What is a valid list?

All items must be **as indented than the first list item** or more. the indentation level of the first item
will be removed before processing that list. This means that *the first example* will result in the same
result as *the second*.
```
- list item with no leading space
- same here
```

```
  - list item with two leading spaces
  - same here, still a valid list
```

All indentation levels must be a multiple of the leading whitespaces of the first nested item. If the first nested 
list item is indented with 4 whitespaces, all nested items must be indented with a multiple of 4 spaces. For example,
a list item can't be indented with 3 spaces while another one is indented with 4 spaces.

The above two rules cause the script to exit with an error message pointing to the faulty list. On top of that,
in keeping with LaTeX and markdown logic, a list item can't skip a nesting level (you cannot go from an item in a list
to an item in a list in a list). This will **not** stop the script, the indentation will just be reset automatically.

```
- this is an item at level 0
  - this is an item at level 1; the indentation is set as 2 whitespaces
  - same here; level 1.
      - visually, this one seems indented as level 3 as it starts with 6 leading whitespaces.
        however, its nesting level will be reset from level 3 to level 2 to avoid skipping
        a nesting level
  - this item is at level 1
```

### Technically, how does it work ?
- The complete markdown list is matched.
- Each list item is mapped to its indentation level, in number of leading spaces.
- The list is validated. If it is not valid, the script stops.
- An indentation multiplier is defined: it is the number of spaces in the first nested list item.
- This multiplier is used to map each list item to its nesting level.
- The markdown is syntax is replaced by TeX syntax.

### Examples of valid and invalid lists

#### Valid lists
```
- item at level 0
- item at level 0
  - item at level 1. here, a 2-whitespace indentation is defined for the list.
    - item at level 2, with 4 leading spaces.
- item at level 0
```

```
     - item at level 0
     - item at level 0
```

```
- item at level 0
    - item at level 1. for this list, the indentation is set to 4 spaces.
            - visually, this item is at level 3 (12 leading spaces), but will be reindented to 2 spaces.
    - item at level 1.
```

#### Invalid lists
```
  - item at level 0
  - item at level 0
- this will cause the script to exit: the item is less indented than the first item.
```

```
- item at level 0
	- indentation is set at 4 spaces
	  - here, there are 6 spaces. the indentation is incoherent and the script stops.
```
          
---

## License and credits
Released under GNU GPL v3. `md2tex` was developed by Paul Kervegan in August 2022. Later additions to `md2tex` were made by Anders Eskildsen, and `md2misc` continues from there. See `NOTICE`.