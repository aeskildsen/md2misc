import importlib.resources

from .backends import SchelpBackend, TeXBackend
from .converters import MDSimple, MDQuote, MDList, MDCode, MDCleaner, MDReference, MDHeader, MDFrontmatter, MDInsertion, MDMedia, MDMath


def default_template() -> str:
    """
    return the text of the TeX template that is part of the package
    """
    return importlib.resources.files("md2misc").joinpath("templates/template.tex").read_text()


def convert(data, unnumbered=False, document_class="article", minted_language="text", override_language=False):
    r"""
    convert Markdown-formatted text to TeX code.

    \b
    parameters (see options if you are in `--help` mode):
    -----------------------------------------------------
    :param data: the string containing the markdown-formatted text
    :param unnumbered: whether to convert headers as numbered chapters/sections (`\chapter{}`)
                     or as unnumbered ones (`\chapter*{}`). defaults to False:
                     the headers are numbered by default.
    :param document_class: the document class of the tex document. defaults to `article`
    :param minted_language: the default language for minted code blocks
    :param override_language: whether to replace the language of every code block with `minted_language`
    :return: The converted TeX code
    """

    backend = TeXBackend(unnumbered, document_class, minted_language, override_language)
    return run_pipeline(data, backend)


def convert_schelp(data, metadata=None, insertions=None):
    """
    convert Markdown-formatted text to a SuperCollider help (schelp) document.

    the header of the document (`TITLE::` or `CLASS::`, `SUMMARY::`, `RELATED::`, `CATEGORIES::`) comes from the
    front matter of the text, the first level 1 heading and the `metadata`. a text with none of these
    gives the body of the document only.

    :param data: the string containing the markdown-formatted text
    :param metadata: a dict that takes the place of the front matter values with the same key: `title`, `class`,
                     `summary`, `related` and `categories` (a list or a string with commas)
    :param insertions: a dict that maps the name of an insertion point (a line `<!-- md2misc: name -->` in the
                     text) to the schelp text that takes its place
    :return: The converted schelp markup
    """
    backend = SchelpBackend(insertions)
    front_matter, data = backend.take_front_matter(data)
    body = run_pipeline(data, backend)
    backend.check_insertions()
    header = backend.header({**front_matter, **(metadata or {})})
    if body:
        return header + body
    # a header alone ends with one line ending
    return header.rstrip("\n") + "\n" if header else ""


def run_pipeline(data, backend):
    """
    convert Markdown-formatted text to the output format of `backend`.

    :param data: the string containing the markdown-formatted text
    :param backend: the output format
    :return: The converted text
    """
    backend.check_source(data)

    # complex replacements
    data = MDCode.block_code(data, backend)   #  the contents of code blocks and inline code strings
    data = MDCode.inline_code(data, backend)  #  must be interpreted verbatim. therefore,
    #                                            these functions come first so that they won't be changed
    #                                            by `prepare_markdown()`
    data = MDInsertion.apply(data, backend)   #  text of the caller is not changed, either
    data, mathdict = MDMath.stash_math(data, backend)
    data, codedict = MDCleaner.prepare_markdown(data, backend)  # remove code from the pipeline
    data = MDHeader.mark(data, backend)                #  headers are located before the text is escaped
    data = backend.escape(data)                        #  escape special chars
    data = MDFrontmatter.convert(data)
    data = MDMedia.image(data, backend)
    data = MDQuote.inline_quote(data, backend)
    data = MDQuote.block_quote(data, backend)
    data = MDList.unordered_l(data, backend)
    data = MDList.ordered_l(data, backend)
    data = MDReference.footnote(data, backend)
    data = MDReference.hyperlink(data, backend)
    data = MDReference.citation(data, backend)
    data = MDList.definition_l(data, backend)
    data = MDHeader.convert(data, backend)

    # "simple" replacements: bold, italics and the like
    data = MDSimple.convert(data, backend)
    data = MDCleaner.clean_output(data, codedict, backend)  # clean the output + reinject the escaped code blocks
    data = MDMath.restore_math(data, mathdict)
    return data
