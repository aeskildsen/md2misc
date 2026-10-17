# The `md2misc` command

The command is a thin layer over the Python functions. Use the library in scripts and CI jobs. Use the command for a single conversion by hand.

```bash
pipx install git+https://github.com/aeskildsen/md2misc
md2misc --help
md2misc tex --help
md2misc schelp --help
```

Each backend has a subcommand.

## `md2misc tex`

```bash
md2misc tex path/to/file.md [options]
```

The argument is the path to a Markdown file. The name of the file must end with `.md`.

| Option | Python argument of `convert` | Meaning |
|---|---|---|
| `-o`, `--output-path` | | Path of the `.tex` file. The default is `output/<input name>.tex` in the current folder. The folders of the path must exist. A `.tex` extension is added if the path has another extension. |
| `-s`, `--stdout` | | Write the TeX to standard output. Warnings go to standard error. |
| `-c`, `--complete-tex-file` | | Write a complete document, with preamble and table of contents. Without it, only the body is written. |
| `-t`, `--custom-tex-template` | | Path of a template for `-c`. The template must contain `@@BODYTOKEN@@`. It can contain `@@DOCUMENTCLASSTOKEN@@` in `\documentclass{...}`. |
| `-d`, `--document-class` | `document_class` | `article` (default) or `book`. |
| `-u`, `--unumbered-headers` | `unnumbered` | Write `\section*{}` and not `\section{}`. |
| `-l`, `--minted-language` | `minted_language` | Language for `minted` (default `text`). |
| `-O`, `--override-language` | `override_language` | Give every code block the language of `-l`. In `md2tex` this option used the short flag `-o`, which clashed with `--output-path`. |

The options `-o`, `-s`, `-c` and `-t` have no Python argument: the library returns the body, and the caller writes the file. The default template is in `md2misc/templates/template.tex`.

Examples:

```bash
# a complete article with unnumbered headers and the default template
md2misc tex README.md -c -u -o README.tex

# a complete book with a custom template
md2misc tex README.md -c -t my_template.tex -d book -o README_book.tex

# the body only, to the terminal
md2misc tex README.md -s
```

## `md2misc schelp`

```bash
md2misc schelp path/to/file.md [options]
```

| Option | Python argument of `convert_schelp` | Meaning |
|---|---|---|
| `-o`, `--output-path` | | Path of the `.schelp` file. The default is `output/<input name>.schelp`. |
| `-s`, `--stdout` | | Write the schelp to standard output. |
| `-m`, `--meta KEY=VALUE` | `metadata` | A header value. It replaces the front matter value with the same key. Can be repeated. |
| `-i`, `--insert NAME=FILE` | `insertions` | Put the text of FILE at the insertion point `NAME`. Can be repeated. |

A construct that has no schelp form shows an error with the file, the line and the construct, and the command exits with a non-zero status. See [schelp.md](schelp.md).
