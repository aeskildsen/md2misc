import re
from itertools import chain

from .base import Backend
from .. import syntax
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
    special_sections = {"description": "DESCRIPTION", "examples": "EXAMPLES"}

    # the keys of the front matter. the values of these keys are lists
    header_keys = ["class", "title", "summary", "related", "categories"]
    list_keys = ["related", "categories"]

    def __init__(self, insertions: dict = None):
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
    footnote_definition_regex = r"\[\^\d+\]:"
    footnote_mark_regex = r"\[\^\d+\]"
    thematic_break_regex = r" {0,3}([-*_])([ \t]*\1){2,}[ \t]*$"
    setext_underline_regex = r" {0,3}(=+|-+)[ \t]*$"
    table_delimiter_regex = r"[ \t]*\|?[ \t]*:?-+:?[ \t]*(\|[ \t]*:?-+:?[ \t]*)+\|?[ \t]*$|[ \t]*\|[ \t]*:?-+:?[ \t]*\|[ \t]*$"
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
        if re.search(syntax.LINK, text) or re.search(self.footnote_mark_regex, text):
            self.unsupported("link or footnote in a heading", line)

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
        for number, line in enumerate(lines):
            line_number = number + 1
            previous = lines[number - 1] if number else ""
            fences = line.count(syntax.CODE_FENCE)
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
                # a code block can be in an admonition, not at the start of a block quote
                is_quote = line.startswith(">")
                if is_quote and not previous_is_quote:
                    self.unsupported("block quote", line_number)
                previous_is_quote = is_quote
                continue

            # the converters take inline code out of the text first
            text = re.sub(syntax.INLINE_CODE, self.code_token.format(""), line)
            prose = re.sub(syntax.INLINE_MATH_STRICT, "", text)

            heading = re.match(syntax.HEADING_STRICT + r"(.*)", text)
            if heading:
                if len(heading[2]) == 1:
                    level_1_headings += 1
                    if level_1_headings > 1:
                        self.unsupported("second level 1 heading (the first one is the title of the document: use level 2 for sections)", line_number)
                self._check_heading_source(heading[3], line_number)
            if re.match(self.setext_underline_regex, text) and self._is_paragraph_line(previous):
                self.unsupported("heading underlined with `=` or `-` (use `#` before the heading)", line_number)
            if re.match(syntax.RULE, text) or re.match(self.thematic_break_regex, text):
                self.unsupported("horizontal rule", line_number)
            if re.match(r"[\s>]*[*+][ \t]+\S", text):
                self.unsupported("list with `*` or `+` marks (use `-`)", line_number)
            if re.match(r"[\s>]*\d+\)[ \t]+\S", text):
                self.unsupported("numbered list with `)` after the number (use `1.`)", line_number)
            if "|" in previous and re.match(self.table_delimiter_regex, text):
                self.unsupported("table", line_number - 1)
            if re.search(syntax.LINE_BREAK, text):
                self.unsupported("line break tag", line_number)
            if re.search(syntax.AUDIO, text):
                self.unsupported("audio file", line_number)
            if re.search(syntax.IMAGE, text):
                self.unsupported("image", line_number)
            if re.search(syntax.CITATION, text):
                self.unsupported("citation", line_number)
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
                if re.search(syntax.LINK, emphasis[1]) or re.search(self.footnote_mark_regex, emphasis[1]):
                    self.unsupported("link or footnote inside bold or italic text", line_number)
            if re.match(self.footnote_definition_regex, text):
                following = lines[number + 1] if number + 1 < len(lines) else ""
                after_empty = lines[number + 2] if number + 2 < len(lines) else ""
                # the converters take only the first line of a footnote
                if ((self._is_paragraph_line(following) and not re.match(self.footnote_definition_regex, following))
                        or (not following.strip() and re.match(r"( {4}|\t)\S", after_empty))):
                    self.unsupported("footnote with more than one line", line_number)

            is_quote = re.match(r">.+", text) is not None
            if is_quote and not previous_is_quote and not self.admonition_tag(text):
                self.unsupported("block quote", line_number)
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
            self.unsupported("link or footnote in a heading")
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
            self.unsupported(f"link or footnote inside {where}")

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

    def block_quote(self, text: str) -> str:
        lines = text.rstrip("\n").split("\n")
        tag = self.admonition_tag(lines[0])
        if tag is None:
            self.unsupported("block quote")
        body = "\n".join(re.sub(r"^>[ \t]?", "", line) for line in lines[1:])
        # the empty line before the end-tag keeps a list in the body from taking the end-tag as text
        return "\n" + tag + "::\n" + body + "\n\n::\n"

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

    def footnote(self, text: str) -> str:
        return self._inline("footnote", text)

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

    def clean(self, string: str) -> str:
        # paragraphs are separated by one empty line; the document ends with one line ending
        string = re.sub(r"\n{3,}", "\n\n", string).strip("\n")
        return string + "\n" if string else ""
