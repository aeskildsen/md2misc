import re
from itertools import chain

from . import syntax
from .helpers import process_list_indentation
from .errors_warnings import Warnings
from .backends import Backend

# ---------------------------------------------------------------
# regex based conversion from markdown to other formats;
# main scrips for the conversion process
# functions are part of classes for clarity
# ---------------------------------------------------------------


class MDSimple:
    """
    simple substitutions: bold, italics, audio files, horizontal rules, line breaks.
    the output is written by the backend.
    """
    bold_regex = syntax.BOLD
    italic_regex = syntax.ITALIC
    audio_regex = syntax.AUDIO
    rule_regex = syntax.RULE
    line_break_regex = syntax.LINE_BREAK

    @staticmethod
    def convert(string: str, backend: Backend):
        """
        perform the conversion: replace markdown syntax by the syntax of the output format
        :param string: the string rpr of the markdown file to convert
        :param backend: the output format
        :return: string with the conversion performed
        """
        string = re.sub(MDSimple.bold_regex, lambda m: backend.bold(m[1]), string, flags=re.M)
        string = re.sub(MDSimple.italic_regex, lambda m: backend.italic(m[1]), string, flags=re.M)
        string = re.sub(MDSimple.audio_regex, lambda m: backend.audio(m[1]), string, flags=re.M)
        string = re.sub(MDSimple.rule_regex, lambda m: backend.horizontal_rule(), string, flags=re.M)
        string = re.sub(MDSimple.line_break_regex, lambda m: backend.line_break(), string, flags=re.M)
        return string


class MDHeader:
    """
    header substitutions

    headers are found in two steps, because the headers must be located before the
    special characters of the text are escaped, and written after the other elements
    have been converted:
    - mark(): replace the `#` characters of each header by a marker that holds the header level
    - convert(): replace the marked headers by the output of the backend
    """
    marker = "\x00{}\x00"
    marker_regex = r"\x00(\d+)\x00"

    @staticmethod
    def mark(string: str, backend: Backend):
        """
        replace the `#` characters of each header by a marker that holds the header level.
        the text of the header is not changed.
        :param string: the markdown text, before escaping
        :param backend: the output format, which gives the form of a header
        :return: the text with marked headers
        """
        # a `>` is replaced by a space by the block quote step, thus a header can follow it
        return re.sub(
            backend.heading_regex,
            lambda m: m[1] + MDHeader.marker.format(len(m[2])),
            string, flags=re.M
        )

    @staticmethod
    def convert(string: str, backend: Backend):
        """
        perform the conversion: replace marked headers by the headers of the output format.
        markers that are not at the beginning of a line (for example in a list item) were not
        headers: they are turned back into `#` characters.
        :param string: the marked and escaped text
        :param backend: the output format
        :return: processed string
        """
        # one pass per header level, from the first level up. the last pass takes all
        # remaining levels. a later pass removes the blank lines that an earlier pass left
        for group in range(1, backend.heading_groups + 1):
            def write_heading(m):
                level = int(m[1])
                if level == group or (group == backend.heading_groups and level > group):
                    return backend.heading(level, m[2])
                return m[0]  # a header of another pass
            string = re.sub(
                r"^\s*" + MDHeader.marker_regex + r" *(.*?)$",
                write_heading, string, flags=re.M
            )
        string = re.sub(MDHeader.marker_regex, lambda m: backend.escape("#" * int(m[1])), string)
        return string


class MDQuote:
    r"""
    inline and block quote substitution

    contains
    --------
    block_quote(): replace multiline markdown quotes (">") into quotes of the output format
    inline_quote(): transform markdown quotes (`"`, `'`) into quotes of the output format
    """
    @staticmethod
    def block_quote(string: str, backend: Backend):
        r"""
        replace a markdown quote ">" with a quote of the output format.
        works in multiline mode.

        :param string:  the string representation of the markdown file
        :param backend: the output format
        :return: the updated string representation of a markdown file
        """
        string = re.sub(
            r"^((>.+(\n|$))+)",
            lambda m: backend.block_quote(m[1]),
            string, flags=re.M
        )
        return backend.remove_quote_marks(string)

    @staticmethod
    def inline_quote(string: str, backend: Backend):
        r"""
        convert quotation marks like "sandwich" to quotes of the output format
        :param string: the string representation of the markdown file
        :param backend: the output format
        :return: the updated string representation of a markdown file
        """
        quotes = re.finditer(r"\"(.*?)\"", string, re.M)
        for q in quotes:
            quote = q[1]
            quote = re.sub(r"(?<=\W)'\b(.*?)'(?=\W)", lambda m: backend.inline_quote(m[1], nested=True), quote)
            quote = backend.inline_quote(quote)
            string = string.replace(q[0], quote)

        return string


class MDList:
    """
    list substitution: replace markdown nested lists by nested lists of the output format

    contains
    --------
    unoredered_l(): create unordered lists from md unnumbered lists
    ordered_l(): create ordered lists from md numbered lists
    definition_l(): create definition lists from md definition lists
    """
    @staticmethod
    def unordered_l(string: str, backend: Backend):
        """
        translate a markdown unnumbered list into an unordered list of the output format
        :param string:  the string representation of the markdown file
        :param backend: the output format
        :return: the updated string representation of a markdown file
        """
        lists = re.finditer(r"((^[ \t]*?-(?!-{2,}).*?\n)+(.+\n)*)+", string, flags=re.MULTILINE)
        for ls in lists:
            # prepare list building
            lstext = ls[0]  # extract list text
            string = string.replace(lstext, "@@LISTTOKEN@@")  # add token to source
            lstext = re.sub(r"\n(?!\s*-)", " ", lstext, flags=re.M)  # group list item into one line

            lsitems = process_list_indentation(lstext)  # process the visual indentation

            string = string.replace("@@LISTTOKEN@@", backend.unordered_list(lsitems))

        return string

    @staticmethod
    def ordered_l(string: str, backend: Backend):
        """
        translate a markdown numbered list into an ordered list of the output format
        the functionning is quite the same as `unnumbered_list()`
        :param string: the string representation of the markdown file
        :param backend: the output format
        :return: the updated string representation of a markdown file
        """
        lists = re.finditer(r"((^[ \t]*?\d+\..*?\n?)+(.+\n?)*)+", string, flags=re.MULTILINE)
        for ls in lists:
            # prepare list building
            lstext = ls[0]  # extract list text
            string = string.replace(lstext, "@@LISTTOKEN@@")  # replace source list by token
            lstext = re.sub(r"\n(?!\s*\d+\.)", " ", lstext, flags=re.M)  # group list items into single line

            lsitems = process_list_indentation(lstext)  # process the visual indentation

            for li in lsitems:
                # remove numbering and whitespace
                li[0] = re.sub(r"^[ \t]*\d+\. *", "", li[0])

            string = string.replace("@@LISTTOKEN@@", backend.ordered_list(lsitems))

        return string
    
    @staticmethod
    def definition_l(string: str, backend: Backend):
        """
        translate a markdown definition list (https://python-markdown.github.io/extensions/definition_lists/)
        into a definition list of the output format.

        :param string:  the string representation of the markdown file
        :param backend: the output format
        :return: the updated string representation of a markdown file
        """

        # find all definition list items
        all_items = list(re.finditer(r"(^[^\n]+?)\n{1,3}: {3}(.+?^)(?=\S)", string, re.DOTALL | re.M))

        # group items located in immediate succession of one another into lists
        lists = []
        current_list = []
        for i, item in enumerate(all_items):
            if i == 0:
                current_list.append(item)
            elif all_items[i - 1].end() == item.start():
                current_list.append(item)
            else:
                lists.append(current_list)
                current_list = [item]

        if current_list:
            lists.append(current_list)
        
        for ls in lists:
            ls_block = ''.join([l[0] for l in ls])

            entries = []  # list of (term, definition)
            for item in ls:
                term = item.group(1)
                definition = item.group(2)
                definition = re.sub(r"^[:| ]{4}", "", definition, flags=re.M)
                definition = definition.strip()
                entries.append((term, definition))

            string = string.replace(ls_block, backend.definition_list(entries))

        return string


class MDCode:
    """
    block and inline code substitution

    contains
    --------
    block_code(): create a code block of the output format from a md block of code
    inline_code(): create inline code of the output format from inline md code
    """
    @staticmethod
    def inline_code(string: str, backend: Backend):
        """
        translate inline code in markdown-formatted text into inline code of the output format.

        :param string: the string representation of the markdown file
        :param backend: the output format
        :return: the updated string representation
        """
        
        matches = re.finditer(syntax.INLINE_CODE, string)
        for m in matches:
            code = m[0]
            string = string.replace(code, backend.inline_code(m[1]))
        
        return string

    @staticmethod
    def block_code(string: str, backend: Backend):
        """
        translate a markdown block of code into a code block of the output format.
        
        the function tries to match a md block code "```...```". if the
        block of code is matched, the code body is given to the backend.

        the function also tries to extract the following from the first line of the code block:
        - a code language specification, which is the first word of the info string.
        - a title, which the backend can write as a caption.
        - hl_lines, which the backend can write as highlighted lines.

        :param string: the string representation of the markdown file
        :param backend: the output format
        :return: the updated string representation of a markdown file
        """
        source = string
        matches = re.finditer(syntax.CODE_BLOCK, source, flags=re.M)
        for m in matches:
            code = m[0]  # isolate the block of code
            string = string.replace(code, "@@BLOCKCODETOKEN@@")  # to reinject code to string later

            # extract info string
            info_string = re.search(r"```([^\n]*)$", code, flags=re.M)[0].replace("```", "").strip()  # ugly but works

            # extract code body
            code_body = re.sub(r"```.*?\n((.|\n)+?)```", r"\1", code, flags=re.M)

            if backend.strip_quote_marks_in_code:
                # a code block in a block quote: each line of the code starts with the quote marks of the fence line
                prefix = source[source.rfind("\n", 0, m.start()) + 1:m.start()]
                if re.fullmatch(r"[ \t]*(>[ \t]*)+", prefix):
                    depth = prefix.count(">")
                    code_body = re.sub(r"^[ \t]*(?:>[ \t]?){1,%d}" % depth, "", code_body, flags=re.M)

            # assume language is the first word in the info string
            # cf. https://spec.commonmark.org/0.31.2/#fenced-code-blocks
            lang_info = re.search(r'^([0-9A-Za-z_-]+) *', info_string)
            language = lang_info[1] if lang_info else None

            # titles specified like title="A nice code block" in the info string
            title_info = re.search(r'title="([^"]+)"', info_string)
            title = title_info[1] if title_info else None

            # highlight lines specified like hl_lines="1 11 4-6" in the info string
            hl_lines_info = re.search(r'hl_lines="([^"]+)"', info_string)
            hl_lines = hl_lines_info[1] if hl_lines_info else None

            # reinject the code block of the output format to string
            string = string.replace("@@BLOCKCODETOKEN@@", backend.code_block(code_body, language, title, hl_lines))

        return string


class MDReference:
    r"""
    substitutions for references inside a markdown document.
    
    contains
    --------
    footnote(): replace markdown footnotes (`[\^\d+]`) into footnotes of the output format
    hyperlink(): replace markdown hyperlinks into hyperlinks of the output format
    citation(): replace pandoc-style references `[@doe1979]` into citations of the output format
    """
    @staticmethod
    def footnote(string: str, backend: Backend):
        r"""
        translate a markdown footnote `[^\d+]` to a footnote of the output format

        the structure of a markdown footnote:
        - This is the body of the text [^1] <-- body of the text
                                       ^^^^ <-- pointer to the footnote
        - [^1]: this is the footnote  <-- footnote
          ^^^^  <------------------------ pointer to the footnote mark
        in turn, what we need to do is remove the pointers, match the body of the
        footnote and add it to a `\footnote{}`

        :param string: the string representation of a markdown file
        :param backend: the output format
        """
        # the text has been escaped: the footnote marks have an escaped caret
        caret = re.escape(backend.escape("^"))
        fnote_pointers = re.finditer(r"\[" + caret + r"\d+\](?![ \t]*:)", string, flags=re.M)
        for match in fnote_pointers:
            try:
                pointer = match[0]  # extract the footnote pointer (the pointer to the actual footnote)
                fnote_num = re.search(r"\d+", pointer)[0]  # extract the footnote n°
                fnote_text = re.search(
                    r"^(\[" + caret + fnote_num + r"\]:) *(.+\n?)",
                    string, flags=re.M
                )  # match the proper footnote (with the good fnote_num)
                # remove the pointer + normalize space
                note = re.sub(r"\s+", " ", fnote_text[0].replace(fnote_text[1], "")).strip()

                if not re.search(r"^\s*$", note):  # if the note isn't empty; else, delete it
                    note = backend.footnote(note)
                    string = string.replace(fnote_text[0], "")  # delete the markdown footnote
                    string = string.replace(pointer, note)  # add the footnote to string
                else:
                    # delete the footnote body and pointers
                    string = string.replace(pointer, "")
                    string = string.replace(fnote_text[0], "")

            except TypeError:
                # a footnote pointer may point to nothing; conversely, a footnote
                # may to have a ref in the body. in that case, pass now and delete every loose
                # footnote part right after
                pass
        # delete all loose footnote strings
        string = re.sub(r"\[" + caret + r"\d+\](?![ \t]*:)", "", string, flags=re.M)
        string = re.sub(r"(\[" + caret + r"\d+\]:)(.+\n?)*", "", string, flags=re.M)

        return string
    
    @staticmethod
    def hyperlink(string: str, backend: Backend):
        r"""
        translate a markdown hyperlink to a hyperlink of the output format
        :param string: the string representation of a markdown file
        :param backend: the output format
        :return: the updated string representation
        """

        links = re.finditer(syntax.LINK, string)
        for link in links:
            if link[2].startswith("http"):
                # External URL
                string = string.replace(link[0], backend.link(link[2], link[1]))
            else: # We are dealing with some other link, likely to another internal document
                written = backend.internal_link(link[2], link[1])
                if written is not None:
                    string = string.replace(link[0], written)
                    continue
                # In LaTeX, we need a \label{} as a target when we link to somewhere else in our document.
                # This is not done automatically, since we don't know how link targets are organized.
                # Adding labels to sections is possible, but how would we programmatically know
                # which label to use so it corresponds to link targets?
                Warnings("link_type_not_supported", link[2])

        return string
    
    @staticmethod
    def citation(string: str, backend: Backend):
        r"""
        translate a markdown pandoc-style citation like `[@doe1999]` to
        citations of the output format. the TeX output is \parencite{doe1999},
        compatible with biblatex (not bibtex!)

        pandoc citation syntax spec: https://pandoc.org/chunkedhtml-demo/8.20-citation-syntax.html
        biblatex docs: https://ctan.org/pkg/biblatex
        
        Input syntax:
        - Citation form: [citationkey, locator]
        - Citation key: `@doe1999` (`-@doe1999` will omit author name with the \parencite* command)
        - Locator syntax: `p. 30`, `30`, `pp. 30-35`, `30-35` are the only valid forms
        
        Conversion examples:
        - [@doe1999] -> \parencite{doe1999}
        - [-@doe1999] -> \parencite*{doe1999}
        - [@doe1999, 30] -> \parencite[p. 30]{doe1999}
        - [@doe1999, p. 30] -> \parencite[p. 30]{doe1999}
        - [@doe1999, 30-35] -> \parencite[pp. 30-35]{doe1999}
        - [@doe1999, pp. 30-35] -> \parencite[pp. 30-35]{doe1999}
        - [@doe1999; @smith] -> \parencites{doe1999, smith}
        
        Limitations:
        - Prefix or suffix not supported currently
        - Multiple sources in same citation are only supported in the basic form `[@doe1999; @smith2000]`, i.e. without locator or pre-/suffix

        :param string: the string representation of a markdown file
        :param backend: the output format
        :return: the updated string representation
        """

        # Use negative lookahead so we don't match links or images
        ref_strings = re.finditer(syntax.CITATION, string, re.M)
        for ref_string in ref_strings:
            if ';' in ref_string[1]:
                # multiple references in one citation
                # -> simple mode
                keys = ref_string[1].replace(';', ',').replace('@', '')
                citation_text = backend.citations(keys)
            else:
                # only one citation, so we split into citation key and locator
                ref_components = re.match(r"(-?@[^, ]+)(, (?:p\. )?(\d+\b(?!-))|, (?:pp\. )?(\d+-\d+))?", ref_string[1])
                citation_key = ref_components[1]
                locator = ref_components[3] or ref_components[4]
                omit_author = citation_key.startswith('-')
                citation_text = backend.citation(
                    citation_key[2:] if omit_author else citation_key[1:],
                    locator,
                    is_range=not ref_components[3],
                    omit_author=omit_author
                )
        
            string = string.replace(ref_string[0], citation_text)

        return string


class MDCleaner:
    """
    clean the input markdown and output text.

    contains
    --------
    prepare_markdown(): prepare the markdown for the conversion and remove code substrings
                        from the rest of the pipeline
    clean_output(): clean the text created and reinsert code substrings at the end of the pipeline
    """
    @staticmethod
    def prepare_markdown(string: str, backend: Backend):
        """
        prepare markdown for the transformation:
        - strip empty lines (matching the expression `^[ \t]*\n`) by removing inline spaces.
          used at the beginning of the process, it will greatly simplify the following matches and replacement.
        - store the code of the output format in a dict, so that it is not changed by the other steps.
        - remove highlight marks.
        - the special characters of the output format must be escaped after this step, by the backend.
          this is also useful because of our use of `_` in `@@*TOKEN*@@` strings used for replacements.

        this function is used after `block_code()` and `inline_code()` to avoid replacing
        special characters that should be interpreted verbatim in code.

        :param string: the string representation of a markdown file
        :param backend: the output format
        :return: the updated string representation of a markdown file, and the dict of stored code
        """
        string = re.sub(r"^[ \t]*\n", r"\n\n", string, flags=re.M)
        string = string.replace("@@", "USERRESERVEDTOKEN")  # @@ is our special token, so we need to escape it
        #                                                     in case it is present in the user file

        # store all code so that its content isn't escaped.
        # the code is replaced in `string` with a special token
        string, codedict = backend.stash_code(string)

        string = string.replace("{==", "") # begin highlight (removed)
        string = string.replace("==}", "") # end highlight (removed)

        return string, codedict

    @staticmethod
    def clean_output(string: str, codedict: dict, backend: Backend):
        """
        clean spaces around commands + uneccessary spaces created during
        transformation
        :param string: the string representation of the markdown file
        :param codedict: the dictionnary containing escaped code blocks
        :param backend: the output format
        :return: the updated string representation of a markdown file
        """
        if backend.clean_before_restore:
            string = backend.clean(string)

        # rebuild the string by reinjecting the code blocks
        for k, v in codedict.items():
            string = string.replace(k, v)

        if not backend.clean_before_restore:
            string = backend.clean(string)

        string = string.replace("USERRESERVEDTOKEN", "@@")

        return string


class MDFrontmatter:
    """
    remove Markdown file frontmatter written in YAML format
    """
    
    @staticmethod
    def convert(string: str):
        """
        perform the conversion: delete markdown frontmatter
        :param string: the string rpr of the markdown file to convert
        :return: string with the conversion performed
        """
        
        flags = re.MULTILINE | re.DOTALL
        string = re.sub(r"^---.*---", "", string, flags=flags)

        return string


class MDMedia:
    """
    Convert embedded media (currently only images)
    """
    
    @staticmethod
    def image(string: str, backend: Backend):
        r"""
        Convert from markdown embedded image to an image of the output format
        Markdown syntax:
        - ![My alt text](/image/path.jpg)
        - ![My alt text](/image/path.jpg){ width=50% }

        Please note that the only sizing attribute currently supported is
        width, specified in percentage.

        :param string: the string rpr of the markdown file to convert
        :param backend: the output format
        :return: string with the conversion performed
        """
        default_width = "85" # percent

        # this regex looks a little weird, but we need to match the escaped chars introduced earlier...
        open_brace = re.escape(backend.escape("{"))
        close_brace = re.escape(backend.escape("}"))
        percent = re.escape(backend.escape("%"))
        images = re.finditer(
            syntax.IMAGE + r"(?:" + open_brace + r".*?width=\"(\d+)" + percent + r"\".*?" + close_brace + r")?",
            string, re.M
        )
        for match in images:
            width = match[3] if match[3] else default_width
            string = string.replace(match[0], backend.image(match[1], match[2], width))
        
        return string


class MDMath:
    """
    Handles conversion of markdown-embedded LaTeX math expressions.
    Converts markdown math delimiters to the math syntax of the output format.
    """

    @staticmethod
    def stash_math(string: str, backend: Backend):
        """
        Finds all math expressions, replaces them with tokens, and stores the math code.
        Converts markdown delimiters to the math delimiters of the output format.
        Returns the modified string and a dict mapping tokens to math code.
        """
        mathdict = {}
        n = 0

        # Block math: $$...$$ (multiline)
        def block_replacer(match):
            nonlocal n
            token = syntax.MATH_TOKEN.format(n)
            expr = match.group(1)
            mathdict[token] = backend.display_math(expr)
            n += 1
            return token

        string = re.sub(syntax.BLOCK_MATH, block_replacer, string, flags=re.DOTALL)

        # Inline math: $...$ (not preceded/followed by $)
        def inline_replacer(match):
            nonlocal n
            token = syntax.MATH_TOKEN.format(n)
            expr = match.group(1)
            mathdict[token] = backend.inline_math(expr)
            n += 1
            return token

        # the backend gives the form of inline math. block math is not matched
        string = re.sub(backend.inline_math_regex, inline_replacer, string, flags=re.DOTALL)

        return string, mathdict

    @staticmethod
    def restore_math(string: str, mathdict: dict):
        """
        Replaces tokens with the converted math expressions.
        """
        for token, math in mathdict.items():
            string = string.replace(token, math)
        return string


class MDInsertion:
    """
    insertion points: a line with an HTML comment, like `<!-- md2misc: classmethods -->`, marks a place
    where the caller of the conversion can put text. the comment is not shown by Markdown viewers.
    """
    placeholder = syntax.INSERTION

    @staticmethod
    def apply(string: str, backend: Backend):
        """
        replace each insertion point by what the caller gave for it, or by nothing.
        :param string: the markdown text
        :param backend: the output format
        :return: the updated text
        """
        if not backend.supports_insertions:
            return string
        return re.sub(MDInsertion.placeholder, lambda m: backend.insertion(m[1]), string, flags=re.M)
