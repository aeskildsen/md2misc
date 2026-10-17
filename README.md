# md2misc

`md2misc` is a Python library that converts Markdown to other text formats. It finds the elements of Markdown with regular expressions and writes them in the target syntax. It has only been tested with latin script.

Each output format is a *backend*:

| Backend | Function | Documentation |
|---|---|---|
| TeX | `convert` | [docs/tex.md](docs/tex.md) |
| SuperCollider help (schelp) | `convert_schelp` | [docs/schelp.md](docs/schelp.md) |

## Installation

`md2misc` needs Python 3.10 or later. Its only dependency is `click`.

```bash
pip install git+https://github.com/aeskildsen/md2misc
```

## Usage

```python
from md2misc import convert, convert_schelp

print(convert("# A title"))         # \section{A title}
print(convert_schelp("## A title")) # SECTION::A title
```

Both functions take a string and return a string. For example, in a CI job:

```python
from pathlib import Path
from md2misc import convert_schelp

source = Path("docs/MyClass.md")
target = Path("Help/MyClass.schelp")

markdown = source.read_text()
schelp = convert_schelp(markdown, metadata={"class": "MyClass"})

target.write_text(schelp)
```

The package also installs a small `md2misc` CLI for one-off conversions. See [docs/cli.md](docs/cli.md).

## Documentation

- [docs/tex.md](docs/tex.md): the TeX backend, the supported Markdown and the rules for lists
- [docs/schelp.md](docs/schelp.md): the schelp backend, the header, the insertion points and the constructs that stop the conversion
- [docs/cli.md](docs/cli.md): the `md2misc` CLI command
- [docs/development.md](docs/development.md): how to run the tests

## Origin

`md2misc` is derived from [`md2tex`](https://github.com/paulhectork/md2tex) by Paul Kervegan. The full history of `md2tex`, with the commits of both authors, is part of the git history of this repository. The TeX output is meant to stay identical to the output of `md2tex`. See `NOTICE`.

## License and credits

Released under GNU GPL v3. `md2tex` was developed by Paul Kervegan in August 2022. Later additions to `md2tex` were made by Anders Eskildsen, and `md2misc` continues from there. See `NOTICE`.
