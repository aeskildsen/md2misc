"""
Markdown cases for the tests of the schelp output.
"""

# Markdown that has no schelp form: the construct that the error names, and its line.
UNSUPPORTED = [
    ("# One\n\nText.\n\n# Two\n", "second level 1 heading", 5),
    ("# Heading with *italics*\n", "heading", 1),
    ("---\nsummary: A\n---\n\n## Section\n\n> Not an alert.\n", "block quote", 7),
    ("---\nsummary: A\nauthor: Me\n---\n", "front matter key `author`", 3),
    ("---\nsummary: [A, B]\n---\n", "front matter key `summary` with a list", 2),
    ("---\nsummary A\n---\n", "front matter line", 2),
    ("## Heading with *italics*\n", "heading", 1),
    ("Text.\n\n## Heading with `code`\n", "heading", 3),
    ("## Heading with $x$\n", "heading", 1),
    ("Text.\n\n> A block quote\n", "block quote", 3),
    ("> [!NOTE]\n> Fine.\n\n> Not fine.\n", "block quote", 4),
    ("Text with [a page](other.md).\n", "link that is not an http URL", 1),
    ("Text.\n\nSee [@doe1999].\n", "citation", 3),
    ("![An image](image.png)\n", "image", 1),
    ("![type:audio](sound.wav)\n", "audio file", 1),
    ("Above.\n\n---\n\nBelow.\n", "horizontal rule", 3),
    ("Text.\n\n```supercollider title=\"Example\"\nx = 1;\n```\n", "code block title", 3),
    ("```sc hl_lines=\"1\"\nx = 1;\n```\n", "highlighted lines", 1),
    ("Use **`code` in bold**.\n", "code inside bold or italic text", 1),
    ("A line<br>break.\n", "line break", 1),
    ("Text.\n\n```\n# Fine in code\n> Fine in code\n```\n\n> Not in code.\n", "block quote", 8),
    ("> [!FOO]\n> An alert that is not known.\n", "block quote", 1),
    ("> ```\n> x = 1;\n> ```\n", "block quote", 1),
    ("Text **see [a page](https://a.org)** here.\n", "link or footnote inside bold or italic text", 1),
    ("Text *with a note[^1]* here.\n\n[^1]: The note.\n", "link or footnote inside bold or italic text", 1),
    ("Text.\n\n## See [a page](https://a.org)\n", "link or footnote in a heading", 3),
    ("## A heading[^1]\n\n[^1]: The note.\n", "link or footnote in a heading", 1),
    ("# A title with [a link](sc:Classes/SinOsc)\n", "link or footnote in a heading", 1),
    ("See [the C# guide](https://example.com).\n", "`#` in the text of a link", 1),
    ("See [a part](https://example.com/a#b#c).\n", "link with more than one `#`", 1),
    ("See [a method](sc:Classes/SinOsc#a#b).\n", "link with more than one `#`", 1),
]

# The heading of the class methods section, for the cases of the section.
M = "## Class methods\n\n"

# Markdown that has no schelp form, which the converters take for text: only the check of the source stops at it.
SOURCE_ONLY = [
    ("* One\n* Two\n", "list with `*` or `+` marks", 1),
    ("Text.\n\n+ One\n", "list with `*` or `+` marks", 3),
    ("1) One\n2) Two\n", "numbered list with `)`", 1),
    ("Above.\n\n***\n\nBelow.\n", "horizontal rule", 3),
    ("Above.\n\n_ _ _\n\nBelow.\n", "horizontal rule", 3),
    ("A title\n=======\n\nText.\n", "heading underlined with `=` or `-`", 2),
    ("Text.\n\nA title\n-------\n", "heading underlined with `=` or `-`", 4),
    ("Text.\n\n| a | b |\n|---|---|\n| 1 | 2 |\n", "table", 3),
] + [(M + markdown, construct, line + 2) for markdown, construct, line in [
    # the class methods section (M is its heading): the markdown starts at line 3
    ("| a | b |\n|---|---|\n| x | y |\n", "table outside a method", 1),
    ("Intro.\n\n| a | b |\n|---|---|\n| x | y |\n", "table outside a method", 3),
    ("### *ar\n\nText.\n\n## Examples\n\n| a | b |\n|---|---|\n| x | y |\n", "table (only the argument table", 7),
    ("### *ar\n\n| a | b |\n|---|\n| x | y |\n", "delimiter row has another number of cells", 4),
    ("### *ar\n\n| a | b |\n|---|---|---|\n| x | y |\n", "delimiter row has another number of cells", 4),
    ("### *ar\n\n| a |\n|---|\n| x |\n", "argument table with one column", 3),
    ("### *ar\n\n| a | | b |\n|---|---|---|\n| x | 1 | y |\n", "column without a heading", 3),
    ("### *ar\n\n| a | b |\n|---|---|\n", "table without rows", 3),
    ("### *ar\n\n| a | b |\n|---|---|\n\nText.\n", "table without rows", 3),
    ("### *ar\n\n| a | b |\n|---|---|\n| x | y |\nMore text.\n", "line without `|` after a table", 6),
    ("### *ar\n\n| a | b |\n|---|---|\n| x | y | z |\n", "more cells than the header", 5),
    ("### *ar\n\n| a | b |\n|---|---|\n| x | y |\n| w | v | u |\n", "more cells than the header", 6),
    ("### *ar\n\n| a | b |\n|---|---|\n| two words | y |\n", "argument name `two words`", 5),
    ("### *ar\n\n| a | b |\n|---|---|\n| *ar | y |\n", "argument name `*ar`", 5),
    ("### *ar\n\n| a | b |\n|---|---|\n| 1x | y |\n", "argument name `1x`", 5),
    ("### *ar\n\n| a | b |\n|---|---|\n| **x** | y |\n", "argument name `**x**`", 5),
    ("### *ar\n\n| a | b |\n|---|---|\n| | y |\n", "argument name ``", 5),
    ("### *ar\n\n| a | b |\n|---|---|\n| `x | y |\n", "argument name", 5),
    ("### *ar\n\n| a | b |\n|---|---|\n| x | y |\n| `x` | z |\n", "argument `x` twice", 6),
    ("### *ar\n\n| a | b |\n|---|---|\n| x | |\n", "argument `x` without text", 5),
    ("### *ar\n\n| a | b |\n|---|---|\n| x |\n", "argument `x` without text", 5),
    ("### *ar\n\n| a | r | b |\n|---|---|---|\n| x | 1 |\n", "argument `x` without text", 5),
    ("### *ar\n\n| a | b |\n|---|---|\n| x | Code `a|b`. |\n", "`|` in code in a table", 5),
    ("### *ar\n\n| `a|b` | c |\n|---|---|\n| x | y |\n", "`|` in code in a table", 3),
    ("### *ar\n\n| a | b |\n|---|---|\n| x | y \\\\| z |\n", "`\\\\|` in a table row", 5),
    ("### *ar\n\n| a | b |\n|---|---|\n| x | y |\n\n| a | b |\n|---|---|\n| w | v |\n", "second table", 7),
    ("### *ar\n\nReturns: x.\n\n| a | b |\n|---|---|\n| w | v |\n", "table after `Returns:`", 5),
    ("### *ar\n\n| a | b |\n|---|---|\n| x | y |\n\nMore text.\n", "text after the argument table", 7),
    ("### *ar\n\n| a | b |\n|---|---|\n| x | y |\n- A list.\n", "text after the argument table", 6),
    ("### *ar\n\n| a | b |\n|---|---|\n| x | y |\n\n```\nx = 1;\n```\n", "text after the argument table", 7),
    ("### *ar\n\n| a | b |\n|---|---|\n| x | y |\n\n> [!NOTE]\n> A note.\n", "text after the argument table", 7),
    ("### *ar\n\nReturns: x.\n\nMore text.\n", "text after the `Returns:` paragraph", 5),
    ("### *ar\n\n| a | b |\n|---|---|\n| x | y |\n\nReturns: x.\n\nReturns: y.\n", "text after the `Returns:`", 9),
    ("### Arguments\n\nText.\n", "heading in the class methods section that is not a method", 1),
    ("### ar\n\nText.\n", "heading in the class methods section that is not a method", 1),
    ("### *ar *kr\n\nText.\n", "heading in the class methods section that is not a method", 1),
    ("### *ar\n\n#### Details\n\nText.\n", "heading in the class methods section that is not a method", 3),
]] + [
    ("See <https://example.com>.\n", "link in `<` and `>`", 1),
    ("Mail <me@example.com>.\n", "link in `<` and `>`", 1),
    ("Press <kbd>Ctrl</kbd>.\n", "HTML tag", 1),
    ("Text.\n\n<!-- A comment. -->\n", "HTML comment", 3),
    ("Text.[^1]\n\n[^1]: Line one\n  and line two.\n", "footnote with more than one line", 3),
    ("Text.[^1]\n\n[^1]: Paragraph one.\n\n    Paragraph two.\n", "footnote with more than one line", 3),
]

# Markdown that only the writers of the backend stop at, thus the error has no line.
WRITER_ONLY = [
    ("Text with **bold $x$ math**.\n", "math inside bold or italic text"),
    ("Text with **bold *italic* inside**.\n", "bold text and italic text inside each other"),
    ("Text with *italic **bold** inside*.\n", "bold text and italic text inside each other"),
]

# Problems with the document as a whole: Markdown, the `metadata` and `insertions` arguments, and the text that the
# error must hold.
DOCUMENT_ERRORS = [
    ("---\nsummary: A\n---\n\n## Section\n", None, None, "needs a title or a class"),
    ("## Section\n", {"colour": "red"}, None, "front matter key `colour`"),
    ("## Section\n", None, {"classmethods": "CLASSMETHODS::\n"}, "has no insertion point for: classmethods"),
    ("---\ntitle: A\nsummary: Bars || here\n---\n\n## Section\n", None, None, "`##` or `||` in the value of `summary`"),
    ("## Section\n", {"title": "A ## B"}, None, "`##` or `||` in the value of `title`"),
]

# Markdown that is fine, although it looks like an unsupported construct.
SUPPORTED = [
    "```\n# A comment in code\n> Not a quote\n---\n![x](y)\n```\n",
    "Inline code `<br>` and `[@key]` and `![x](y)`.\n",
    "---\ntitle: Front matter\n---\n\n## Section\n",
    "> [!WARNING]\n> A warning.\n",
    "A link to [a class](sc:Classes/SinOsc) and to [the web](https://example.com).\n",
    "# A title\n\nText.\n",
    "```\n<!-- md2misc: classmethods -->\n```\n",
    "#1 is not a heading, as there is no space after the `#`.\n",
    "It costs $5 and $10, and \\$x\\$ is not math.\n",
    "> [!NOTE]\n> Try this:\n> ```\n> x = 1;\n> ```\n> And then this.\n",
    "Text with a < b > c and C# and F#.\n",
    "A link to [Classes/SinOsc#*ar](sc:Classes/SinOsc#*ar), which has the address as its text.\n",
    "Text.[^1]\n\n[^1]: A note.\n[^2]: Another note.\n",
    "Text.\n\n= is a sign, after an empty line.\n",
    "A text with a | pipe, and a | b.\n",
    "Code with a pipe: `a | b`.\n",
    "```\n| a | b |\n|---|---|\n| 1 | 2 |\n```\n",
    "| a | b |\n\n|---|---|\n",
    "Returns: in a section that is not the class methods section.\n",
    "## Section\n\n### *ar\n\nA heading with a star, outside the class methods section.\n",
    "## Class methods\n\n### *ar\n\nText with a | pipe.\n\n| a | b |\n|---|---|\n| x | y |\n",
    "## Class methods\n\n### *ar\n\n| a | b |\n|---|---|\n| x | y |\n### *kr\n\nText.\n",
    "## Class methods\n\n### *ar\n\n| a | b |\n|---|---|\n| x | y |\n## Examples\n\nText.\n",
    "## Class methods\n\n### *ar\n\n| a | b |\n|---|---|\n| x | Code `a \\| b`. |\n",
    "## Class methods\n\n### *ar\n\n```\n| a | b |\n```\n\n| a | b |\n|---|---|\n| x | y |\n",
]

# Markdown, and the parts of the HTML page that SCDoc must make from the schelp output. The cases of SUPPORTED are
# rendered too, and must give no error.
RENDERS = [
    ("**Note:** text.\n", ["<strong>Note:</strong> text."]),
    ("*Note:* text.\n", ["<em>Note:</em> text."]),
    ("Use `foo:`: please.\n", ["<code>foo:</code>: please."]),
    ("A path `C:\\` here.\n", ["<code>C:\\</code> here."]),
    ("[Note:](https://example.com) text.\n", ['<a href="https://example.com">Note:</a> text.']),
    ("Math $a:$ here.\n", ["<span class='math'>a:</span> here."]),
    ("Text.[^1]\n\n[^1]: A note that ends with a colon:\n", ["A note that ends with a colon:</div>"]),
    ("**Two colons::** here.\n", ["<strong>Two colons::</strong> here."]),
    ("# A::B\n\nText.\n", ["<h1>A::B"]),
    ("> [!NOTE]\n> Try this:\n> ```\n> x = 1;\n> ```\n> And then this.\n",
     ["<textarea class='editor'>x = 1;</textarea>", "And then this."]),
    ("It costs $5 and $10, and \\$x\\$ is not math.\n", ["It costs $5 and $10, and $x$ is not math."]),
    ("#1 is text.\n", ["<p>#1 is text."]),
    ("Math $a::b$ in text.\n", ["<span class='math'>a::b</span>"]),
    ("Before.\n\n$$\nx\n::\ny\n$$\n\nAfter.\n", ["x\n::\ny"]),
    ("Use `a::b` and `x\\` here.\n", ["<code>a::b</code>", "<code>x\\</code> here."]),
    ("## Section: with a colon\n\nText.\n", ["<h2>Section: with a colon</h2>"]),
    ("Term:\n:   A definition that ends with a colon:\n\nAfter.\n", ["<dt>Term:<dd>A definition that ends with a colon:"]),
]
