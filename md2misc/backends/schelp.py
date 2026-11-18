import re
from itertools import chain

from .base import Backend
from .. import citations, syntax, tables
from ..errors_warnings import DocumentError, UnsupportedConstruct


class SchelpBackend(Backend):
    """
    SuperCollider help (schelp) output, the markup that SCDoc renders to HTML.

    `header()` writes the header tags (`TITLE::` and the like) of the document; the converters write the body.
    """

    name = "schelp"

    # the code is still a token when the text is cleaned
    clean_before_restore = True

    # languages of a code block that SCDoc can colour: SuperCollider
    supercollider_languages = ["sc", "scd", "sclang", "supercollider"]

    # the token that stands for a piece of code until the text is finished
    code_token = "\x01{}\x01"

    # the schelp tag of each kind of admonition (GitHub alerts, like `> [!NOTE]`)
    admonitions = {
        "NOTE": "note",
        "TIP": "note",
        "IMPORTANT": "note",
        "WARNING": "warning",
        "CAUTION": "warning",
    }

    supports_insertions = True

    # the Markdown forms of CommonMark and Pandoc: `#1` at the start of a line is text, `$5 and $10` is not math
    heading_regex = syntax.HEADING_STRICT
    inline_math_regex = syntax.INLINE_MATH_STRICT

    # a code block can be in an admonition (`> [!NOTE]`)
    strip_quote_marks_in_code = True

    # a tag in a text: a word with `::` after it. the escaped `::` of the text has a backslash before it
    tag_regex = r"\w::"

    # the sections that SCDoc tells apart from other sections, by the text of a level 2 heading
    special_sections = {"description": "DESCRIPTION", "examples": "EXAMPLES", "class methods": "CLASSMETHODS",
                        "instance methods": "INSTANCEMETHODS"}

    # the sections whose methods and argument tables the converters write as `METHOD::` and `ARGUMENT::`, and the
    # mark before the name of each method in a method heading. SCDoc uses the same marks in the anchors of methods
    methods_sections = {"class methods": "*", "instance methods": "-"}
    supports_methods = True

    # a heading that starts the discussion of a method, after its arguments and its return value
    discussion_heading_regex = r"^#{4}[ \t]+[Dd]iscussion[ \t]*$"

    @staticmethod
    def method_heading_regex(mark: str) -> str:
        """
        the form of a method heading in a methods section: `### *ar`, or `### *ar, *kr` for more names. `mark` is
        the mark of the section (`*` or `-`).
        """
        name = re.escape(mark) + r"[A-Za-z_]\w*"
        return r"^#{3}[ \t]+(" + name + r"([ \t]*,[ \t]*" + name + r")*)[ \t]*$"

    # the name of an argument in the first cell of an argument table: a name, or a name in code
    argument_name_regex = r"(`?)([A-Za-z_]\w*)\1"

    # a paragraph that starts with this text is the return value of a method
    returns_mark = "Returns:"

    # the keys of the front matter. the values of these keys are lists
    header_keys = ["class", "title", "summary", "related", "categories"]
    list_keys = ["related", "categories"]

    def __init__(self, insertions: dict = None, bibliography=None):
        self.bibliography = bibliography  # the path of the bibliography file for the citations, or None
        self.stash = {}
        self.insertions = dict(insertions or {})
        self.used_insertions = set()
        self.title_heading = None  # the text of the level 1 heading
        self.title_heading_line = None

    # ------------------------------------------------------ the header

    @classmethod
    def _header_value(cls, key: str, value, line: int = None):
        """
        check the value of a header key and give it its form: a list for `related` and `categories`,
        else a string.
        """
        if key not in cls.header_keys:
            raise UnsupportedConstruct(cls.name, f"front matter key `{key}` (the keys are {', '.join(cls.header_keys)})", line)
        if key in cls.list_keys:
            if isinstance(value, str):
                value = value.split(",")
            return [str(v).strip() for v in value if str(v).strip()]
        if not isinstance(value, str):
            raise UnsupportedConstruct(cls.name, f"front matter key `{key}` with a list as value", line)
        return value.strip()

    @staticmethod
    def _unquote(value: str) -> str:
        """
        the value without the quotation marks around it, if it has them.
        """
        value = value.strip()
        if len(value) > 1 and value[0] == value[-1] and value[0] in "\"'":
            return value[1:-1]
        return value

    def take_front_matter(self, markdown: str) -> tuple:
        """
        take the front matter from the start of the text. it is a block of `key: value` lines between two
        lines with `---`. a value of `related` and `categories` can be a list, written as `[a, b]`, as lines
        with `- item` below the key, or as a string with commas.
        :return: the values by key, and the text with empty lines in place of the front matter, so that
                 the line numbers stay as they were
        """
        lines = markdown.split("\n")
        if not lines or lines[0].strip() != "---":
            return {}, markdown
        end = next((i for i in range(1, len(lines)) if lines[i].strip() in ("---", "...")), None)
        if end is None:
            return {}, markdown

        values = {}
        i = 1
        while i < end:
            line = lines[i]
            i += 1
            if not line.strip():
                continue
            entry = re.match(r"([A-Za-z_][\w-]*):[ \t]*(.*)$", line)
            if not entry:
                raise UnsupportedConstruct(self.name, "front matter line that is not `key: value`", i)
            key, value = entry[1].lower(), entry[2].strip()
            line_number = i
            if value == "":
                items = []
                while i < end and re.match(r"[ \t]*-[ \t]+", lines[i]):
                    items.append(self._unquote(re.sub(r"^[ \t]*-[ \t]+", "", lines[i])))
                    i += 1
                value = items if items else ""
            elif value.startswith("[") and value.endswith("]"):
                value = [self._unquote(v) for v in value[1:-1].split(",")]
            if isinstance(value, str):
                value = self._unquote(value)
            values[key] = self._header_value(key, value, line_number)
        return values, "\n" * (end + 1) + "\n".join(lines[end + 1:])

    def header(self, values: dict) -> str:
        """
        write the header tags of the document, with an empty line after them. there is no header
        if there are no values and no level 1 heading.
        :param values: the values by key (see `take_front_matter()`); they can be strings and lists
        """
        values = {key: self._header_value(key, value) for key, value in values.items()}
        if self.title_heading and not values.get("title") and not values.get("class"):
            values["title"] = self.title_heading
        values = {key: value for key, value in values.items() if value}
        if not values:
            return ""
        if "title" not in values and "class" not in values:
            raise DocumentError("the header of a schelp document needs a title or a class: "
                                "use `title:` or `class:` in the front matter, a level 1 heading, or give the value")
        out = ""
        for key in self.header_keys:
            if key in values:
                value = ", ".join(values[key]) if key in self.list_keys else values[key]
                if "##" in value or "||" in value:
                    # SCDoc takes the characters as markup in a header line, and a backslash is shown as it is
                    self.unsupported(f"`##` or `||` in the value of `{key}`")
                out += key.upper() + "::" + value.replace("::", "\\::") + "\n"
        return out + "\n"

    def insertion(self, name: str) -> str:
        self.used_insertions.add(name)
        text = self.insertions.get(name)
        # the text of the caller is schelp already: it is put in the finished text as it is
        return self._stash(text.strip("\n")) if text and text.strip() else ""

    def check_insertions(self):
        """
        stop if the caller gave text for an insertion point that the document does not have.
        """
        unused = sorted(set(self.insertions) - self.used_insertions)
        if unused:
            raise DocumentError("the document has no insertion point for: " + ", ".join(unused)
                                + " (a line like `<!-- md2misc: " + unused[0] + " -->`)")

    # ------------------------------------------------------------ checks

    # the Markdown constructs that only `check_source()` finds
    list_item_regex = r"[ \t]*([-*+]|\d+[.)])[ \t]"
    alert_mark_regex = r">\s*\[!(\w+)\]\s*$"
    # a source in a citation: `@key`, with an optional locator after a comma. `-@key` is the form that does not
    # name the author in the text, which has no use in a footnote: the `-` is ignored
    citation_item_regex = r"\s*-?@([^\s,;@\]]+)(?:\s*,\s*([^;@]*?))?\s*"
    markup_in_quote_construct = ("code, math, a link, a footnote, a citation, or bold or italic text in a block "
                                 "quote (the quote is in italics)")
    footnote_definition_regex = r"\[\^\d+\]:"
    footnote_mark_regex = r"\[\^\d+\]"
    thematic_break_regex = r" {0,3}([-*_])([ \t]*\1){2,}[ \t]*$"
    setext_underline_regex = r" {0,3}(=+|-+)[ \t]*$"
    autolink_regex = r"<([A-Za-z][A-Za-z0-9+.-]{1,31}:[^\s<>]*|[^\s<>@]+@[^\s<>]+)>"
    html_tag_regex = r"</?[A-Za-z][A-Za-z0-9-]*(\s[^<>]*)?/?>"

    def _is_paragraph_line(self, line: str) -> bool:
        """
        whether the line can be a line of a paragraph: it is not empty and it does not start another construct.
        """
        return bool(line.strip()) and not (
            re.match(self.list_item_regex, line) or re.match(syntax.HEADING_STRICT, line)
            or line.lstrip().startswith((">", syntax.CODE_FENCE, "|"))
        )

    def _check_heading_source(self, text: str, line: int):
        # the name of a section is plain text
        if (self.code_token[0] in text or re.search(r"\*[^*\n]+\*", text)
                or re.search(syntax.INLINE_MATH_STRICT, text)):
            self.unsupported("bold, italic text, code or math in a heading", line)
        if (re.search(syntax.LINK, text) or re.search(self.footnote_mark_regex, text)
                or re.search(syntax.CITATION, text)):
            self.unsupported("link, footnote or citation in a heading", line)

    def _check_citation(self, citation: str, line: int = None):
        """
        check a citation: the text between `[` and `]`. a citation is one source or more, separated by `;`. each
        source is a key with `@` before it, and an optional locator after a comma: `@doe1999, p. 30`.
        """
        if not self.bibliography:
            self.unsupported("citation (give a bibliography to the conversion, or write the citation as text)",
                             line)
        for item in citation.split(";"):
            if not re.fullmatch(self.citation_item_regex, item):
                self.unsupported(f"citation `[{citation}]` (the forms are `[@key]`, `[@key, p. 30]` and "
                                 "`[@key; @other]`)", line)

    def _check_table(self, lines: list, number: int, in_methods: bool, in_method: bool) -> int:
        """
        check the table whose header row is `lines[number]`. in a methods section, a table is only possible as the
        argument table of a method: the first column is the argument name, the last column its text, and the
        columns between them add `heading: value` to the text. outside the methods sections, a table gives
        `table::`, with the header row in bold.
        :return: the index after the last row of the table
        """
        header_line = number + 1
        if in_methods and not in_method:
            self.unsupported("table outside a method (put a heading like `### *ar` before it)", header_line)
        end = tables.table_end(lines, number)
        for index in range(number, end):
            raw = lines[index]
            if "\\\\|" in raw:
                self.unsupported("`\\\\|` in a table row (Markdown renderers read it in different ways)", index + 1)
            for code in re.finditer(r"`[^`\n]*`", raw):
                if tables.has_pipe(code[0]):
                    self.unsupported("`|` in code in a table (write `\\|`)", index + 1)
        header = tables.split_row(lines[number])
        if len(tables.split_row(lines[number + 1])) != len(header):
            self.unsupported("table whose delimiter row has another number of cells than its header row",
                             header_line + 1)
        if end == number + 2:
            self.unsupported("table without rows", header_line)
        for index in range(number + 2, end):
            row = lines[index]
            if not tables.has_pipe(row):
                self.unsupported("line without `|` after a table (put an empty line before it)", index + 1)
            if len(tables.split_row(row)) > len(header):
                self.unsupported("table row with more cells than the header row", index + 1)
        if in_methods:
            self._check_argument_table(lines, number, end)
        else:
            for cell in header:
                # the header row is bold, and SCDoc's `strong::` cannot hold other tags
                if ("`" in cell or "*" in cell or re.search(syntax.INLINE_MATH_STRICT, cell)
                        or re.search(syntax.LINK, cell) or re.search(self.footnote_mark_regex, cell)
                        or re.search(syntax.CITATION, cell)):
                    self.unsupported("code, math, a link, a footnote, a citation, or bold or italic text in the "
                                     "header row of a table (the header row is bold)", header_line)
        return end

    def _check_argument_table(self, lines: list, number: int, end: int):
        """
        check the columns and the rows of the argument table from `lines[number]` (the header row) to
        `lines[end]`.
        """
        header_line = number + 1
        header = tables.split_row(lines[number])
        if len(header) < 2:
            self.unsupported("argument table with one column (the first column is the name, the last the text)",
                             header_line)
        if not all(header[1:-1]):
            self.unsupported("argument table column without a heading", header_line)
        names = set()
        for index in range(number + 2, end):
            cells = tables.split_row(lines[index])
            name = re.fullmatch(self.argument_name_regex, cells[0])
            if not name:
                self.unsupported(f"argument name `{cells[0]}` (a name, or a name in code)", index + 1)
            if name[2] in names:
                self.unsupported(f"argument `{name[2]}` twice in a table", index + 1)
            names.add(name[2])
            if len(cells) < len(header) or not cells[-1]:
                self.unsupported(f"argument `{name[2]}` without text", index + 1)

    def _check_image(self, image, text: str, previous: str, following: str, line: int):
        """
        check an image `![caption](path)`. SCDoc shows an image as a block, thus the image must be alone in its
        paragraph. the path is relative to the schelp file.
        """
        if text.strip() != image[0] or self._is_paragraph_line(previous) or self._is_paragraph_line(following):
            self.unsupported("image in a line of text (put the image alone in a paragraph)", line)
        problem = self.image_problem(image[1], image[2])
        if problem:
            self.unsupported(problem, line)

    @classmethod
    def image_problem(cls, caption: str, path: str):
        """
        the construct that SCDoc cannot write in an image with `caption` and `path`, or `None`. SCDoc splits the
        tag at each `#`: path, caption, link.
        """
        if not path.strip() or re.match(r"[A-Za-z][A-Za-z0-9+.-]*:|/", path):
            return "image that is not a relative path (put the image file next to the schelp file)"
        if "#" in path or "#" in caption:
            return "`#` in the caption or the path of an image"
        # SCDoc shows the caption as plain text
        if (cls.code_token[0] in caption or "`" in caption or "*" in caption
                or re.search(syntax.INLINE_MATH_STRICT, caption) or re.search(syntax.MATH_TOKEN_REGEX, caption)
                or re.search(r"\[[^\]]*\]", caption)):
            return "code, math, a link, a footnote, or bold or italic text in the caption of an image"
        return None

    def _check_quote_line(self, text: str, line: int):
        """
        check a line of a block quote that is not an alert. the quote is in italics, and SCDoc's `emphasis::` cannot
        hold other tags or blocks.
        """
        content = re.sub(r"^>[ \t]?", "", text)
        if content.lstrip().startswith(">"):
            self.unsupported("block quote in a block quote", line)
        if re.match(self.list_item_regex, content):
            self.unsupported("list in a block quote", line)
        if re.match(syntax.HEADING_STRICT, content):
            self.unsupported("heading in a block quote", line)
        if (self.code_token[0] in content or "*" in content or re.search(syntax.INLINE_MATH_STRICT, content)
                or re.search(syntax.LINK, content) or re.search(self.footnote_mark_regex, content)
                or re.search(syntax.CITATION, content)):
            self.unsupported(self.markup_in_quote_construct, line)

    indented_regex = r"( {4}|\t)\S"

    def footnote_paragraphs(self, lines: list, number: int) -> list:
        """
        the paragraphs of the footnote whose definition (`[^1]: text`) is `lines[number]`, as lists of line
        indexes. the lines of a paragraph follow each other; the lines of a later paragraph have an indent of
        4 spaces or a tab, and empty lines come before it.
        """
        paragraphs = [[number]]
        index = number + 1
        while index < len(lines):
            line = lines[index]
            if not line.strip():
                following = next((i for i in range(index + 1, len(lines)) if lines[i].strip()), None)
                if following is None or not re.match(self.indented_regex, lines[following]):
                    break
                paragraphs.append([following])
                index = following + 1
                continue
            if re.match(self.footnote_definition_regex, line) or not (
                    self._is_paragraph_line(line) or re.match(self.indented_regex, line)):
                break
            paragraphs[-1].append(index)
            index += 1
        return paragraphs

    def join_footnotes(self, string: str) -> str:
        """
        put each footnote definition on one line, with a paragraph mark between its paragraphs, because the
        converters take the first line of a footnote definition as its text. `footnote()` writes the paragraphs.
        """
        lines = string.split("\n")
        out = []
        number = 0
        while number < len(lines):
            if not re.match(self.footnote_definition_regex, lines[number]):
                out.append(lines[number])
                number += 1
                continue
            paragraphs = self.footnote_paragraphs(lines, number)
            out.append(self.footnote_paragraph_mark.join(" ".join(lines[i].strip() for i in paragraph)
                                                         for paragraph in paragraphs))
            number = paragraphs[-1][-1] + 1
        return "\n".join(out)

    def _check_method_part(self, lines: list, number: int, in_methods: bool, part):
        """
        check a line of a method in a methods section, after the method heading, and give the part of the
        method that the line is in. the parts of a method are its text, its argument table, its return value and
        its discussion, in this order. SCDoc puts all text after an argument into that argument, and all text after
        `returns::` into the return value: thus only a `Returns:` paragraph or a `#### Discussion` heading can
        follow the table, and only the heading can follow the `Returns:` paragraph. headings and tables are
        checked in `check_source()`.
        """
        line = lines[number]
        if (not in_methods or part in (None, "discussion") or not line.strip()
                or re.match(syntax.HEADING_STRICT, line) or tables.starts_table(lines, number)):
            return part
        paragraph_start = number == 0 or not lines[number - 1].strip()
        if paragraph_start and line.startswith(self.returns_mark) and part != "returns":
            return "returns"
        if part == "table":
            self.unsupported("text after the argument table of a method (only a `Returns:` paragraph or a "
                             "`#### Discussion` heading can follow it)", number + 1)
        if part == "returns" and paragraph_start:
            self.unsupported("text after the `Returns:` paragraph of a method (put a `#### Discussion` heading "
                             "before it)", number + 1)
        return part

    def check_source(self, markdown: str):
        r"""
        stop at the first Markdown construct that has no schelp form, and name its line.
        the converters stop at most of these constructs too, but they cannot tell the line. some constructs
        (tables, lists with `*`, HTML tags and the like) are text for the converters: only this check stops at them.
        code is not looked at. front matter has been taken from the text already.
        """
        lines = markdown.split("\n")
        level_1_headings = 0

        in_code = False
        previous_is_quote = False
        plain_quote = False  # whether the block quote of the last quote line is a quote, not an alert
        # a methods section: in a method, the parts after the text are the argument table, the return value and the
        # discussion. `method_part` is the last part: None (no method), "text", "table", "returns" or "discussion".
        # `methods_mark` is the mark of the method names of the section (`*` or `-`), or None
        methods_mark = None
        method_part = None
        table_end = 0  # the index after the last row of the last table
        delimiter_rows = set()
        for number, line in enumerate(lines):
            line_number = number + 1
            previous = lines[number - 1] if number else ""
            fences = line.count(syntax.CODE_FENCE)
            if number in delimiter_rows:
                continue
            in_methods = methods_mark is not None
            if not in_code and number >= table_end:
                method_part = self._check_method_part(lines, number, in_methods, method_part)
            if in_code:
                if fences % 2:
                    in_code = False
                    previous_is_quote = line.startswith(">")
                continue
            if fences % 2:
                in_code = True
                info = line.split(syntax.CODE_FENCE, 1)[1]
                if re.search(r'title="', info):
                    self.unsupported("code block title", line_number)
                if re.search(r'hl_lines="', info):
                    self.unsupported("highlighted lines in a code block", line_number)
                # a code block can be in an alert, not in a quote: the quote is in italics
                is_quote = line.startswith(">")
                if is_quote and (plain_quote or not previous_is_quote):
                    self.unsupported("code block in a block quote", line_number)
                previous_is_quote = is_quote
                continue

            # the converters take inline code out of the text first
            text = re.sub(syntax.INLINE_CODE, self.code_token.format(""), line)
            prose = re.sub(syntax.INLINE_MATH_STRICT, "", text)

            heading = re.match(syntax.HEADING_STRICT + r"(.*)", text)
            if heading:
                level = len(heading[2])
                if level == 1:
                    level_1_headings += 1
                    if level_1_headings > 1:
                        self.unsupported("second level 1 heading (the first one is the title of the document: use level 2 for sections)", line_number)
                if level == 2:
                    methods_mark = self.methods_sections.get(heading[3].strip().lower())
                    method_part = None
                if methods_mark and level == 3 and re.match(self.method_heading_regex(methods_mark), line):
                    method_part = "text"
                elif (methods_mark and method_part not in (None, "discussion")
                      and re.match(self.discussion_heading_regex, line)):
                    method_part = "discussion"
                elif methods_mark and level >= 3:
                    self.unsupported(f"heading in a methods section that is not a method or the discussion of a "
                                     f"method (a method heading is like `### {methods_mark}ar` or "
                                     f"`### {methods_mark}ar, {methods_mark}kr`; one `#### Discussion` heading "
                                     f"can follow it)", line_number)
                else:
                    self._check_heading_source(heading[3], line_number)
            if number >= table_end and tables.starts_table(lines, number):
                if method_part == "discussion":
                    self.unsupported("table in the discussion of a method", line_number)
                table_end = self._check_table(lines, number, in_methods, method_part is not None)
                delimiter_rows.add(number + 1)
                if method_part in ("table", "returns"):
                    self.unsupported("second table in a method, or a table after `Returns:`", line_number)
                if method_part is not None:
                    method_part = "table"
            if re.match(self.setext_underline_regex, text) and self._is_paragraph_line(previous):
                self.unsupported("heading underlined with `=` or `-` (use `#` before the heading)", line_number)
            if re.match(syntax.RULE, text) or re.match(self.thematic_break_regex, text):
                self.unsupported("horizontal rule", line_number)
            if re.match(r"[\s>]*[*+][ \t]+\S", text):
                self.unsupported("list with `*` or `+` marks (use `-`)", line_number)
            if re.match(r"[\s>]*\d+\)[ \t]+\S", text):
                self.unsupported("numbered list with `)` after the number (use `1.`)", line_number)
            if re.search(syntax.LINE_BREAK, text):
                self.unsupported("line break tag", line_number)
            if re.search(syntax.AUDIO, text):
                self.unsupported("audio file", line_number)
            for image in re.finditer(syntax.IMAGE, text):
                self._check_image(image, text, previous, lines[number + 1] if number + 1 < len(lines) else "",
                                  line_number)
            for citation in re.finditer(syntax.CITATION, text):
                self._check_citation(citation[1], line_number)
            if re.search(self.autolink_regex, prose):
                self.unsupported("link in `<` and `>` (write the URL alone, or use `[text](URL)`)", line_number)
            if "<!--" in prose and not re.match(syntax.INSERTION, prose):
                self.unsupported("HTML comment", line_number)
            if re.search(self.html_tag_regex, prose):
                self.unsupported("HTML tag", line_number)
            for link in re.finditer(syntax.LINK, text):
                target = link[2]
                if not target.startswith(("http", "sc:")):
                    self.unsupported(self.other_link_construct, line_number)
                problem = self.link_problem(target[3:] if target.startswith("sc:") else target, link[1])
                if problem:
                    self.unsupported(problem, line_number)
            for emphasis in chain(re.finditer(syntax.BOLD, text), re.finditer(syntax.ITALIC, text)):
                if self.code_token[0] in emphasis[1]:
                    self.unsupported("code inside bold or italic text", line_number)
                if (re.search(syntax.LINK, emphasis[1]) or re.search(self.footnote_mark_regex, emphasis[1])
                        or re.search(syntax.CITATION, emphasis[1])):
                    self.unsupported("link, footnote or citation inside bold or italic text", line_number)
            if re.match(self.footnote_definition_regex, text):
                # the lines after the definition line
                for index in chain.from_iterable(self.footnote_paragraphs(lines, number)):
                    content = lines[index].strip()
                    if index != number and not self._is_paragraph_line(content):
                        self.unsupported("list, code block or other block in a footnote", index + 1)

            is_quote = text.startswith(">")
            if is_quote and not previous_is_quote:
                if re.match(self.alert_mark_regex, text) and not self.admonition_tag(text):
                    self.unsupported("alert of a kind that is not known (the kinds are "
                                     + ", ".join(self.admonitions) + ")", line_number)
                plain_quote = not self.admonition_tag(text)
            if is_quote and plain_quote:
                self._check_quote_line(text, line_number)
            previous_is_quote = is_quote

    # ------------------------------------------------------- the writers

    other_link_construct = "link that is not an http URL or an sc: link"

    def escape(self, string: str) -> str:
        # `::` ends a tag, `##` and `||` mark list items and table cells. a backslash in front takes the
        # characters as text. a single backslash is text already.
        string = re.sub(r"::|##|\|\|", lambda m: "\\" + m[0], string)
        # `\$` is a dollar sign that does not start math
        return string.replace("\\$", "$")

    @staticmethod
    def _unescape(string: str) -> str:
        """
        the text without the backslashes that `escape()` added.
        """
        return re.sub(r"\\(::|##|\|\|)", r"\1", string)

    @staticmethod
    def _inline(tag: str, text: str) -> str:
        """
        write the inline form of a tag, `tag::text::`.
        """
        # SCDoc takes a `:` or a `\` at the end of the text as part of the end-tag: a space keeps them apart
        return tag + "::" + text + (" " if text.endswith((":", "\\")) else "") + "::"

    def heading(self, level: int, text: str) -> str:
        # the name of a section is plain text
        if self.code_token[0] in text or re.search(syntax.MATH_TOKEN_REGEX, text) or re.search(r"\*[^*\n]+\*", text):
            self.unsupported("bold, italic text, code or math in a heading")
        if re.search(self.tag_regex, text):
            self.unsupported("link, footnote or citation in a heading")
        if level == 1:
            # the title of the document: it goes in the header, which escapes it
            if self.title_heading is not None:
                self.unsupported("second level 1 heading (the first one is the title of the document: use level 2 for sections)")
            self.title_heading = self._unescape(text.strip())
            return ""
        special = self.special_sections.get(text.strip().lower()) if level == 2 else None
        if special:
            return "\n" + special + "::\n"
        tag = {2: "SECTION", 3: "SUBSECTION"}.get(level, "SUBSUBSECTION")
        return "\n" + tag + "::" + text + "\n"

    def _check_modal(self, text: str, where: str = "bold or italic text"):
        """
        stop if the text of a modal tag holds other tags, which SCDoc does not allow. `where` names the tag.
        """
        if self.code_token[0] in text:
            self.unsupported(f"code inside {where}")
        if re.search(syntax.MATH_TOKEN_REGEX, text):
            self.unsupported(f"math inside {where}")
        if re.search(r"\*[^*\n]+\*", text) or re.search(r"(strong|emphasis)::", text):
            if where == "bold or italic text":
                self.unsupported("bold text and italic text inside each other")
            self.unsupported(f"bold or italic text inside {where}")
        if re.search(self.tag_regex, text):
            self.unsupported(f"link, footnote or citation inside {where}")

    def bold(self, text: str) -> str:
        self._check_modal(text)
        return self._inline("strong", text)

    def italic(self, text: str) -> str:
        self._check_modal(text)
        return self._inline("emphasis", text)

    def inline_quote(self, text: str, nested: bool = False) -> str:
        mark = "'" if nested else '"'
        return mark + text + mark

    def admonition_tag(self, text: str):
        """
        the schelp tag for a block quote that starts with a GitHub alert mark (`> [!NOTE]`), or `None`.
        """
        mark = re.match(r">\s*\[!(\w+)\]\s*$", text.split("\n", 1)[0])
        return self.admonitions.get(mark[1].upper()) if mark else None

    # the character of the markers that the converters put in place of the `#` marks of a heading
    heading_marker = "\x00"

    # a line with `>` alone separates the paragraphs of a block quote
    block_quote_regex = r"^((>.*(\n|$))+)"

    def _unknown_alert(self, first_line: str):
        """
        stop at an alert mark of a kind that is not known.
        """
        if re.match(self.alert_mark_regex, first_line) and not self.admonition_tag(first_line):
            self.unsupported("alert of a kind that is not known (the kinds are " + ", ".join(self.admonitions) + ")")

    def block_quote(self, text: str) -> str:
        lines = text.rstrip("\n").split("\n")
        tag = self.admonition_tag(lines[0])
        if tag is None:
            self._unknown_alert(lines[0])
            return self._quote([re.sub(r"^>[ \t]?", "", line) for line in lines])
        body = "\n".join(re.sub(r"^>[ \t]?", "", line) for line in lines[1:])
        # the empty line before the end-tag keeps a list in the body from taking the end-tag as text
        return "\n" + tag + "::\n" + body + "\n\n::\n"

    def _quote(self, lines: list) -> str:
        """
        write a block quote that is not an alert. SCDoc has no tag for it: the paragraphs are in italics, with
        quotation marks at the start of the first paragraph and at the end of the last one.
        """
        paragraphs = [p.strip("\n") for p in re.split(r"\n[ \t]*\n", "\n".join(lines)) if p.strip()]
        for paragraph in paragraphs:
            if re.search(r"^\s*>", paragraph, re.M):
                self.unsupported("block quote in a block quote")
            if re.search(r"^\s*([-+*]|\d+[.)])[ \t]", paragraph, re.M):
                self.unsupported("list in a block quote")
            if self.heading_marker in paragraph:
                self.unsupported("heading in a block quote")
            # the code of a block has more than one line; inline code has one
            mark = re.escape(self.code_token[0])
            if any("\n" in self.stash[token] for token in re.findall(mark + r"\d+" + mark, paragraph)):
                self.unsupported("code block in a block quote")
            if (self.code_token[0] in paragraph or "*" in paragraph
                    or re.search(syntax.MATH_TOKEN_REGEX, paragraph) or re.search(self.tag_regex, paragraph)
                    or re.search(syntax.LINK, paragraph) or re.search(self.footnote_mark_regex, paragraph)):
                self.unsupported(self.markup_in_quote_construct)
        if not paragraphs:
            return ""
        paragraphs[0] = '"' + paragraphs[0]
        paragraphs[-1] += '"'
        return "\n" + "\n\n".join(self._inline("emphasis", p) for p in paragraphs) + "\n"

    @staticmethod
    def _items(items: list, tag: str) -> str:
        """
        write the `##` items of a list, with a nested list for each nesting level.
        """
        out = ""
        prev = 0  # previous indentation level
        for text, level in items:
            if level > prev:
                out += (tag + "::\n") * (level - prev)
            elif level < prev:
                out += "::\n" * (prev - level)
            out += "## " + text.strip() + "\n"
            prev = level
        out += "::\n" * prev  # close the remaining nested lists
        return out

    def unordered_list(self, items: list) -> str:
        return "\nLIST::\n" + self._items(items, "LIST") + "::"

    def ordered_list(self, items: list) -> str:
        return "\nNUMBEREDLIST::\n" + self._items(items, "NUMBEREDLIST") + "::"

    def definition_list(self, entries: list) -> str:
        out = "\nDEFINITIONLIST::\n"
        for term, definition in entries:
            out += "## " + term.strip() + "\n|| " + definition + "\n"
        return out + "::\n\n"

    supports_tables = True

    def table(self, header: list, rows: list) -> str:
        """
        write a table. `header` is the cells of the header row, `rows` the cells of each body row; the text is
        escaped. SCDoc has no header row: the header row is a first row in bold, and a header row with only empty
        cells gives no row.
        """
        lines = []
        if any(cell.strip() for cell in header):
            lines.append(" || ".join(self._inline("strong", cell) if cell.strip() else "" for cell in header))
        lines += [" || ".join(cells) for cells in rows]
        return "\ntable::\n" + "".join("## " + line.rstrip() + "\n" for line in lines) + "::\n"

    def link(self, url: str, text: str) -> str:
        return self._link(url, text)

    def internal_link(self, target: str, text: str):
        # `sc:Classes/SinOsc` is a link to a SuperCollider help page; `sc:Classes/SinOsc#*ar` goes to an anchor
        if not target.startswith("sc:") or len(target) == 3:
            self.unsupported(self.other_link_construct)
        return self._link(target[3:], text)

    @staticmethod
    def _has_label(target: str, text: str) -> bool:
        """
        whether a link gets a label. without a label, SCDoc takes the name of the page as the label.
        """
        page = target.split("#", 1)[0]
        return not (text == target or text == page.rsplit("/", 1)[-1])

    @classmethod
    def link_problem(cls, target: str, text: str):
        """
        the construct that SCDoc cannot write in a link to `target` with the text `text`, or `None`.
        SCDoc splits the link at each `#`: page, anchor, label.
        """
        if target.count("#") > 1:
            return "link with more than one `#` in its address"
        if "#" in text and cls._has_label(target, text):
            return "`#` in the text of a link"
        return None

    def _link(self, target: str, text: str) -> str:
        self._check_modal(text, "the text of a link")
        problem = self.link_problem(target, text)
        if problem:
            self.unsupported(problem)
        if not self._has_label(target, text):
            return self._inline("link", target)
        # the label follows an anchor (`page#anchor#label`) or an empty anchor (`page##label`)
        return self._inline("link", target + ("#" if "#" in target else "##") + text)

    def image(self, caption: str, path: str, width: str) -> str:
        if caption == "type:audio":
            # the converter finds an audio file as an image, as the audio syntax is the one of an image
            self.unsupported("audio file")
        problem = self.image_problem(caption, path)
        if problem:
            self.unsupported(problem)
        # the width of an image is not part of SCDoc
        return self._inline("image", path + ("#" + caption if caption.strip() else ""))

    # ------------------------------------------------------- citations

    # the citations are written before the footnotes, thus a citation in a footnote is known by its line
    citations_before_footnotes = True

    def write_citations(self, string: str) -> str:
        """
        replace each citation by its text. Pandoc writes the citations and the references (see `citations`).
        a citation in the text gives a footnote: its first citation gives the reference entry of a source, with
        the locator; a later citation gives the short form (`Doe 1999, 30.`). a citation in a footnote gives the
        short form in parentheses, as SCDoc cannot put a footnote in a footnote.
        """
        found = list(re.finditer(syntax.CITATION, string))
        if not found:
            return string
        for citation in found:
            self._check_citation(citation[1])
        string = self.join_footnotes(string)
        found = list(re.finditer(syntax.CITATION, string))

        # the citations for Pandoc: the whole citation in a footnote, else each source alone
        requests = []  # (index of the citation, key or None)
        sources = []
        for index, citation in enumerate(found):
            line_start = string.rfind("\n", 0, citation.start()) + 1
            items = [re.fullmatch(self.citation_item_regex, item) for item in citation[1].split(";")]
            if re.match(self.footnote_definition_regex, string[line_start:]):
                requests.append((index, None))
                sources.append("[" + "; ".join(self._pandoc_item(item) for item in items) + "]")
            else:
                for item in items:
                    requests.append((index, item))
                    sources.append("[" + self._pandoc_item(item) + "]")
        texts, entries = citations.process(sources, self.bibliography)
        missing = sorted({item[1] for _, item in requests if item} - set(entries))
        if missing:
            raise DocumentError("the bibliography has no entry for: " + ", ".join(missing))
        entries = self._entries(entries)

        parts = [[] for _ in found]  # the parts of each footnote, or the text of a citation in a footnote
        in_footnote = set()
        cited = set()
        for (index, item), text in zip(requests, texts):
            if item is None:
                in_footnote.add(index)
                parts[index].append(self._pandoc_text(text))
            elif item[1] not in cited:
                cited.add(item[1])
                parts[index].append(self._with_locator(entries[item[1]], item[2]))
            else:
                parts[index].append(re.sub(r"^\((.*)\)$", r"\1", self._pandoc_text(text)))

        out, position = [], 0
        for index, citation in enumerate(found):
            before = string[position:citation.start()]
            if index in in_footnote:
                text = parts[index][0]
            else:
                text = self._inline("footnote", "; ".join(part.rstrip(".") for part in parts[index]) + ".")
                before = self._separate_footnote(before)
            # the text is schelp already: no later step of the conversion changes it
            out += [before, self._stash(text)]
            position = citation.end()
        return "".join(out) + string[position:]

    @staticmethod
    def _pandoc_item(item) -> str:
        """
        a source of a citation in the form of Pandoc, without the `-` before the key.
        """
        return "@" + item[1] + (", " + item[2] if item[2] else "")

    @staticmethod
    def _with_locator(entry: str, locator: str) -> str:
        """
        the reference entry with the locator at its end: a page (`30` gives `p. 30`), pages (`30-35` gives
        `pp. 30–35`), or the locator as it is.
        """
        if not locator:
            return entry
        if re.fullmatch(r"\d+", locator):
            locator = "p. " + locator
        elif re.fullmatch(r"\d+\s*[-–]+\s*\d+", locator):
            locator = "pp. " + re.sub(r"\s*[-–]+\s*", "–", locator)
        return entry.rstrip(".") + ", " + locator + "."

    def _entries(self, entries: dict) -> dict:
        """
        the text of each reference entry. in a list of references, the style writes `———` in place of the
        authors of an entry that has the same authors as the entry before it; a footnote shows one entry, thus
        the authors are written again.
        """
        out = {}
        previous = ""
        for key, inlines in entries.items():
            text = self._pandoc_text(inlines)
            authors = re.match(r"(.+?)\.\s(?=\d{4}|n\.d\.)", previous)
            if text.startswith("———") and authors:
                text = authors[1] + text[len("———"):].lstrip("—")
            out[key] = previous = text
        return out

    def _pandoc_text(self, inlines: list, plain: bool = False) -> str:
        """
        write a list of Pandoc inline elements (the JSON form) as schelp. `plain` is true in a tag that cannot hold
        other tags: then the text is written without markup.
        """
        out = ""
        for inline in inlines:
            kind, content = inline["t"], inline.get("c")
            if kind == "Str":
                out += self.escape(content)
            elif kind in ("Space", "SoftBreak", "LineBreak"):
                out += " "
            elif kind in ("Emph", "Strong", "Underline"):
                text = self._pandoc_text(content, plain=True)
                out += text if plain else self._inline("strong" if kind == "Strong" else "emphasis", text)
            elif kind == "Link":
                text, url = self._pandoc_text(content[1], plain=True), content[2][0]
                out += text if plain or self.link_problem(url, text) else self._link(url, text)
            elif kind == "Code":
                out += self.escape(content[1]) if plain else self._inline("code", content[1].replace("::", "\\::"))
            elif kind == "Quoted":
                marks = "“”" if content[0]["t"] == "DoubleQuote" else "‘’"
                out += marks[0] + self._pandoc_text(content[1], plain) + marks[1]
            elif kind == "Cite":
                out += self._pandoc_text(content[1], plain)
            elif kind in ("Span", "SmallCaps", "Superscript", "Subscript", "Strikeout"):
                out += self._pandoc_text(content[-1], plain)
            elif kind in ("Math", "RawInline"):
                out += self.escape(content[1])
        return out

    # between the paragraphs of a footnote, until `footnote()` writes them
    footnote_paragraph_mark = "\x06"

    @staticmethod
    def _separate_footnote(before: str) -> str:
        """
        the text before a footnote tag. SCDoc does not find a tag directly after a letter, but it removes the
        space before a footnote mark: thus a space comes between a letter and the tag.
        """
        return before + " " if re.search(r"[^\W\d_]\Z", before) else before

    def footnote(self, text: str) -> str:
        # SCDoc shows the paragraphs of a footnote that are separated by an empty line
        return self._inline("footnote", re.sub(r"\s*" + self.footnote_paragraph_mark + r"\s*", "\n\n", text))

    def inline_math(self, expression: str) -> str:
        return self._inline("math", expression.replace("::", "\\::"))

    def display_math(self, expression: str) -> str:
        body = re.sub(r"^([ \t]*)::([ \t]*)$", r"\1\\::\2", expression.strip("\n"), flags=re.M)
        return "\nmath::\n" + body + "\n::\n"

    def _stash(self, text: str) -> str:
        token = self.code_token.format(len(self.stash))
        self.stash[token] = text
        return token

    def inline_code(self, code: str) -> str:
        # in the inline form of a tag, `::` in the text needs a backslash
        return self._stash(self._inline("code", code.replace("::", "\\::")))

    def code_block(self, code: str, language: str = None, title: str = None, highlight_lines: str = None) -> str:
        if title:
            self.unsupported("code block title")
        if highlight_lines:
            self.unsupported("highlighted lines in a code block")
        tag = "code" if language is None or language.lower() in self.supercollider_languages else "teletype"
        if not code.endswith("\n"):
            code += "\n"
        # in the block form of a tag, a line with `::` alone ends the block, thus it needs a backslash
        code = re.sub(r"^([ \t]*)::([ \t]*)$", r"\1\\::\2", code, flags=re.M)
        return self._stash(tag + "::\n" + code + "::")

    def stash_code(self, string: str) -> tuple:
        # `inline_code()` and `code_block()` stored the code and put tokens in the text already
        return string, self.stash

    # SCDoc reads letters directly before `::` as the name of a tag: `wordstrong::` is a tag `wordstrong`, which is
    # an error. a character that is not a letter keeps the word and the tag apart. the word joiner (U+2060) is not
    # visible and does not let a line break between them
    word_joiner = "\u2060"
    after_letter = r"(?<=[^\W\d_])"

    def clean(self, string: str) -> str:
        # SCDoc removes a space before a footnote mark: a footnote gets a space. the footnotes of citations have it
        # already (see `write_citations()`)
        string = re.sub(self.after_letter + r"footnote::", " footnote::", string)
        # the other inline tags get a word joiner. code and math are still tokens here
        string = re.sub(self.after_letter + r"(?=(strong|emphasis|link)::|" + syntax.MATH_TOKEN_REGEX + "|"
                        + re.escape(self.code_token[0]) + r"\d+" + re.escape(self.code_token[0]) + ")",
                        self.word_joiner, string)
        # paragraphs are separated by one empty line; the document ends with one line ending
        string = re.sub(r"\n{3,}", "\n\n", string).strip("\n")
        return string + "\n" if string else ""
