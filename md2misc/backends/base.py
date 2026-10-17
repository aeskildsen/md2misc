from .. import syntax
from ..errors_warnings import UnsupportedConstruct


class Backend:
    """
    an output format. the converters find the Markdown elements and call the
    backend to write them in the target syntax.

    a backend must write the elements that every format has: `escape()`, `heading()`, `bold()`, `italic()`,
    `inline_code()`, `code_block()`, `stash_code()` and `clean()`. for the other elements, the default
    is to stop the conversion with an `UnsupportedConstruct` error. a backend that can write an element
    overrides the method.
    """

    # the name of the format, for messages
    name = "this"

    def unsupported(self, construct: str, line: int = None):
        """
        stop the conversion: the format has no way to write `construct`. `line` is the line of the construct in
        the Markdown text, if it is known.
        """
        raise UnsupportedConstruct(self.name, construct, line)

    # whether the backend can put text of the caller at the insertion points of the document
    supports_insertions = False

    # whether `clean()` runs before the stashed code is put back in the text (the code then stays as it is)
    clean_before_restore = False

    # the number of heading levels that the format tells apart. all deeper levels are written like the last one
    heading_groups = 1

    # the forms of a heading and of inline math in the Markdown (see `syntax`). the default is the form of md2tex
    heading_regex = syntax.HEADING
    inline_math_regex = syntax.INLINE_MATH

    # whether the quote marks (`>`) are removed from the lines of a code block in a block quote.
    # md2tex keeps them in the code
    strip_quote_marks_in_code = False

    def check_source(self, markdown: str):
        """
        look at the Markdown text before it is converted. a backend can stop the conversion with an
        `UnsupportedConstruct` error that holds the line of the construct, which the converters cannot know.
        the default is to do nothing.
        """

    def escape(self, string: str) -> str:
        """
        escape the characters of the whole text that have a special meaning in the target syntax.
        the text may contain stashed code and math tokens, which must stay as they are.
        """
        raise NotImplementedError

    def heading(self, level: int, text: str) -> str:
        """
        write a heading. `level` is the number of `#` characters (1 or more), `text` is the escaped heading text.
        the result includes the line ending.
        """
        raise NotImplementedError

    def bold(self, text: str) -> str:
        """
        write bold text. `text` is escaped.
        """
        raise NotImplementedError

    def italic(self, text: str) -> str:
        """
        write italic text. `text` is escaped.
        """
        raise NotImplementedError

    def block_quote(self, text: str) -> str:
        """
        write a block quote. `text` is the quoted lines, each line still starts with `>`.
        """
        self.unsupported("block quote")

    def remove_quote_marks(self, string: str) -> str:
        """
        remove the `>` marks of block quotes from the text, after the block quotes were written.
        the default is to leave the text as it is.
        """
        return string

    def inline_quote(self, text: str, nested: bool = False) -> str:
        """
        write text in quotation marks. `text` is escaped. `nested` is true for a quotation inside another quotation.
        """
        self.unsupported("quotation marks")

    def unordered_list(self, items: list) -> str:
        """
        write an unordered list. `items` is a list of `[text, level]`: the escaped
        text of each item and its nesting level, starting at 0. an item can be at most
        one level deeper than the item before it.
        """
        self.unsupported("unordered list")

    def ordered_list(self, items: list) -> str:
        """
        write an ordered list. `items` is the same as for `unordered_list()`, and the item
        numbers are removed from the text.
        """
        self.unsupported("ordered list")

    def definition_list(self, entries: list) -> str:
        """
        write a definition list. `entries` is a list of `(term, definition)` with escaped text.
        """
        self.unsupported("definition list")

    def horizontal_rule(self) -> str:
        """
        write a horizontal rule.
        """
        self.unsupported("horizontal rule")

    def line_break(self) -> str:
        """
        write the break that a `<br>` tag stands for.
        """
        self.unsupported("line break tag")

    def audio(self, path: str) -> str:
        """
        write the place of an audio file. `path` is escaped.
        """
        self.unsupported("audio file")

    def image(self, caption: str, path: str, width: str) -> str:
        """
        write an image. `caption` and `path` are escaped. `width` is a percentage of the text width, as digits.
        """
        self.unsupported("image")

    def link(self, url: str, text: str) -> str:
        """
        write a link to an external URL. `url` and `text` are escaped.
        """
        self.unsupported("link")

    def insertion(self, name: str) -> str:
        """
        write what the caller gave for the insertion point `name`. only called if `supports_insertions` is true.
        """
        raise NotImplementedError

    def internal_link(self, target: str, text: str):
        """
        write a link to a target that is not an external URL (a page or a file, for example).
        `target` and `text` are escaped. return `None` to leave the link as it is in the text.
        """
        return None

    def footnote(self, text: str) -> str:
        """
        write a footnote mark with its text. `text` is escaped.
        """
        self.unsupported("footnote")

    def citation(self, key: str, locator: str = None, is_range: bool = False, omit_author: bool = False) -> str:
        """
        write a citation of one source. `locator` is a page number, or a range of pages if
        `is_range` is true. `omit_author` is true if the author must not be named.
        """
        self.unsupported("citation")

    def citations(self, keys: str) -> str:
        """
        write a citation of several sources. `keys` is the keys of the sources, separated by commas.
        """
        self.unsupported("citation")

    def inline_math(self, expression: str) -> str:
        """
        write a math expression in a line of text. `expression` is not escaped.
        """
        self.unsupported("inline math")

    def display_math(self, expression: str) -> str:
        """
        write a math expression on its own lines. `expression` is not escaped.
        """
        self.unsupported("block math")

    def inline_code(self, code: str) -> str:
        """
        write inline code. `code` is not escaped. the result is protected from
        escaping with `stash_code()`.
        """
        raise NotImplementedError

    def code_block(self, code: str, language: str = None, title: str = None, highlight_lines: str = None) -> str:
        """
        write a block of code. `code` is not escaped. `language` is the language from the info string
        of the code block, if any. `title` is the title, if any. `highlight_lines` is the lines to
        highlight, as written in the Markdown (for example `1 11 4-6`). the result is protected from
        escaping with `stash_code()`.
        """
        raise NotImplementedError

    def stash_code(self, string: str) -> tuple:
        """
        replace the code that `inline_code()` and `code_block()` wrote with tokens, so that the code is not
        changed by the next steps. the backend selects the form of the tokens.
        :return: the text with tokens, and a dict that maps each token to its code
        """
        raise NotImplementedError

    def clean(self, string: str) -> str:
        """
        clean the finished text: remove the unnecessary spaces and empty lines that the conversion left.
        the code is in the text already, unless `clean_before_restore` is true.
        """
        raise NotImplementedError
