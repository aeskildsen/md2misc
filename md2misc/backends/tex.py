import re

from .base import Backend
from .minted import languages
from ..errors_warnings import Warnings
from ..helpers import get_matching_brackets


class TeXBackend(Backend):
    r"""
    TeX output.

    :param unnumbered: whether headings are unnumbered (`\section*{}`) or numbered (`\section{}`)
    :param document_class: `article` or `book`; sets which TeX command each heading level gets
    :param minted_language: the default language for minted code
    :param override_language: whether the language of every code block is replaced by `minted_language`
    """

    name = "TeX"

    # TeX commands for heading levels 1, 2, 3, ... of each document class.
    # levels below the end of the list are written as bold text.
    sectioning = {
        "article": ["section", "subsection", "subsubsection"],
        "book": ["chapter", "section", "subsection", "subsubsection"],
    }
    def __init__(self, unnumbered: bool = False, document_class: str = "article",
                 minted_language: str = "text", override_language: bool = False):
        self.unnumbered = unnumbered
        self.document_class = document_class
        self.minted_language = minted_language
        self.override_language = override_language
        if (minted_language not in languages) and (not override_language):
            Warnings("lang_not_supported", minted_language)

    @property
    def heading_groups(self) -> int:
        return len(self.sectioning[self.document_class if self.document_class in self.sectioning else "book"]) + 1

    def escape(self, string: str) -> str:
        string = string.replace(r"{", r"\{")
        string = string.replace(r"}", r"\}")
        # string = re.sub("(?<![^\]]\[)\^", r"\^", string, flags=re.M)
        string = re.sub(r"\\(?![\{\}])", r"\\textbackslash{}", string, flags=re.M)
        # string = string.replace(r">", r"\textgreater{}") # obstructs blockquotes
        string = string.replace(r"#", r"\#")
        string = string.replace("$", r"\$")
        string = string.replace("%", r"\%")
        string = string.replace(r"$", r"\&")
        #string = string.replace(r"~", r"\~") # leads to an error if ~ is used in an inline quote
        string = string.replace("_", r"\_")
        string = string.replace("&", r"\&")
        string = re.sub(r"\^", r"\\^", string, flags=re.M)
        return string

    def heading(self, level: int, text: str) -> str:
        commands = self.sectioning[self.document_class if self.document_class in self.sectioning else "book"]
        if level > len(commands):
            # headings below the lowest TeX sectioning level are bold paragraphs
            if self.unnumbered or self.document_class == "article":
                return "\n\n\\noindent{}\\textbf{" + text + "}\n\n"
            return "\n\n\\textbf{" + text + "}\n\n"
        if not self.unnumbered:
            return "\\" + commands[level - 1] + "{" + text + "}\n"
        if self.document_class == "article":
            # unnumbered article headings: levels 1 and 2 both give a \section*,
            # the table of contents entry follows the level
            command = ["section*", "section*", "subsection*"][level - 1]
            toc = ["section", "subsection", "subsubsection"][level - 1]
        else:
            command = commands[level - 1] + "*"
            toc = commands[level - 1]
        return "\\" + command + "{" + text + "}\n\\addcontentsline{toc}{" + toc + "}{" + text + "}\n"

    def bold(self, text: str) -> str:
        return "\\textbf{" + text + "}"

    def italic(self, text: str) -> str:
        return "\\textit{" + text + "}"

    def block_quote(self, text: str) -> str:
        return "\\begin{quotation}\n" + text + "\n\\end{quotation}\n\n"

    def remove_quote_marks(self, string: str) -> str:
        # md2tex replaces every `>` of the text, not only the marks of block quotes. this is kept
        # so that the output stays as it was: it is also why a `<br>` tag is never found
        return string.replace(">", " ")

    def inline_quote(self, text: str, nested: bool = False) -> str:
        return "\\enquote{" + text + "}"

    @staticmethod
    def _items(items: list, environment: str) -> str:
        """
        write the `\\item` lines of a list, with a nested `environment` for each nesting level.
        """
        out = ""
        prev = 0  # previous indentation level
        for text, level in items:
            # open/close the good number of envs
            if level - prev > 0:  # if there are envs to open; shouldn't be > 1 env to open, but just in case
                out += ("\\begin{" + environment + "} \n \\item ") * (level - prev)
                out += text + "\n"
            elif level - prev < 0:  # if there are envs to close
                out += ("\\end{" + environment + "}\n") * (prev - level)
                out += "\\item " + text + "\n"
            else:  # no envs to open/close
                out += "\\item " + text + "\n"
            prev = level
        out += ("\\end{" + environment + "}\n") * prev  # close the remaining nested envs
        return out

    def unordered_list(self, items: list) -> str:
        return "\n\\begin{itemize}\n" + self._items(items, "itemize") + "\n\\end{itemize}"

    def ordered_list(self, items: list) -> str:
        # the indentation of the environment is part of the output of md2tex
        return (
            "\n            \\begin{enumerate}\n            "
            + self._items(items, "enumerate")
            + "\n            \\end{enumerate}"
        )

    def definition_list(self, entries: list) -> str:
        out = "\\begin{description}\n"
        for term, definition in entries:
            out += "\\item[" + term + "] " + definition + "\n\n"
        return out + "\\end{description}\n\n"

    def horizontal_rule(self) -> str:
        return "\\par\\noindent\\rule{\\linewidth}{0.4pt}"

    def line_break(self) -> str:
        return "\n\n"

    def audio(self, path: str) -> str:
        # audio files are currently not well-supported in LaTeX -> pdf
        # so we turn it into a TeX comment for now
        return "%AUDIO_FILE:" + path

    def image(self, caption: str, path: str, width: str) -> str:
        env = r"""
\begin{figure}[H]
    \centering
    \includegraphics[width=.WIDTH\textwidth]{PATH}
    \caption{CAPTION}
\end{figure}"""
        for k, v in {"CAPTION": caption, "PATH": path, "WIDTH": width}.items():
            env = env.replace(k, v)
        return env

    def link(self, url: str, text: str) -> str:
        return "\\href{" + url + "}{" + text + "}"

    def footnote(self, text: str) -> str:
        return "\\footnote{" + text + "}"

    def citation(self, key: str, locator: str = None, is_range: bool = False, omit_author: bool = False) -> str:
        tex_locator = ""
        if locator:
            tex_locator = f"[pp. {locator}]" if is_range else f"[p. {locator}]"
        command = "\\parencite*" if omit_author else "\\parencite"
        return command + tex_locator + "{" + key + "}"

    def citations(self, keys: str) -> str:
        return "\\parencites{" + keys + "}"

    def inline_math(self, expression: str) -> str:
        return "\\(" + expression + "\\)"

    def display_math(self, expression: str) -> str:
        return "\\[" + expression + "\\]"

    def inline_code(self, code: str) -> str:
        return "\\mintinline{" + self.minted_language + "}{" + code + "}"

    def code_block(self, code: str, language: str = None, title: str = None, highlight_lines: str = None) -> str:
        env = r"""
\begin{listing}[H]
\begin{minted}{@@LANGTOKEN@@}
@@CODETOKEN@@
\end{minted}
@@CAPTIONTOKEN@@
\end{listing}"""  # env to add the code to; ugly indentation to avoid messing up the .tex file
        env = env.replace("@@CODETOKEN@@", code)

        if self.override_language:
            lang = self.minted_language
        elif language:
            # if the used language is supported by minted, create a minted inside
            # a listing environment to hold the code
            lang = language
            if lang not in languages:
                Warnings("lang_not_supported", lang)
                lang = "text"
        else:
            lang = "text"
        env = env.replace("@@LANGTOKEN@@", lang)

        # titles are converted to captions
        if title:
            env = env.replace("@@CAPTIONTOKEN@@", r'\caption{' + title + r'}')
        else:  # remove captiontoken line
            env = env.replace("@@CAPTIONTOKEN@@\n", "")

        if highlight_lines:
            lines = ", ".join(highlight_lines.split(" "))  # add commas to hl_lines
            env = env.replace(r"begin{minted}", r"begin{minted}[highlightlines={" + lines + r"}]")

        return env

    def stash_code(self, string: str) -> tuple:
        n = 0
        codedict = {}

        block_codematch = re.finditer(r"\\begin\{listing}(.|\n)*?\\end\{listing}", string, flags=re.M)
        for match in block_codematch:
            code = match[0]  # extract text
            string = string.replace(code, f"@@CODETOKEN{n}@@")
            codedict[f"@@CODETOKEN{n}@@"] = code
            n += 1

        # \mintinline envs are trickier to match, because we might match the
        # closing } too soon or too late since it may be part of the code
        # string. so we matches whole lines containing one ore more \mintinline
        # commands, then we split those lines by the `\mintline` token.
        # from there we use a helper function to extract the "outer" open/close
        # brackets pair in that string, starting from its beginning.
        for line in re.finditer(r"^.*\\mintinline.*$", string, re.M):
            segments = re.split(r"\\mintinline", line[0])
            if len(segments) > 1:
                for segment in segments[1:]:
                    mintinline_args = re.finditer(r"(\{.*?\})(\{.*\})", segment, flags=re.M)
                    for match in mintinline_args:
                        arg1 = match[1]
                        arg2 = get_matching_brackets(match[2])
                        mintinline_command = "\\mintinline" + arg1 + arg2
                        codedict[f"@@CODETOKEN{n}@@"] = mintinline_command
                        string = string.replace(mintinline_command, f"@@CODETOKEN{n}@@")
                        n += 1

        return string, codedict

    def clean(self, string: str) -> str:
        # string = re.sub(r"((?<!^ ) )+", " ", string, flags=re.M)  # replace multiple spaces with a single space, but not if they are at the beginning of a line
        # string = re.sub(r"{\s+", r"{", string, flags=re.M)  # remove whitespace after opening curly brace
        # string = re.sub(r"\s+}", r"}", string, flags=re.M)  # remove whitespace before closing curly brace
        string = re.sub(r"\n{2,}", r"\n\n", string, flags=re.M)  # reduce 2+ consecutive newlines to 2
        string = re.sub(r"(\\begin\{.*?)\n{2,}", r"\1\n", string, flags=re.M)  # replace multiple consecutive newlines after \begin with just one
        string = re.sub(r"\n{2,}( *\\end\{)", r"\n\1", string, flags=re.M) # replace multiple consecutive newlines before \end with just one
        return string
