from ntpath import basename
import click
import re
import os

from .core import convert, convert_schelp, default_template
from .errors_warnings import DocumentError, InputException, UnsupportedConstruct, Warnings


@click.group("md2misc")
def main():
    """
    convert Markdown to other formats. each output format has its own subcommand.
    """


@main.command("tex")
@click.argument("inpath")
@click.option("-o", "--output-path", "outpath", default=None,
              help="optional. a custom output path. defaults to `output/{input_file_name}.tex`.")
@click.option("-c", "--complete-tex-file", "tex", is_flag=True, default=False,
              help="optional. if provided, a complete TeX file will be created from a template (with "
              + "preamble and tables of content). if not provided, only the contents of the markdown "
              + "file are translated. can be used with `-t` to use a custom, user-provided TeX template. "
              + "defaults to `False`.")
@click.option("-t", "--custom-tex-template", "template", default=None,
              help="optional. if provided, a custom TeX template will be used to create a complete TeX file. "
                   + "this argument must be used with `-c` and the TeX template must contain a "
                   + "`@@BODYTOKEN@@` between its `\\begin{document}` and `\\end{document}` "
                   + "to perform the replacement. "
                   + "defaults to the template that is part of the package.")
@click.option("-u", "--unumbered-headers", "unnumbered", is_flag=True, default=False,
              help="optional. if provided, Markdown headers will be translated as TeX unnumbered headers/sections"
                   + "defaults to False: the headers are numbered by default.")
@click.option("-d", "--document-class", "document_class", default="article",
              help="optional. sets the class of the TeX document. possible values "
                   + "are: `book`|`article`. defaults to `article`")
@click.option("-s", "--stdout", "write_stdout", is_flag=True, default=False,
              help="optional. if provided, output wil be written to stdout instead of the output path.")
@click.option("-l", "--minted-language", "minted_language", is_flag=False,
              default="text",
              help="optional. if provided, the string is used to specify language for source code highlighting within `minted` environments.")
@click.option("-O", "--override-language", "override_language", is_flag=True, default=False,
              help="optional. if provided, existing language specification in code blocks will be overridden with the language specified with --minted-language.")
def tex(
        inpath: str,
        outpath=None,
        tex=False,
        template=None,
        unnumbered=False,
        document_class="article",
        write_stdout=False,
        minted_language="text",
        override_language=False
):
    r"""
    convert a Markdown file to a TeX file.

    \b
    parameters (see options if you are in `--help` mode):
    -----------------------------------------------------
    :param inpath: the path to the *.md file to convert to tex
    :param outpath: the path to save the file to
    :param tex: a flag indicating wether to create a full tex file,
                with preamble and table of contents
    :param template: a custom TeX template to use for the conversion, in order
                     to add extra packages and whatnot. the contents of
                     \begin{document} - \end{document} should be empty, except for a
                     title page; this part must contain a "@@BODYTOKEN@@" string to be
                     able to append the TeX body to the template.
    :param unnumbered: wether to convert headers as numbered chapters/sections (`\chapter{}`)
                     or as unnumbered ones (`\chapter*{}`). defaults to False:
                     the headers are numbered by default.
    :param document_class: the document class of the tex document. defaults to `article`
    :param write_stdout: whether to write the output to stdout instead of a file
    :param minted_language: the default language for minted code blocks
    :param override_language: whether to replace the language of every code block with `minted_language`
    :return: None
    """
    # ==================== PROCESS THE ARGUMENTS ==================== #
    if not re.search(r"\.md$", inpath):
        raise InputException("not_md", inpath)
    if not os.path.isfile(inpath):
        raise InputException("not_inpath", inpath)
    if outpath is None:
        outpath = "output/" + re.sub(r'\..+?$', '.tex', basename(inpath))  # build default outpath
    elif "/" in outpath and "\\" in outpath:
        raise InputException("outpath_slashes", outpath)  # gnu-linux escapes backslashes so this shouldn't be called
    elif os.path.isdir(outpath):  # if the output path is a dir and not a file, save the file to that dir
        outpath = f"{outpath}/{basename(inpath)}"
    if not re.search(r"\.tex$", outpath):
        # add a .tex extension if it doesn't exist or if a different extension was
        # provided by the user
        Warnings("outpath_extension", outpath)
        outpath = re.sub(r"$", ".tex", outpath)
    if not re.search("^(book|article)$", document_class):
        raise InputException("document_class", document_class)

    # build output directory
    if not os.path.exists("./output"):
        os.makedirs("./output")

    # open file and read contents
    with open(inpath, mode="r") as fh:
        data = fh.read()
        data = convert(data, unnumbered, document_class, minted_language, override_language)

    # ==================== BUILD + WRITE OUTPUT TO FILE ==================== #
    if write_stdout:
        print(data)
    else:
        if tex is True:  # create full tex file.
            if template is None:
                tex_template = default_template()
            else:
                try:
                    with open(template, mode="r") as fh:
                        tex_template = fh.read()
                except FileNotFoundError:
                    raise InputException("not_template", template)
            if "@@BODYTOKEN@@" not in tex_template:
                raise InputException("template_no_token", template or "the default template")
            data = tex_template.replace("@@BODYTOKEN@@", data)
            data = data.replace("@@DOCUMENTCLASSTOKEN@@", document_class)
        try:
            with open(outpath, mode="w") as fh:
                fh.write(data)
                click.echo(f"FINISHED - file conversion completed and saved to `{outpath}`")
        except FileNotFoundError:
            raise InputException("not_outpath", outpath)

    return


def _output_name(inpath: str, extension: str) -> str:
    """
    the name of the output file: the name of the input file, with `extension` in place of `.md`.
    """
    return os.path.splitext(basename(inpath))[0] + extension


def _pairs(options, what: str) -> dict:
    """
    the `name=value` options of a command as a dict.
    """
    pairs = {}
    for option in options:
        name, equals, value = option.partition("=")
        if not equals or not name.strip():
            raise DocumentError(f"`{option}` is not of the form {what}")
        pairs[name.strip()] = value
    return pairs


@main.command("schelp")
@click.argument("inpath")
@click.option("-o", "--output-path", "outpath", default=None,
              help="optional. a custom output path. defaults to `output/{input_file_name}.schelp`.")
@click.option("-s", "--stdout", "write_stdout", is_flag=True, default=False,
              help="optional. if provided, output wil be written to stdout instead of the output path.")
@click.option("-m", "--meta", "meta", multiple=True, metavar="KEY=VALUE",
              help="optional, can be repeated. a value for the header of the document, that takes the place of the "
                   + "front matter value with the same key. the keys are `title`, `class`, `summary`, `related` and "
                   + "`categories`; the last two take a list with commas. for example `--meta class=PhysWoodbar`.")
@click.option("-i", "--insert", "insert", multiple=True, metavar="NAME=FILE",
              help="optional, can be repeated. the schelp text in FILE takes the place of the line "
                   + "`<!-- md2misc: NAME -->` in the Markdown file.")
def schelp(inpath: str, outpath=None, write_stdout=False, meta=(), insert=()):
    """
    convert a Markdown file to a SuperCollider help (schelp) document.

    the header of the document (`TITLE::` or `CLASS::`, `SUMMARY::`, `RELATED::`, `CATEGORIES::`) comes from the
    front matter of the file, its first level 1 heading and the `--meta` options. a file with none of these
    gives the body of the document only.
    a Markdown construct that has no schelp form stops the conversion with an error.
    """
    if not re.search(r"\.md$", inpath):
        raise InputException("not_md", inpath)
    if not os.path.isfile(inpath):
        raise InputException("not_inpath", inpath)

    insertions = {}
    for name, path in _pairs(insert, "NAME=FILE").items():
        try:
            with open(path, mode="r") as fh:
                insertions[name] = fh.read()
        except FileNotFoundError:
            raise DocumentError(f"the file `{path}` for the insertion point `{name}` was not found")

    with open(inpath, mode="r") as fh:
        try:
            data = convert_schelp(fh.read(), _pairs(meta, "KEY=VALUE"), insertions)
        except UnsupportedConstruct as error:
            error.message = error.describe(inpath)  # name the file and the line
            raise

    if write_stdout:
        click.echo(data, nl=False)
        return

    if outpath is None:
        os.makedirs("output", exist_ok=True)
        outpath = os.path.join("output", _output_name(inpath, ".schelp"))
    elif os.path.isdir(outpath):  # if the output path is a dir and not a file, save the file to that dir
        outpath = os.path.join(outpath, _output_name(inpath, ".schelp"))
    try:
        with open(outpath, mode="w") as fh:
            fh.write(data)
    except FileNotFoundError:
        raise InputException("not_outpath", outpath)
    click.echo(f"FINISHED - file conversion completed and saved to `{outpath}`")
